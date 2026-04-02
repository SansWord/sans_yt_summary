---
name: sans-yt-summary
description: Use this skill when the user wants to summarize a YouTube video, fetch a YouTube transcript, or shares a YouTube URL and asks for a summary or overview.
version: 1.0.0
---

# Summarize YouTube Video

Fetch a YouTube transcript and summarize it using Claude.

The `fetch_transcript.py` script is at `scripts/fetch_transcript.py` inside this skill's base directory. Your system context shows the base directory as "Base directory for this skill: <path>". Use that path to construct the full script path: `<base_dir>/scripts/fetch_transcript.py`.

## Steps

**1. Parse the URL**

Extract the YouTube URL from the user's message. If no URL is given, ask the user for one.

**2. Check for cookies**

If the user passes `--cookies FILE`, use that path. Otherwise the script handles cookies automatically via Chrome.

If `.youtube_cookies.txt` does not exist in the current directory and no `--cookies` flag was given, warn the user before proceeding:

> "No cached YouTube cookies found. The script will export your YouTube cookies from Chrome, which will prompt you for your system password (macOS Keychain). This only happens once — the cookies will be saved to `.youtube_cookies.txt` for future runs.
>
> Make sure `.youtube_cookies.txt` is in your `.gitignore` to avoid accidentally committing your YouTube session."

Then check if `.gitignore` exists and does not already contain `.youtube_cookies.txt`. If so, offer to add it automatically before continuing.

**3. List available languages**

Run:
```bash
python3 <base_dir>/scripts/fetch_transcript.py --list-langs [--cookies FILE] "URL"
```

Show the language list to the user and ask which one to use. Default recommendation: pick `en` or `en-*` if available.

**4. Fetch the transcript**

Run:
```bash
python3 <base_dir>/scripts/fetch_transcript.py --lang CHOSEN [--cookies FILE] "URL"
```

This saves `<video_id>.txt` in the current directory.

**5. Summarize**

Read the saved `.txt` file. Then load the summarization prompt:
- If `summarize_prompts/summarize.md` exists in the current working directory, use that.
- Otherwise fall back to `<base_dir>/summarize_prompts/summarize.md`.

Apply the prompt to the transcript content and produce the summary. Do not call the Anthropic API or run any summarize script — Claude produces the summary directly.

**6. Save the summary**

Write the summary to a `.md` file in the current directory. Use the video title (from the `.txt` file header) as the filename: sanitize it by replacing spaces with `_` and removing special characters, then append `_summary.md`. For example, a title of "My Video Title" becomes `My_Video_Title_summary.md`.

Do not print the summary in the conversation. Just tell the user the filename it was saved to.
