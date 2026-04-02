import re
import sys
import argparse
from typing import Optional

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
    pass


def summarize(transcript_path: str, model: str = DEFAULT_MODEL, prompt_path: str = DEFAULT_PROMPT) -> str:
    pass


def main() -> None:
    pass


if __name__ == "__main__":
    main()
