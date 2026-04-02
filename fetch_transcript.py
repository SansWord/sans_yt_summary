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


def _fetch_subtitles(video_id: str, lang: str, cookies_path: Optional[str], tmpdir: str) -> tuple:
    """Run yt-dlp to download subtitles for a given language. Returns (title, subtitle_path)."""
    output_template = os.path.join(tmpdir, "%(id)s")
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--write-subs",
        "--skip-download",
        "--sub-lang", lang,
        "--sub-format", "json3",
        "--no-playlist",
        "--quiet",
        "--print", "%(title)s",
        "-o", output_template,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    if cookies_path is not None:
        cmd[1:1] = ["--cookies", cookies_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    title = result.stdout.strip()
    subtitle_file = os.path.join(tmpdir, f"{video_id}.{lang}.json3")
    return title, subtitle_file


def _list_available_languages(video_id: str, cookies_path: Optional[str] = None) -> list:
    """Return sorted list of available subtitle/caption language codes via yt-dlp --dump-json."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        "--quiet",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    if cookies_path is not None:
        cmd[1:1] = ["--cookies", cookies_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to fetch video info")
    if not result.stdout.strip():
        return []
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    langs = set()
    for key in ("subtitles", "automatic_captions"):
        langs.update(info.get(key, {}).keys())
    return sorted(langs)


def fetch_transcript(video_id: str, cookies_path: Optional[str] = None) -> tuple:
    langs = _list_available_languages(video_id, cookies_path)
    if not langs:
        raise RuntimeError(f"No transcripts found for video: {video_id}")

    print("Available languages:")
    for i, lang in enumerate(langs, 1):
        print(f"  {i}. {lang}")

    while True:
        choice = input("Select a language (number or code): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(langs):
            selected = langs[int(choice) - 1]
            break
        if choice in langs:
            selected = choice
            break
        print(f"Enter a number 1-{len(langs)} or a language code.")

    with tempfile.TemporaryDirectory() as tmpdir:
        title, subtitle_file = _fetch_subtitles(video_id, selected, cookies_path, tmpdir)
        if not os.path.exists(subtitle_file):
            raise RuntimeError(f"Could not fetch transcript in language '{selected}' for video: {video_id}")

        with open(subtitle_file) as f:
            data = json.load(f)

    return _parse_json3(data), title


def format_segments(segments: list) -> str:
    lines = []
    for segment in segments:
        total_seconds = int(segment["start"])
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        timestamp = f"{minutes}:{seconds:02d}"
        lines.append(f"[{timestamp}] {segment['text']}")
    return "\n".join(lines) + "\n" if lines else ""


def save_transcript(video_id: str, url: str, segments: list, title: str) -> str:
    formatted = format_segments(segments)
    output_path = f"{video_id}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {title}\nurl: {url}\n---\n\n")
        f.write(formatted)
    return output_path


def export_cookies(output_path: str) -> None:
    result = subprocess.run(
        [
            "yt-dlp",
            "--cookies-from-browser", "chrome",
            "--cookies", output_path,
            "--skip-download",
            "--quiet",
            "https://www.youtube.com",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to export cookies from Chrome")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a timed YouTube transcript and save it to a .txt file."
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument(
        "--cookies",
        metavar="FILE",
        default=None,
        help="Path to a Netscape-format cookies.txt file for sign-in-required videos",
    )
    parser.add_argument(
        "--export-cookies",
        metavar="FILE",
        default=None,
        help="Export YouTube cookies from Chrome to FILE and exit",
    )
    args = parser.parse_args()

    if args.export_cookies:
        try:
            export_cookies(args.export_cookies)
            print(f"Cookies exported to {args.export_cookies}")
        except RuntimeError as e:
            print(str(e))
            sys.exit(1)
        return

    if not args.url:
        parser.error("url is required when not using --export-cookies")

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    try:
        segments, title = fetch_transcript(video_id, cookies_path=args.cookies)
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

    output_path = save_transcript(video_id, args.url, segments, title)
    print(f"\nTranscript saved to {output_path}")


if __name__ == "__main__":
    main()
