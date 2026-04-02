import json
import pytest
from unittest.mock import patch, MagicMock
from fetch_transcript import extract_video_id, _parse_json3, format_segments, fetch_transcript, export_cookies, main


# ── extract_video_id ──────────────────────────────────────────────────────────

def test_extract_video_id_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_video_id_short_url():
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_video_id_with_extra_params():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s") == "dQw4w9WgXcQ"


def test_extract_video_id_short_url_with_query_params():
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ?si=abc123&t=10") == "dQw4w9WgXcQ"


def test_extract_video_id_live_url():
    assert extract_video_id("https://www.youtube.com/live/ckkbxPE-5wc?si=abc") == "ckkbxPE-5wc"


def test_extract_video_id_invalid_url():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://example.com/not-a-video")


def test_extract_video_id_empty_string():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("")


def test_extract_video_id_short_url_empty_path():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://youtu.be/")


def test_extract_video_id_watch_url_missing_v_param():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://www.youtube.com/watch")


# ── _parse_json3 ──────────────────────────────────────────────────────────────

def test_parse_json3_basic():
    data = {
        "events": [
            {"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello world"}]},
            {"tStartMs": 65000, "dDurationMs": 3000, "segs": [{"utf8": "This is a test"}]},
        ]
    }
    result = _parse_json3(data)
    assert result == [
        {"text": "Hello world", "start": 0.0, "duration": 2.0},
        {"text": "This is a test", "start": 65.0, "duration": 3.0},
    ]


def test_parse_json3_skips_events_without_segs():
    data = {
        "events": [
            {"tStartMs": 0, "id": 1, "wpWinPosId": 1},  # layout event, no segs
            {"tStartMs": 1000, "dDurationMs": 2000, "segs": [{"utf8": "Hello"}]},
        ]
    }
    result = _parse_json3(data)
    assert len(result) == 1
    assert result[0]["text"] == "Hello"


def test_parse_json3_skips_empty_text():
    data = {
        "events": [
            {"tStartMs": 0, "dDurationMs": 1000, "segs": [{"utf8": "\n"}]},
            {"tStartMs": 1000, "dDurationMs": 2000, "segs": [{"utf8": "Real text"}]},
        ]
    }
    result = _parse_json3(data)
    assert len(result) == 1
    assert result[0]["text"] == "Real text"


def test_parse_json3_joins_multiple_segs():
    data = {
        "events": [
            {"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello "}, {"utf8": "world"}]},
        ]
    }
    result = _parse_json3(data)
    assert result[0]["text"] == "Hello world"


def test_parse_json3_empty_events():
    assert _parse_json3({"events": []}) == []


def test_parse_json3_missing_duration():
    data = {"events": [{"tStartMs": 5900, "segs": [{"utf8": "Quick start"}]}]}
    result = _parse_json3(data)
    assert result[0] == {"text": "Quick start", "start": 5.9, "duration": 0.0}


# ── format_segments ───────────────────────────────────────────────────────────

def test_format_segments_basic():
    segments = [
        {"text": "Hello world", "start": 0.0, "duration": 2.5},
        {"text": "This is a test", "start": 65.0, "duration": 3.0},
    ]
    assert format_segments(segments) == "[0:00] Hello world\n[1:05] This is a test\n"


def test_format_segments_exact_minute():
    assert format_segments([{"text": "On the minute", "start": 120.0, "duration": 1.0}]) == "[2:00] On the minute\n"


def test_format_segments_sub_ten_seconds():
    assert format_segments([{"text": "Quick start", "start": 5.9, "duration": 1.0}]) == "[0:05] Quick start\n"


def test_format_segments_truncates_not_rounds():
    assert format_segments([{"text": "x", "start": 125.4, "duration": 1.0}]) == "[2:05] x\n"


def test_format_segments_empty():
    assert format_segments([]) == ""


# ── fetch_transcript ──────────────────────────────────────────────────────────

def _make_fake_run(video_id: str, json3_data: dict):
    """Returns a subprocess.run mock that writes a json3 file into the temp dir."""
    import subprocess

    def fake_run(cmd, **kwargs):
        output_template = cmd[cmd.index("-o") + 1]
        output_dir = output_template.replace("%(id)s", video_id)
        subtitle_path = output_dir + ".en.json3"
        with open(subtitle_path, "w") as f:
            json.dump(json3_data, f)
        return MagicMock(returncode=0, stderr="")

    return fake_run


def test_fetch_transcript_success():
    fake_data = {
        "events": [{"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello"}]}]
    }
    with patch("subprocess.run", side_effect=_make_fake_run("abc123", fake_data)):
        result = fetch_transcript("abc123")
    assert result == [{"text": "Hello", "start": 0.0, "duration": 2.0}]


def test_fetch_transcript_no_subtitles():
    with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="")):
        with pytest.raises(RuntimeError, match="No English transcript found"):
            fetch_transcript("abc123")


def test_fetch_transcript_with_cookies(tmp_path):
    cookies_file = tmp_path / "cookies.txt"
    cookies_file.write_text("# Netscape HTTP Cookie File\n")
    fake_data = {"events": [{"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello"}]}]}

    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        output_template = cmd[cmd.index("-o") + 1]
        output_dir = output_template.replace("%(id)s", "abc123")
        with open(output_dir + ".en.json3", "w") as f:
            json.dump(fake_data, f)
        return MagicMock(returncode=0, stderr="")

    with patch("subprocess.run", side_effect=fake_run):
        fetch_transcript("abc123", cookies_path=str(cookies_file))

    assert "--cookies" in captured_cmd
    assert str(cookies_file) in captured_cmd



# ── export_cookies ───────────────────────────────────────────────────────────

def test_export_cookies_success(tmp_path):
    output_file = str(tmp_path / "cookies.txt")
    with patch("subprocess.run", return_value=MagicMock(returncode=0, stderr="")) as mock_run:
        export_cookies(output_file)
    cmd = mock_run.call_args[0][0]
    assert "--cookies-from-browser" in cmd
    assert "chrome" in cmd
    assert "--cookies" in cmd
    assert output_file in cmd


def test_export_cookies_failure():
    with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="Browser not found")):
        with pytest.raises(RuntimeError, match="Browser not found"):
            export_cookies("/tmp/cookies.txt")


# ── main ──────────────────────────────────────────────────────────────────────

def test_main_missing_argument(capsys):
    with patch("sys.argv", ["fetch_transcript.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 2
    assert "url" in capsys.readouterr().err


def test_main_export_cookies(capsys, tmp_path):
    output_file = str(tmp_path / "cookies.txt")
    with patch("sys.argv", ["fetch_transcript.py", "--export-cookies", output_file]):
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stderr="")):
            main()
    assert f"Cookies exported to {output_file}" in capsys.readouterr().out


def test_main_export_cookies_failure(capsys):
    with patch("sys.argv", ["fetch_transcript.py", "--export-cookies", "/tmp/cookies.txt"]):
        with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="Browser not found")):
            with pytest.raises(SystemExit) as exc:
                main()
    assert exc.value.code == 1
    assert "Browser not found" in capsys.readouterr().out


def test_main_invalid_url(capsys):
    with patch("sys.argv", ["fetch_transcript.py", "https://example.com"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1
    assert "Could not extract video ID" in capsys.readouterr().out


def test_main_success(capsys, tmp_path, monkeypatch):
    fake_data = {
        "events": [
            {"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello"}]},
            {"tStartMs": 5000, "dDurationMs": 2000, "segs": [{"utf8": "World"}]},
        ]
    }
    monkeypatch.chdir(tmp_path)
    with patch("sys.argv", ["fetch_transcript.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("subprocess.run", side_effect=_make_fake_run("abc1234", fake_data)):
            main()
    captured = capsys.readouterr()
    assert "[0:00] Hello" in captured.out
    assert "[0:05] World" in captured.out
    output_file = tmp_path / "abc1234.txt"
    assert output_file.exists()
    content = output_file.read_text()
    assert "[0:00] Hello" in content
    assert "[0:05] World" in content


def test_main_no_transcript(capsys):
    with patch("sys.argv", ["fetch_transcript.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="")):
            with pytest.raises(SystemExit) as exc:
                main()
    assert exc.value.code == 1
    assert "No English transcript found" in capsys.readouterr().out



def test_main_with_cookies(capsys, tmp_path, monkeypatch):
    cookies_file = tmp_path / "cookies.txt"
    cookies_file.write_text("# Netscape HTTP Cookie File\n")
    fake_data = {"events": [{"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "Hello"}]}]}
    monkeypatch.chdir(tmp_path)

    with patch("sys.argv", ["fetch_transcript.py", "--cookies", str(cookies_file), "https://www.youtube.com/watch?v=abc1234"]):
        with patch("subprocess.run", side_effect=_make_fake_run("abc1234", fake_data)):
            main()
    assert "[0:00] Hello" in capsys.readouterr().out
