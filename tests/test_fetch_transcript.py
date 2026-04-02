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
