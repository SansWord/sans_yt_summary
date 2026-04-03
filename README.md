# sans-yt-summary

Built by SansWord [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sansword/)

**TL;DR** — Paste a YouTube URL and get a structured summary saved to your project. Can also fetch transcripts on their own, or summarize a transcript file you already have.

---

Ever watched a long YouTube video just to find out it wasn't worth your time? **sans-yt-summary** is a [Claude Code](https://claude.ai/code) plugin that summarizes any YouTube video for you — just paste the URL and ask. No extra tools, no API key, no copy-pasting transcripts.

The summary includes a structured overview, key points with **clickable timestamp links** that jump directly to the moment in the video, and notable takeaways. Everything is saved as a Markdown file you can keep, search, or share.

## Why use this?

- **No API key needed** — Claude summarizes directly inside your session
- **Transcript-based** — works with auto-generated captions, no audio processing
- **Clickable timestamps** — every key point links back to the exact moment in the video
- **Customizable** — bring your own prompt to change the language, format, or focus
- **Works with any YouTube URL** — standard, live, shorts, and youtu.be links

## How it works

1. You give Claude a YouTube URL and ask it to summarize
2. The skill fetches the transcript using `yt-dlp`
3. Claude reads the transcript and produces a structured summary
4. The summary is saved as a `.md` file in your current directory

## Requirements

- [Claude Code](https://claude.ai/code)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed on your system
- Chrome browser (for exporting YouTube cookies on first run)

Install yt-dlp via Homebrew (macOS):
```bash
brew install yt-dlp
```

## Install

```bash
claude plugins marketplace add SansWord/sans_yt_summary
claude plugins install sans-yt-summary@sans_yt_summary
```

## Usage

In any Claude Code session, share a YouTube URL and ask for a summary:

> "Summarize this video: https://www.youtube.com/watch?v=VIDEO_ID"

Claude will:
1. List the available transcript languages and ask which to use
2. Fetch the transcript (exporting Chrome cookies on first run — you'll see a macOS Keychain prompt)
3. Save a `<Video_Title>_summary.md` to your current directory

### Example prompts

```
Summarize this video: https://www.youtube.com/watch?v=VIDEO_ID
```
```
Just fetch the transcript: https://www.youtube.com/watch?v=VIDEO_ID
```
```
Summarize abc123.txt
```
```
I want to customize the YouTube summary prompt
```

### Cookies

The first time you run the skill, it exports your YouTube cookies from Chrome to `.youtube_cookies.txt` in your current directory. This file contains session tokens — keep it out of version control. The `.gitignore` in this repo already excludes it, but if you're working in a different project directory:

```bash
echo ".youtube_cookies.txt" >> .gitignore
```

Subsequent runs reuse the cached file. Re-run the skill after a week or two if YouTube starts blocking requests — cookies expire.

### Custom prompt

To override the default summarization prompt, create `summarize_prompts/summarize.md` in your working directory. The skill will use your version instead of the built-in one.

Use `skills/sans-yt-summary/summarize_prompts/summarize_template.md` as a starting point:

```bash
mkdir -p summarize_prompts
cp ~/.claude/plugins/sans-yt-summary/summarize_prompts/summarize_template.md summarize_prompts/summarize.md
# Edit summarize_prompts/summarize.md to your liking
```

The summary language follows your prompt language — write the prompt in French to get a French summary.

## Running tests

```bash
pip install -r requirements.txt
pytest tests/
```

## Supported URL formats

```
https://www.youtube.com/watch?v=VIDEO_ID
https://www.youtube.com/live/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
https://youtu.be/VIDEO_ID
```

## Security note

`.youtube_cookies.txt` contains your YouTube session tokens in plaintext. The `.gitignore` in this repo excludes it by default. Never commit this file.

