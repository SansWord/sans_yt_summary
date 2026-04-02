import sys
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


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
    if len(sys.argv) < 2:
        print("Usage: python fetch_transcript.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    try:
        segments = fetch_transcript(video_id)
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
