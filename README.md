# YouTube Transcript Fetcher

Fetches the timed transcript of a YouTube video and saves it to a `.txt` file.

## Requirements

- Python 3.9+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed on your system

Install yt-dlp via Homebrew (macOS):
```bash
brew install yt-dlp
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Public videos

```bash
python3 fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Sign-in required or bot-blocked videos

YouTube blocks automated requests for some videos. Use a cookies file to authenticate.

**Step 1 — Export your Chrome cookies (one-time setup):**
```bash
python3 fetch_transcript.py --export-cookies cookies.txt
```

This reads cookies from your Chrome browser (macOS Keychain prompt will appear) and saves them to `cookies.txt`.

**Step 2 — Fetch the transcript:**
```bash
python3 fetch_transcript.py --cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

Re-run Step 1 when the script stops working — cookies expire after days to weeks.

### Supported URL formats

```
https://www.youtube.com/watch?v=VIDEO_ID
https://www.youtube.com/live/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
https://youtu.be/VIDEO_ID
```

## Output

The transcript is printed to the console and saved to `<video_id>.txt` in the current directory.

Each line is formatted as:
```
[M:SS] transcript text here
```

Example:
```
[0:01] Okay so today we are going to be
[0:04] covering the airline flight ticketing problem.
[0:07] For the requirements, users can browse available flights.
```

## Security note

`cookies.txt` contains your YouTube session tokens in plaintext. Keep it out of version control:
```bash
echo "cookies.txt" >> .gitignore
```
