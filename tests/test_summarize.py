import pytest
import json
from unittest.mock import patch, MagicMock
from summarize import (
    parse_transcript_file,
    load_prompt,
    build_prompt,
    sanitize_filename,
)


# ── parse_transcript_file ─────────────────────────────────────────────────────

def test_parse_transcript_file_success(tmp_path):
    f = tmp_path / "abc123.txt"
    f.write_text(
        "---\ntitle: My Video\nurl: https://www.youtube.com/watch?v=abc123\n---\n\n"
        "[0:00] Hello\n[0:05] World\n"
    )
    result = parse_transcript_file(str(f))
    assert result["title"] == "My Video"
    assert result["url"] == "https://www.youtube.com/watch?v=abc123"
    assert result["transcript"] == "[0:00] Hello\n[0:05] World"


def test_parse_transcript_file_missing_header(tmp_path):
    f = tmp_path / "no_header.txt"
    f.write_text("[0:00] Hello\n")
    with pytest.raises(ValueError, match="missing metadata header"):
        parse_transcript_file(str(f))


def test_parse_transcript_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_transcript_file("/nonexistent/file.txt")


def test_parse_transcript_file_missing_url(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("---\ntitle: My Video\n---\n\n[0:00] Hello\n")
    with pytest.raises(ValueError, match="missing title or url"):
        parse_transcript_file(str(f))


# ── load_prompt ───────────────────────────────────────────────────────────────

def test_load_prompt_success(tmp_path):
    p = tmp_path / "prompt.md"
    p.write_text("Summarize this: {{transcript}}")
    assert load_prompt(str(p)) == "Summarize this: {{transcript}}"


def test_load_prompt_not_found():
    with pytest.raises(FileNotFoundError):
        load_prompt("/nonexistent/prompt.md")


# ── build_prompt ──────────────────────────────────────────────────────────────

def test_build_prompt_replaces_both_placeholders():
    template = "URL: {{url}}\n\n{{transcript}}"
    result = build_prompt(template, "https://youtube.com/watch?v=abc", "Hello World")
    assert result == "URL: https://youtube.com/watch?v=abc\n\nHello World"


def test_build_prompt_missing_transcript_placeholder(capsys):
    template = "URL: {{url}}\n\nSummarize this."
    result = build_prompt(template, "https://youtube.com/watch?v=abc", "Hello World")
    assert "Hello World" in result
    assert "Warning" in capsys.readouterr().out


# ── sanitize_filename ─────────────────────────────────────────────────────────

def test_sanitize_filename_spaces():
    assert sanitize_filename("My Video Title") == "My_Video_Title"


def test_sanitize_filename_special_chars():
    assert sanitize_filename("Video: Part #1 (Final)") == "Video_Part_1_Final"


def test_sanitize_filename_unicode():
    assert sanitize_filename("系統設計 System Design") == "_System_Design"


def test_sanitize_filename_leading_trailing_spaces():
    assert sanitize_filename("  My Video  ") == "My_Video"
