Spotify Playlist to YouTube Downloader
A Python tool to fetch Spotify playlist metadata and download audio from YouTube.
Fetches track details (name, artist, album, duration) from a Spotify playlist.
Downloads MP3 audio from YouTube for each track.
Saves metadata to a CSV file and audio to a folder.
Command-line interface with progress bar.

Prerequisite

Python 3.8+
FFmpeg (for audio conversion)
Spotify Developer account

Setup

Install FFmpeg:

Windows: Download ffmpeg-release-full.7z from gyan.dev. Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH.
macOS: brew install ffmpeg
Linux: sudo apt install ffmpeg
Verify: ffmpeg -version


Install Python libraries:
pip install -r requirements.txt


Set up Spotify API:

Go to Spotify Developer Dashboard.
Create an app, note Client ID and Client Secret.
Add http://127.0.0.1:8888/callback as a Redirect URI.
Set environment variables:export SPOTIPY_CLIENT_ID=your_client_id
export SPOTIPY_CLIENT_SECRET=your_client_secret

(Windows: use set instead of export)



Usage

Run the script:python spotify_downloader.py


Enter a Spotify playlist URL (e.g., https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M).
Authorize via browser on first run.
Output:
CSV: downloads/playlist_name.csv
Audio: downloads/playlist_name_audio/*.mp3



Options:

--output-dir: Change output folder (default: downloads).
--port: Change OAuth port if 8888 is in use (e.g., --port 8080).

Example
python spotify_downloader.py --playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M

spotipy
yt-dlp
click

