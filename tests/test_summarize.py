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


from anthropic import RateLimitError, AuthenticationError
from summarize import call_claude, summarize, main


def test_call_claude_success():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Summary text here")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50

    with patch("summarize.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.return_value = mock_response
        text, usage = call_claude("My prompt", "claude-opus-4-6")

    assert text == "Summary text here"
    assert usage.input_tokens == 100
    assert usage.output_tokens == 50


def test_call_claude_rate_limit():
    with patch("summarize.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = RateLimitError(
            message="rate limit", response=MagicMock(status_code=429), body={}
        )
        with pytest.raises(RateLimitError):
            call_claude("My prompt", "claude-opus-4-6")


def test_call_claude_auth_error():
    with patch("summarize.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = AuthenticationError(
            message="auth error", response=MagicMock(status_code=401), body={}
        )
        with pytest.raises(AuthenticationError):
            call_claude("My prompt", "claude-opus-4-6")


def test_summarize_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transcript_file = tmp_path / "abc123.txt"
    transcript_file.write_text(
        "---\ntitle: My Video Title\nurl: https://www.youtube.com/watch?v=abc123\n---\n\n"
        "[0:00] Hello world\n"
    )
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Summarize: {{url}}\n\n{{transcript}}")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="# Summary\n\nGreat video.")]
    mock_response.usage.input_tokens = 200
    mock_response.usage.output_tokens = 30

    with patch("summarize.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.return_value = mock_response
        output_path = summarize(str(transcript_file), model="claude-opus-4-6", prompt_path=str(prompt_file))

    assert output_path == "My_Video_Title_summary.md"
    assert (tmp_path / "My_Video_Title_summary.md").read_text() == "# Summary\n\nGreat video."


def test_main_success(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transcript_file = tmp_path / "abc123.txt"
    transcript_file.write_text(
        "---\ntitle: My Video\nurl: https://www.youtube.com/watch?v=abc123\n---\n\n[0:00] Hello\n"
    )
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("{{url}}\n\n{{transcript}}")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Summary here")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 20

    with patch("sys.argv", ["summarize.py", str(transcript_file), "--prompt", str(prompt_file)]):
        with patch("summarize.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.return_value = mock_response
            main()

    captured = capsys.readouterr()
    assert "Summary complete" in captured.out
    assert "Input: 100" in captured.out
    assert "Output: 20" in captured.out
    assert "Summary saved to My_Video_summary.md" in captured.out


def test_main_rate_limit_error(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transcript_file = tmp_path / "abc123.txt"
    transcript_file.write_text(
        "---\ntitle: My Video\nurl: https://www.youtube.com/watch?v=abc123\n---\n\n[0:00] Hello\n"
    )
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("{{url}}\n\n{{transcript}}")

    with patch("sys.argv", ["summarize.py", str(transcript_file), "--prompt", str(prompt_file)]):
        with patch("summarize.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = RateLimitError(
                message="rate limit", response=MagicMock(status_code=429), body={}
            )
            with pytest.raises(SystemExit) as exc:
                main()

    assert exc.value.code == 1
    assert "rate limit" in capsys.readouterr().out.lower()


def test_main_auth_error(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transcript_file = tmp_path / "abc123.txt"
    transcript_file.write_text(
        "---\ntitle: My Video\nurl: https://www.youtube.com/watch?v=abc123\n---\n\n[0:00] Hello\n"
    )
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("{{url}}\n\n{{transcript}}")

    with patch("sys.argv", ["summarize.py", str(transcript_file), "--prompt", str(prompt_file)]):
        with patch("summarize.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = AuthenticationError(
                message="auth error", response=MagicMock(status_code=401), body={}
            )
            with pytest.raises(SystemExit) as exc:
                main()

    assert exc.value.code == 1
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().out
