import sys
import urllib.parse


def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in ("www.youtube.com", "youtube.com"):
        params = urllib.parse.parse_qs(parsed.query)
        video_ids = params.get("v", [])
        if video_ids:
            return video_ids[0]
    elif parsed.netloc == "youtu.be":
        video_id = parsed.path.lstrip("/")
        if video_id:
            return video_id
    raise ValueError(f"Could not extract video ID from URL: {url!r}")


def fetch_transcript(video_id: str) -> list:
    pass


def format_segments(segments: list) -> str:
    pass


def main() -> None:
    pass


if __name__ == "__main__":
    main()
