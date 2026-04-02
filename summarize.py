import re
import sys
import argparse
from typing import Optional
from anthropic import Anthropic, RateLimitError, AuthenticationError

DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_PROMPT = "prompts/summarize.md"


def parse_transcript_file(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---\n"):
        raise ValueError(f"Transcript file {path!r} is missing metadata header")
    end = content.index("\n---\n", 4)
    header = content[4:end]
    body = content[end + 5:].strip()
    metadata = {}
    for line in header.splitlines():
        key, _, value = line.partition(": ")
        metadata[key.strip()] = value.strip()
    if "title" not in metadata or "url" not in metadata:
        raise ValueError(f"Transcript file {path!r} is missing title or url in header")
    return {"title": metadata["title"], "url": metadata["url"], "transcript": body}


def load_prompt(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_prompt(template: str, url: str, transcript: str) -> str:
    if "{{transcript}}" not in template:
        print("Warning: {{transcript}} placeholder not found in prompt, appending transcript at end.")
        return template.replace("{{url}}", url) + "\n\n" + transcript
    return template.replace("{{url}}", url).replace("{{transcript}}", transcript)


def sanitize_filename(title: str) -> str:
    sanitized = re.sub(r"[^\w\s-]", "", title.strip(), flags=re.ASCII)
    sanitized = re.sub(r"\s+", "_", sanitized)
    return sanitized


def call_claude(prompt: str, model: str) -> tuple:
    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text, response.usage


def summarize(transcript_path: str, model: str = DEFAULT_MODEL, prompt_path: str = DEFAULT_PROMPT) -> str:
    parsed = parse_transcript_file(transcript_path)
    template = load_prompt(prompt_path)
    prompt = build_prompt(template, parsed["url"], parsed["transcript"])

    text, usage = call_claude(prompt, model)

    print("Summary complete.")
    print(f"Input: {usage.input_tokens:,} tokens | Output: {usage.output_tokens:,} tokens | Total: {usage.input_tokens + usage.output_tokens:,} tokens")

    output_filename = sanitize_filename(parsed["title"]) + "_summary.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(text)

    return output_filename


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize a YouTube transcript using Claude."
    )
    parser.add_argument("transcript", help="Path to transcript .txt file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help=f"Prompt .md file (default: {DEFAULT_PROMPT})")
    args = parser.parse_args()

    try:
        output_path = summarize(args.transcript, model=args.model, prompt_path=args.prompt)
        print(f"Summary saved to {output_path}")
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    except RateLimitError:
        print("API rate limit reached, please try again later.")
        sys.exit(1)
    except AuthenticationError:
        print("Invalid or missing ANTHROPIC_API_KEY.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
