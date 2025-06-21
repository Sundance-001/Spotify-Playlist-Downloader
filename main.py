import os
import re
import csv
import time
import click
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
from urllib.parse import urlparse

# Initialize Spotify API client
def init_spotify():
    try:
        client_id = "f113c1af98a54131a20975f03c87123a"  # Replace with your Client ID
        client_secret = "733a73049b814c31a1ac172f64166e67"  # Replace with your Client Secret
        if "YOUR_CLIENT_ID" in client_id or "YOUR_CLIENT_SECRET" in client_secret:
            raise ValueError("Client ID or Client Secret not set. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET or update script.")
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="playlist-read-private"
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        click.echo(f"Error initializing Spotify API: {e}")
        exit(1)

# Extract playlist ID from URL
def get_playlist_id(playlist_input):
    if "open.spotify.com/playlist/" in playlist_input:
        parsed = urlparse(playlist_input)
        playlist_id = parsed.path.split("/")[-1].split("?")[0]
    else:
        playlist_id = playlist_input.strip()
    if not re.match(r"^[a-zA-Z0-9]{22}$", playlist_id):
        raise ValueError("Invalid playlist ID or URL.")
    return playlist_id

# Fetch playlist details and tracks
def fetch_playlist(sp, playlist_id):
    try:
        playlist = sp.playlist(playlist_id, fields="name,owner.display_name,tracks")
        playlist_name = playlist["name"]
        owner = playlist["owner"]["display_name"]
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        while results:
            tracks.extend(results["items"])
            results = sp.next(results)
        return playlist_name, owner, tracks
    except Exception as e:
        click.echo(f"Error fetching playlist: {e}")
        exit(1)

# Process tracks and extract metadata
def process_tracks(tracks):
    track_data = []
    for item in tracks:
        track = item["track"]
        if not track:
            continue
        artists = ", ".join(artist["name"] for artist in track["artists"])
        duration_ms = track["duration_ms"]
        duration_str = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
        track_info = {
            "name": track["name"],
            "artists": artists,
            "album": track["album"]["name"],
            "duration": duration_str,
            "youtube_url": "N/A"  # Will be updated after YouTube search
        }
        track_data.append(track_info)
    return track_data

# Download audio from YouTube
def download_from_youtube(search_query, output_dir, track_info):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "writeinfojson": False,
        "no_warnings": True,
        "extract_flat": True,  # For search results
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search YouTube for the track
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            if not search_results or not search_results.get("entries"):
                return False, "N/A"
            video_url = search_results["entries"][0]["url"]
            video_title = search_results["entries"][0]["title"]
            # Update options for actual download
            ydl_opts["outtmpl"] = os.path.join(output_dir, f"{track_info['name']}_{track_info['artists']}.%(ext)s".replace("/", "_").replace("\\", "_")[:100])
            ydl_opts["extract_flat"] = False
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True, video_url
    except Exception as e:
        click.echo(f"Error downloading {search_query}: {e}")
        return False, "N/A"

# Save track metadata to CSV
def save_to_csv(track_data, playlist_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{playlist_name}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "artists", "album", "duration", "youtube_url"])
        writer.writeheader()
        for track in track_data:
            writer.writerow(track)
    return csv_path

# Main CLI command
@click.command()
@click.option("--playlist", prompt="Enter Spotify playlist URL or ID", help="Spotify playlist URL or ID")
@click.option("--output-dir", default="downloads", help="Output directory for CSV and audio")
def download_playlist(playlist, output_dir):
    """Fetch Spotify playlist metadata and download audio from YouTube."""
    sp = init_spotify()
    try:
        playlist_id = get_playlist_id(playlist)
        click.echo(f"Fetching playlist: {playlist_id}")
        playlist_name, owner, tracks = fetch_playlist(sp, playlist_id)
        click.echo(f"Playlist: {playlist_name} by {owner} ({len(tracks)} tracks)")

        track_data = process_tracks(tracks)
        audio_dir = os.path.join(output_dir, f"{playlist_name}_audio")
        downloaded = 0
        skipped = 0

        with click.progressbar(track_data, label="Processing tracks") as bar:
            for track in bar:
                search_query = f"{track['name']} {track['artists']}"
                success, youtube_url = download_from_youtube(search_query, audio_dir, track)
                track["youtube_url"] = youtube_url
                if success:
                    downloaded += 1
                else:
                    skipped += 1
                time.sleep(2)  # Delay to avoid YouTube rate limits

        csv_path = save_to_csv(track_data, playlist_name, output_dir)
        click.echo(f"\nSaved metadata to: {csv_path}")
        click.echo(f"Downloaded {downloaded} tracks to: {audio_dir}")
        click.echo(f"Skipped {skipped} tracks (download failed)")
    except Exception as e:
        click.echo(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    download_playlist()