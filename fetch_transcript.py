import sys
import json
import argparse
import subprocess
import tempfile
import os
import urllib.parse
from typing import Optional


def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in ("www.youtube.com", "youtube.com"):
        params = urllib.parse.parse_qs(parsed.query)
        video_ids = params.get("v", [])
        if video_ids:
            return video_ids[0]
        # Handle /live/VIDEO_ID and /shorts/VIDEO_ID paths
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) == 2 and path_parts[0] in ("live", "shorts"):
            return path_parts[1]
    elif parsed.netloc == "youtu.be":
        video_id = parsed.path.removeprefix("/")
        if video_id:
            return video_id
    raise ValueError(f"Could not extract video ID from URL: {url!r}")


def _parse_json3(data: dict) -> list:
    segments = []
    for event in data.get("events", []):
        if "segs" not in event:
            continue
        text = "".join(s.get("utf8", "") for s in event["segs"]).strip()
        if not text:
            continue
        segments.append({
            "text": text,
            "start": event["tStartMs"] / 1000,
            "duration": event.get("dDurationMs", 0) / 1000,
        })
    return segments


def fetch_transcript(video_id: str, cookies_path: Optional[str] = None, from_chrome: bool = False) -> list:
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s")
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--skip-download",
            "--sub-lang", "en",
            "--sub-format", "json3",
            "--no-playlist",
            "--quiet",
            "-o", output_template,
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        if from_chrome:
            cmd[1:1] = ["--cookies-from-browser", "chrome"]
        elif cookies_path is not None:
            cmd[1:1] = ["--cookies", cookies_path]

        subprocess.run(cmd, capture_output=True, text=True)

        subtitle_file = os.path.join(tmpdir, f"{video_id}.en.json3")
        if not os.path.exists(subtitle_file):
            raise RuntimeError(f"No English transcript found for video: {video_id}")

        with open(subtitle_file) as f:
            data = json.load(f)

    return _parse_json3(data)


def format_segments(segments: list) -> str:
    lines = []
    for segment in segments:
        total_seconds = int(segment["start"])
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        timestamp = f"{minutes}:{seconds:02d}"
        lines.append(f"[{timestamp}] {segment['text']}")
    return "\n".join(lines) + "\n" if lines else ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a timed YouTube transcript and save it to a .txt file."
    )
    parser.add_argument("url", help="YouTube video URL")
    auth = parser.add_mutually_exclusive_group()
    auth.add_argument(
        "--cookies",
        metavar="FILE",
        default=None,
        help="Path to a Netscape-format cookies.txt file for sign-in-required videos",
    )
    auth.add_argument(
        "--from-chrome",
        action="store_true",
        default=False,
        help="Read YouTube cookies directly from Chrome (no file export needed)",
    )
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    try:
        segments = fetch_transcript(video_id, cookies_path=args.cookies, from_chrome=args.from_chrome)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        sys.exit(1)

    formatted = format_segments(segments)

    print(formatted, end="")

    output_path = f"{video_id}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted)
    print(f"\nTranscript saved to {output_path}")


if __name__ == "__main__":
    main()
