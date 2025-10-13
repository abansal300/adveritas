import os, tempfile, subprocess, shutil, uuid, json
from typing import Optional, Dict
from .storage import upload_file

AUDIO_CT = "audio/mpeg"

def _run(cmd: list[str], capture_output=False) -> Optional[str]:
    if capture_output:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    subprocess.run(cmd, check=True)
    return None

def get_video_metadata(source_url: str) -> Dict:
    """Extract video metadata using yt-dlp without downloading."""
    try:
        output = _run(["yt-dlp", "--dump-json", "--no-download", source_url], capture_output=True)
        metadata = json.loads(output)
        return {
            "title": metadata.get("title"),
            "thumbnail_url": metadata.get("thumbnail"),
            "duration": metadata.get("duration"),
        }
    except Exception as e:
        print(f"Failed to extract metadata: {e}")
        return {}

def ytdlp_to_mp3(source_url: str) -> str:
    """Download audio using yt-dlp and convert to mp3 with ffmpeg. Returns local mp3 path."""
    tmpdir = tempfile.mkdtemp(prefix="ingest_")
    try:
        out = os.path.join(tmpdir, "input.%(ext)s")
        _run(["yt-dlp", "-f", "bestaudio/best", "-o", out, source_url])
        # find downloaded file
        files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.startswith("input.")]
        if not files:
            raise RuntimeError("yt-dlp did not produce a file")
        src = files[0]
        mp3 = os.path.join(tmpdir, "audio.mp3")
        _run(["ffmpeg", "-y", "-i", src, "-ac", "1", "-ar", "16000", mp3])
        return mp3
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise

def upload_audio_from_url(video_id: int, url: str) -> str:
    mp3 = ytdlp_to_mp3(url)
    key = f"media/{video_id}.mp3"
    upload_file(key, mp3, content_type=AUDIO_CT)
    return key

def save_upload_file(video_id: int, local_path: str) -> str:
    key = f"media/{video_id}.mp3"
    upload_file(key, local_path, content_type=AUDIO_CT)
    return key
