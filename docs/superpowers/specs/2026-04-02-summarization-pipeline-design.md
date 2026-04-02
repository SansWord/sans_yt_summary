# Summarization Pipeline — Design Spec

**Date:** 2026-04-02
**Status:** Approved

---

## Overview

Extend the YouTube transcript fetcher with a summarization step powered by the Claude API (Anthropic SDK). Users can run a single command to go from a YouTube URL to a structured summary `.md` file. The transcript fetcher remains usable standalone.

---

## Usage

```bash
# Full pipeline: fetch + summarize
python3 pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID" [--cookies cookies.txt] [--model MODEL] [--prompt FILE]

# Summarize only (transcript already fetched)
python3 summarize.py <video_id>.txt [--model MODEL] [--prompt FILE]

# Transcript only (unchanged)
python3 fetch_transcript.py "URL" [--cookies cookies.txt]
```

**Model flag:**
- Default: `claude-opus-4-6`
- Override: `--model claude-sonnet-4-6` (or any valid model ID)

**Prompt flag:**
- Default: `prompts/summarize.md`
- Override: `--prompt prompts/custom.md`

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `fetch_transcript.py` | Modify | Add `---` metadata header to saved `.txt` |
| `summarize.py` | Create | Read `.txt`, call Claude, save `_summary.md` |
| `pipeline.py` | Create | Orchestrate fetch + summarize |
| `prompts/summarize.md` | Create | Default prompt (Traditional Chinese, ready to use) |
| `prompts/summarize_template.md` | Create | Template with comments explaining placeholders, for users who want to write their own prompt |
| `tests/test_summarize.py` | Create | Unit tests for summarize.py |
| `tests/test_pipeline.py` | Create | Unit tests for pipeline.py |
| `tests/test_fetch_transcript.py` | Modify | Add tests for metadata header |

---

## Transcript File Format (updated)

`fetch_transcript.py` prepends a YAML-style metadata block:

```
---
title: Airline Flight Ticketing System Design
url: https://www.youtube.com/watch?v=ckkbxPE-5wc
---

[0:01] Okay so today we are going to be
[0:04] covering the airline flight ticketing problem.
```

The title is fetched from yt-dlp at transcript download time using `%(title)s`.

---

## Architecture

### `summarize.py`

Functions:

| Function | Signature | Responsibility |
|---|---|---|
| `parse_transcript_file` | `(path: str) -> dict` | Parse metadata header + body; returns `{title, url, transcript}` |
| `load_prompt` | `(path: str) -> str` | Read prompt `.md` file |
| `build_prompt` | `(template: str, url: str, transcript: str) -> str` | Replace `{{url}}` and `{{transcript}}` |
| `call_claude` | `(prompt: str, model: str) -> tuple[str, Usage]` | Call Anthropic SDK; return (response text, usage) |
| `sanitize_filename` | `(title: str) -> str` | Spaces → underscores, strip special chars |
| `summarize` | `(transcript_path, model, prompt_path) -> str` | Orchestrate; return output file path |
| `main` | `() -> None` | CLI entry point |

### `pipeline.py`

Thin orchestrator — no business logic:
1. Call `fetch_transcript.fetch_transcript()` → get `<video_id>.txt`
2. Call `summarize.summarize()` → get `<title>_summary.md`

### `prompts/summarize.md`

The ready-to-use default prompt — prefilled with the Traditional Chinese system design prompt. Hardcoded URL replaced with `{{url}}`. Transcript injected via `{{transcript}}` at the end.

### `prompts/summarize_template.md`

A starter template with inline comments explaining each placeholder and section. Intended for users who want to write their own prompt. Not used by the script directly.

---

## Data Flow

```
pipeline.py "URL" [--cookies FILE] [--model MODEL] [--prompt FILE]
    │
    ├─ fetch_transcript() → ckkbxPE-5wc.txt
    │     ---
    │     title: Airline Flight Ticketing System Design
    │     url: https://www.youtube.com/watch?v=ckkbxPE-5wc
    │     ---
    │     [0:01] Okay so today...
    │
    └─ summarize() → Airline_Flight_Ticketing_System_Design_summary.md
          ├─ parse header → title, url, transcript body
          ├─ load prompts/summarize_template.md
          ├─ replace {{url}} and {{transcript}}
          ├─ call Claude (claude-opus-4-6)
          ├─ print token usage to console
          └─ save summary .md
```

---

## Output

**Console (always English):**
```
Fetching transcript for video: ckkbxPE-5wc
Transcript saved to ckkbxPE-5wc.txt
Summarizing with claude-opus-4-6...
Summary complete.
Input: 12,450 tokens | Output: 1,832 tokens | Total: 14,282 tokens
Summary saved to Airline_Flight_Ticketing_System_Design_summary.md
```

**Summary file** (`<sanitized_title>_summary.md`): content language matches the prompt language — Traditional Chinese if prompt is in Chinese, English if prompt is in English.

---

## Error Handling

| Scenario | Behavior |
|---|---|
| Transcript file not found | Print error, exit 1 |
| Metadata header missing from `.txt` | Print error, exit 1 |
| `{{transcript}}` missing from prompt | Print warning, continue (inject transcript at end) |
| Claude `RateLimitError` (429) | Print "API rate limit reached, please try again later.", exit 1 |
| Claude `AuthenticationError` | Print "Invalid or missing ANTHROPIC_API_KEY.", exit 1 |
| Other Claude API error | Print error message, exit 1 |
| Fetch step fails in pipeline | Print error, skip summarize step, exit 1 |

---

## Authentication

`ANTHROPIC_API_KEY` environment variable — handled by the Anthropic SDK automatically. Not discussed further in this spec.

---

## Prompt Template Placeholders

| Placeholder | Replaced with |
|---|---|
| `{{url}}` | Full YouTube URL from transcript metadata |
| `{{transcript}}` | Full timed transcript body |

---

## Testing

- `test_fetch_transcript.py` — add tests for metadata header written to `.txt`
- `test_summarize.py` — mock `anthropic.Anthropic` client; test `parse_transcript_file`, `build_prompt`, `sanitize_filename`, `call_claude`, file output
- `test_pipeline.py` — mock `fetch_transcript` and `summarize` functions; verify correct args passed

---

## Out of Scope

- Streaming Claude responses
- Multiple language outputs from a single run
- Retry logic on rate limit errors
- Token cost estimation in dollars
