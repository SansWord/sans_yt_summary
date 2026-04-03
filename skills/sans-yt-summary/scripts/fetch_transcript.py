import glob
import re
import secrets
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


def _auth_flags(cookies_path: Optional[str], from_browser: bool) -> list:
    if from_browser:
        return ["--cookies-from-browser", "chrome"]
    if cookies_path is not None:
        return ["--cookies", cookies_path]
    return []


def _fetch_subtitles(video_id: str, lang: str, cookies_path: Optional[str], tmpdir: str, from_browser: bool = False) -> tuple:
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
        "--no-simulate",
        "--print", "%(title)s",
        "-o", output_template,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    cmd[1:1] = _auth_flags(cookies_path, from_browser)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"yt-dlp failed fetching subtitles for {video_id}")
    title = result.stdout.strip()
    matches = glob.glob(os.path.join(tmpdir, f"{video_id}.*.json3"))
    subtitle_file = matches[0] if matches else os.path.join(tmpdir, f"{video_id}.{lang}.json3")
    return title, subtitle_file


def _list_available_languages(video_id: str, cookies_path: Optional[str] = None, from_browser: bool = False) -> tuple:
    """Return (sorted list of available language codes, detected original language or None)."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        "--quiet",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    cmd[1:1] = _auth_flags(cookies_path, from_browser)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to fetch video info")
    if not result.stdout.strip():
        return [], None
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [], None
    langs = set(info.get("subtitles", {}).keys())
    original_lang = info.get("language")
    if original_lang and original_lang in info.get("automatic_captions", {}):
        langs.add(original_lang)
    return sorted(langs), original_lang


PERSISTENT_COOKIES_PATH = ".youtube_cookies.txt"

_COOKIE_ERROR_PATTERNS = [
    "sign in",
    "confirm you're not a bot",
    "bot detection",
    "http error 401",
    "http error 403",
]


def _is_cookie_error(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in _COOKIE_ERROR_PATTERNS)


def _refresh_cookies() -> str:
    print(
        "\nYouTube cookies have expired. Re-fetching from Chrome — "
        "you will see a macOS system password prompt."
    )
    if os.path.exists(PERSISTENT_COOKIES_PATH):
        os.remove(PERSISTENT_COOKIES_PATH)
    export_cookies(PERSISTENT_COOKIES_PATH)
    return PERSISTENT_COOKIES_PATH


def fetch_transcript(video_id: str, cookies_path: Optional[str] = None, lang: Optional[str] = None, from_browser: bool = False) -> tuple:
    # Export browser cookies to a persistent file on first use, reuse on subsequent runs.
    # Each --cookies-from-browser chrome call costs 2 macOS Keychain prompts; caching avoids this.
    if from_browser:
        if not os.path.exists(PERSISTENT_COOKIES_PATH):
            export_cookies(PERSISTENT_COOKIES_PATH)
        cookies_path = PERSISTENT_COOKIES_PATH
        from_browser = False

    if lang is None:
        langs, _ = _list_available_languages(video_id, cookies_path, from_browser)
        if not langs:
            raise RuntimeError(f"No transcripts found for video: {video_id}")

        print("Available languages:")
        for i, l in enumerate(langs, 1):
            print(f"  {i}. {l}")

        while True:
            choice = input("Select a language (number or code): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(langs):
                lang = langs[int(choice) - 1]
                break
            if choice in langs:
                lang = choice
                break
            print(f"Enter a number 1-{len(langs)} or a language code.")

    with tempfile.TemporaryDirectory() as tmpdir:
        title, subtitle_file = _fetch_subtitles(video_id, lang, cookies_path, tmpdir, from_browser)
        if not os.path.exists(subtitle_file):
            raise RuntimeError(f"Could not fetch transcript in language '{lang}' for video: {video_id}")

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
    sentinel = secrets.token_hex(4)  # e.g. 'a3f9c72b'
    closing_tag = f"</transcript_{sentinel}>"
    formatted = format_segments(segments)
    escaped = formatted.replace(closing_tag, closing_tag.replace("<", "&lt;"))
    output_path = f"{video_id}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {title}\nurl: {url}\nsentinel: {sentinel}\n---\n\n")
        f.write(f"<transcript_{sentinel}>\n")
        f.write(escaped)
        f.write(f"</transcript_{sentinel}>\n")
    return output_path


def export_cookies(output_path: str) -> None:
    subprocess.run(
        [
            "yt-dlp",
            "--cookies-from-browser", "chrome",
            "--cookies", output_path,
            "--skip-download",
            "--no-playlist",
            "--quiet",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ],
        capture_output=True,
        text=True,
    )
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("Failed to export cookies from Chrome")

    # Strip cookies unrelated to YouTube/Google to reduce file size.
    _YOUTUBE_DOMAINS = re.compile(r"\.(youtube\.com|google\.com|googlevideo\.com)$")
    with open(output_path) as f:
        lines = f.readlines()
    filtered = [
        line for line in lines
        if line.startswith("#") or _YOUTUBE_DOMAINS.search(line.split("\t")[0])
    ]
    with open(output_path, "w") as f:
        f.writelines(filtered)


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
    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="List available transcript languages and exit",
    )
    parser.add_argument(
        "--lang",
        metavar="CODE",
        default=None,
        help="Language code to fetch (skips interactive prompt)",
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

    cookies_path = args.cookies
    from_browser = args.cookies is None

    if from_browser:
        if not os.path.exists(PERSISTENT_COOKIES_PATH):
            export_cookies(PERSISTENT_COOKIES_PATH)
        cookies_path = PERSISTENT_COOKIES_PATH
        from_browser = False

    if args.list_langs:
        try:
            langs, detected = _list_available_languages(video_id, cookies_path, from_browser)
        except RuntimeError as e:
            if _is_cookie_error(str(e)):
                cookies_path = _refresh_cookies()
                try:
                    langs, detected = _list_available_languages(video_id, cookies_path)
                except RuntimeError as e2:
                    print(str(e2))
                    sys.exit(1)
            else:
                print(str(e))
                sys.exit(1)
        if not langs:
            print("No transcripts found.")
            sys.exit(1)
        if detected:
            print(f"detected:{detected}")
        for lang in langs:
            print(lang)
        return

    try:
        segments, title = fetch_transcript(video_id, cookies_path=cookies_path, lang=args.lang, from_browser=from_browser)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except RuntimeError as e:
        if _is_cookie_error(str(e)):
            cookies_path = _refresh_cookies()
            try:
                segments, title = fetch_transcript(video_id, cookies_path=cookies_path, lang=args.lang)
            except RuntimeError as e2:
                print(str(e2))
                sys.exit(1)
        else:
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
