import pytest
from fetch_transcript import extract_video_id


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


from fetch_transcript import format_segments


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
