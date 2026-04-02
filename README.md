# YouTube Transcript Fetcher & Summarizer

Fetches the timed transcript of a YouTube video, then summarizes it using Claude AI.

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

## API Key Setup

The summarization step requires an Anthropic API key.

**Step 1 — Get your API key** from [console.anthropic.com](https://console.anthropic.com/) → API Keys.

**Step 2 — Set the environment variable:**

For the current terminal session only:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

To persist across sessions, add it to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

> Never commit your API key to version control. If you use a `.env` file, add it to `.gitignore`.

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

## Summarization

Summarize a transcript using Claude AI.

### Full pipeline (recommended)

Fetch and summarize in one command:

```bash
python3 pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID"

# With cookies for sign-in required videos
python3 pipeline.py --cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"

# Use a faster/cheaper model
python3 pipeline.py --model claude-sonnet-4-6 "URL"

# Use a custom prompt
python3 pipeline.py --prompt prompts/my_prompt.md "URL"
```

Output: `<Video_Title>_summary.md` in the current directory.

### Summarize only (transcript already fetched)

```bash
python3 summarize.py VIDEO_ID.txt
python3 summarize.py VIDEO_ID.txt --model claude-sonnet-4-6
python3 summarize.py VIDEO_ID.txt --prompt prompts/my_prompt.md
```

### Custom prompts

Copy `prompts/summarize_template.md` as a starting point:

```bash
cp prompts/summarize_template.md prompts/my_prompt.md
# Edit prompts/my_prompt.md to your liking
python3 pipeline.py --prompt prompts/my_prompt.md "URL"
```

The summary language follows the prompt language — Traditional Chinese prompt produces a Chinese summary, English prompt produces an English summary.

## Security note

`cookies.txt` contains your YouTube session tokens in plaintext. Keep it out of version control:
```bash
echo "cookies.txt" >> .gitignore
```
