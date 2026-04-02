import pytest
from unittest.mock import patch, MagicMock
from pipeline import main


def test_pipeline_success(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]

    with patch("sys.argv", ["pipeline.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.fetch_transcript", return_value=(fake_segments, "My Video Title")):
            with patch("pipeline.save_transcript", return_value="abc1234.txt"):
                with patch("pipeline.summarize", return_value="My_Video_Title_summary.md"):
                    main()

    captured = capsys.readouterr()
    assert "Fetching transcript for video: abc1234" in captured.out
    assert "Transcript saved to abc1234.txt" in captured.out
    assert "Summarizing with claude-opus-4-6" in captured.out
    assert "Summary saved to My_Video_Title_summary.md" in captured.out


def test_pipeline_invalid_url(capsys):
    with patch("sys.argv", ["pipeline.py", "https://example.com"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1
    assert "Could not extract video ID" in capsys.readouterr().out


def test_pipeline_fetch_fails(capsys):
    with patch("sys.argv", ["pipeline.py", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.fetch_transcript", side_effect=RuntimeError("No transcript found")):
            with pytest.raises(SystemExit) as exc:
                main()
    assert exc.value.code == 1
    assert "No transcript found" in capsys.readouterr().out


def test_pipeline_passes_cookies(tmp_path):
    cookies_file = tmp_path / "cookies.txt"
    cookies_file.write_text("# Netscape\n")
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]

    captured_kwargs = {}

    def fake_fetch(video_id, cookies_path=None):
        captured_kwargs["cookies_path"] = cookies_path
        return fake_segments, "My Video"

    with patch("sys.argv", ["pipeline.py", "--cookies", str(cookies_file), "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.fetch_transcript", side_effect=fake_fetch):
            with patch("pipeline.save_transcript", return_value="abc1234.txt"):
                with patch("pipeline.summarize", return_value="My_Video_summary.md"):
                    main()

    assert captured_kwargs["cookies_path"] == str(cookies_file)


def test_pipeline_passes_model_and_prompt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]
    captured_kwargs = {}

    def fake_summarize(path, model=None, prompt_path=None):
        captured_kwargs["model"] = model
        captured_kwargs["prompt_path"] = prompt_path
        return "My_Video_summary.md"

    with patch("sys.argv", ["pipeline.py", "--model", "claude-sonnet-4-6", "--prompt", "custom.md", "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.fetch_transcript", return_value=(fake_segments, "My Video")):
            with patch("pipeline.save_transcript", return_value="abc1234.txt"):
                with patch("pipeline.summarize", side_effect=fake_summarize):
                    main()

    assert captured_kwargs["model"] == "claude-sonnet-4-6"
    assert captured_kwargs["prompt_path"] == "custom.md"


def test_pipeline_exports_cookies_when_missing(capsys, tmp_path):
    missing_cookies = str(tmp_path / "cookies.txt")
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]

    with patch("sys.argv", ["pipeline.py", "--cookies", missing_cookies, "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.export_cookies") as mock_export:
            with patch("pipeline.fetch_transcript", return_value=(fake_segments, "My Video")):
                with patch("pipeline.save_transcript", return_value="abc1234.txt"):
                    with patch("pipeline.summarize", return_value="My_Video_summary.md"):
                        main()

    mock_export.assert_called_once_with(missing_cookies)
    assert "Exporting from Chrome" in capsys.readouterr().out


def test_pipeline_skips_export_when_cookies_exist(tmp_path):
    cookies_file = tmp_path / "cookies.txt"
    cookies_file.write_text("# Netscape\n")
    fake_segments = [{"text": "Hello", "start": 0.0, "duration": 2.0}]

    with patch("sys.argv", ["pipeline.py", "--cookies", str(cookies_file), "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.export_cookies") as mock_export:
            with patch("pipeline.fetch_transcript", return_value=(fake_segments, "My Video")):
                with patch("pipeline.save_transcript", return_value="abc1234.txt"):
                    with patch("pipeline.summarize", return_value="My_Video_summary.md"):
                        main()

    mock_export.assert_not_called()


def test_pipeline_export_cookies_failure(capsys, tmp_path):
    missing_cookies = str(tmp_path / "cookies.txt")

    with patch("sys.argv", ["pipeline.py", "--cookies", missing_cookies, "https://www.youtube.com/watch?v=abc1234"]):
        with patch("pipeline.export_cookies", side_effect=RuntimeError("Browser not found")):
            with pytest.raises(SystemExit) as exc:
                main()

    assert exc.value.code == 1
    assert "Browser not found" in capsys.readouterr().out
