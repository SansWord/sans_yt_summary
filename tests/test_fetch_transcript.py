import pytest
from unittest.mock import patch, MagicMock
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
from fetch_transcript import extract_video_id, format_segments, fetch_transcript, main


def test_extract_video_id_watch_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_video_id_short_url():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_video_id_with_extra_params():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_video_id_invalid_url():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://example.com/not-a-video")


def test_extract_video_id_empty_string():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("")


def test_extract_video_id_short_url_with_query_params():
    url = "https://youtu.be/dQw4w9WgXcQ?si=abc123&t=10"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_video_id_short_url_empty_path():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://youtu.be/")


def test_extract_video_id_watch_url_missing_v_param():
    with pytest.raises(ValueError, match="Could not extract video ID"):
        extract_video_id("https://www.youtube.com/watch")


def test_format_segments_basic():
    segments = [
        {"text": "Hello world", "start": 0.0, "duration": 2.5},
        {"text": "This is a test", "start": 65.0, "duration": 3.0},
    ]
    result = format_segments(segments)
    assert result == "[0:00] Hello world\n[1:05] This is a test\n"


def test_format_segments_exact_minute():
    segments = [{"text": "On the minute", "start": 120.0, "duration": 1.0}]
    result = format_segments(segments)
    assert result == "[2:00] On the minute\n"


def test_format_segments_sub_ten_seconds():
    segments = [{"text": "Quick start", "start": 5.9, "duration": 1.0}]
    result = format_segments(segments)
    assert result == "[0:05] Quick start\n"


def test_format_segments_empty():
    assert format_segments([]) == ""


def test_format_segments_truncates_not_rounds():
    segments = [{"text": "x", "start": 125.4, "duration": 1.0}]
    result = format_segments(segments)
    assert result == "[2:05] x\n"


def test_fetch_transcript_success():
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]
    mock_transcript = MagicMock()
    mock_transcript.to_raw_data.return_value = fake_segments
    with patch("fetch_transcript.YouTubeTranscriptApi.fetch", return_value=mock_transcript):
        result = fetch_transcript("dQw4w9WgXcQ")
    assert result == fake_segments


def test_fetch_transcript_disabled():
    with patch("fetch_transcript.YouTubeTranscriptApi.fetch",
               side_effect=TranscriptsDisabled("dQw4w9WgXcQ")):
        with pytest.raises(TranscriptsDisabled):
            fetch_transcript("dQw4w9WgXcQ")


def test_fetch_transcript_not_found():
    mock_transcript_list = MagicMock()
    with patch("fetch_transcript.YouTubeTranscriptApi.fetch",
               side_effect=NoTranscriptFound("dQw4w9WgXcQ", [], mock_transcript_list)):
        with pytest.raises(NoTranscriptFound):
            fetch_transcript("dQw4w9WgXcQ")


def test_main_missing_argument(capsys):
    with patch("sys.argv", ["fetch_transcript.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_main_invalid_url(capsys):
    with patch("sys.argv", ["fetch_transcript.py", "https://example.com"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Could not extract video ID" in captured.out


def test_main_success(capsys, tmp_path, monkeypatch):
    fake_segments = [
        {"text": "Hello", "start": 0.0, "duration": 2.0},
        {"text": "World", "start": 5.0, "duration": 2.0},
    ]
    mock_transcript = MagicMock()
    mock_transcript.to_raw_data.return_value = fake_segments
    monkeypatch.chdir(tmp_path)
    with patch("sys.argv", ["fetch_transcript.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("fetch_transcript.YouTubeTranscriptApi.fetch", return_value=mock_transcript):
            main()
    captured = capsys.readouterr()
    assert "[0:00] Hello" in captured.out
    assert "[0:05] World" in captured.out
    output_file = tmp_path / "abc1234.txt"
    assert output_file.exists()
    content = output_file.read_text()
    assert "[0:00] Hello" in content
    assert "[0:05] World" in content


def test_main_transcript_unavailable(capsys):
    with patch("sys.argv", ["fetch_transcript.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("fetch_transcript.YouTubeTranscriptApi.fetch",
                   side_effect=TranscriptsDisabled("abc1234")):
            with pytest.raises(SystemExit) as exc:
                main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Transcript not available" in captured.out
