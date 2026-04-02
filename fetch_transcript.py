import sys
import argparse
import http.cookiejar
import urllib.parse
from typing import Optional
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


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


def build_api(cookies_path: Optional[str]) -> YouTubeTranscriptApi:
    if cookies_path is None:
        return YouTubeTranscriptApi()
    jar = http.cookiejar.MozillaCookieJar(cookies_path)
    jar.load(ignore_discard=True, ignore_expires=True)
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(
        {c.name: c.value for c in jar}
    )
    return YouTubeTranscriptApi(http_client=session)


def fetch_transcript(video_id: str, cookies_path: Optional[str] = None) -> list:
    api = build_api(cookies_path)
    return api.fetch(video_id).to_raw_data()


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
    parser.add_argument(
        "--cookies",
        metavar="FILE",
        default=None,
        help="Path to a Netscape-format cookies.txt file for sign-in-required videos",
    )
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    try:
        segments = fetch_transcript(video_id, cookies_path=args.cookies)
    except FileNotFoundError:
        print(f"Cookies file not found: {args.cookies}")
        sys.exit(1)
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"Transcript not available for video: {video_id}")
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
