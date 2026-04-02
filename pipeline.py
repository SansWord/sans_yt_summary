import sys
import argparse
from fetch_transcript import extract_video_id, fetch_transcript, save_transcript
from summarize import summarize, DEFAULT_MODEL, DEFAULT_PROMPT


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a YouTube transcript and summarize it with Claude."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--cookies", metavar="FILE", default=None, help="Netscape cookies.txt for sign-in required videos")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help=f"Prompt .md file (default: {DEFAULT_PROMPT})")
    args = parser.parse_args()

    cookies_path = args.cookies
    from_browser = args.cookies is None

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    print(f"Fetching transcript for video: {video_id}")
    try:
        segments, title = fetch_transcript(video_id, cookies_path=cookies_path, from_browser=from_browser)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        sys.exit(1)

    transcript_path = save_transcript(video_id, args.url, segments, title)
    print(f"Transcript saved to {transcript_path}")

    print(f"Summarizing with {args.model}...")
    try:
        summary_path = summarize(transcript_path, model=args.model, prompt_path=args.prompt)
        print(f"Summary saved to {summary_path}")
    except Exception as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
