Fetch a YouTube transcript and summarize it.

The user has provided this input: $ARGUMENTS

## Steps

**1. Parse the URL**

Extract the YouTube URL from the arguments. If no URL is given, ask the user for one.

**2. Check for cookies**

The script is at `/Users/sansword/Source/github/youtube_sd_summary/fetch_transcript.py`.

If the video is sign-in required, a cookies file is needed. Check if `cookies.txt` exists in the working directory. If the user passes `--cookies FILE`, use that path.

**3. List available languages**

Run:
```bash
python3 /Users/sansword/Source/github/youtube_sd_summary/fetch_transcript.py --list-langs [--cookies FILE] "URL"
```

Show the language list to the user and ask which one to use. Default recommendation: pick `en` or `en-*` if available.

**4. Fetch the transcript**

Run:
```bash
python3 /Users/sansword/Source/github/youtube_sd_summary/fetch_transcript.py --lang CHOSEN [--cookies FILE] "URL"
```

This saves `<video_id>.txt` in the current directory.

**5. Summarize**

Read the saved `.txt` file. Then read `prompts/summarize.md` from the script directory for the summarization prompt and instructions.

Apply the prompt to the transcript content and produce the summary. Output it directly in the conversation — do not call the Anthropic API or run `summarize.py`.
