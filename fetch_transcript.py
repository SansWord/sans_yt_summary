import sys
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in ("www.youtube.com", "youtube.com"):
        params = urllib.parse.parse_qs(parsed.query)
        video_ids = params.get("v", [])
        if video_ids:
            return video_ids[0]
    elif parsed.netloc == "youtu.be":
        video_id = parsed.path.removeprefix("/")
        if video_id:
            return video_id
    raise ValueError(f"Could not extract video ID from URL: {url!r}")


def fetch_transcript(video_id: str) -> list:
    api = YouTubeTranscriptApi()
    return api.fetch(video_id)


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
    pass


if __name__ == "__main__":
    main()
