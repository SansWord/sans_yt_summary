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

**2. Check for custom prompt**

If `summarize_prompts/summarize.md` does not exist in the current working directory, ask the user:

> "No custom summary prompt found. Would you like to copy the default prompt to `summarize_prompts/summarize.md` so you can customize it?"

- If **yes**: copy `<base_dir>/summarize_prompts/summarize.md` to `summarize_prompts/summarize.md` (create the directory if needed). Then show the user the contents of the file and say: "Review and edit `summarize_prompts/summarize.md` as needed, then let me know when you're ready to continue." Stop and wait for the user to confirm before proceeding.
- If **no**: use `<base_dir>/summarize_prompts/summarize.md` directly as the prompt for this run.

If `summarize_prompts/summarize.md` already exists in the current directory, use it without asking.

**3. Check for cookies**

If the user passes `--cookies FILE`, use that path. Otherwise the script handles cookies automatically via Chrome.

If `.youtube_cookies.txt` does not exist in the current directory and no `--cookies` flag was given, warn the user before proceeding:

> "No cached YouTube cookies found. The script will export your YouTube cookies from Chrome, which will prompt you for your system password (macOS Keychain). This only happens once — the cookies will be saved to `.youtube_cookies.txt` for future runs.
>
> Make sure `.youtube_cookies.txt` is in your `.gitignore` to avoid accidentally committing your YouTube session."

Then check if `.gitignore` exists and does not already contain `.youtube_cookies.txt`. If so, offer to add it automatically before continuing.

**4. List available languages**

Run:
```bash
python3 <base_dir>/scripts/fetch_transcript.py --list-langs [--cookies FILE] "URL"
```

Show the language list to the user and ask which one to use. Default recommendation: pick `en` or `en-*` if available.

**5. Fetch the transcript**

Run:
```bash
python3 <base_dir>/scripts/fetch_transcript.py --lang CHOSEN [--cookies FILE] "URL"
```

This saves `<video_id>.txt` in the current directory.

**6. Summarize**

Read the saved `.txt` file. Load `summarize_prompts/summarize.md` from the current working directory (resolved in step 2) and apply it to the transcript content to produce the summary. Do not call the Anthropic API or run any summarize script — Claude produces the summary directly.

**7. Save the summary**

Write the summary to a `.md` file in the current directory. Use the video title (from the `.txt` file header) as the filename: sanitize it by replacing spaces with `_` and removing special characters, then append `_summary.md`. For example, a title of "My Video Title" becomes `My_Video_Title_summary.md`.

If the file already exists, overwrite it.

Do not print the summary in the conversation. Just tell the user the filename it was saved to, and whether it was created or updated.
