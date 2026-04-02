<!--
  This is a template for creating your own summarization prompt.

  Available placeholders:
    {{url}}        — replaced with the YouTube video URL
    {{transcript}} — replaced with the full timed transcript

  Both placeholders are required. {{transcript}} must appear somewhere
  in the file so the transcript content is included in the prompt sent to Claude.

  The language of the summary output will match the language of this prompt.
  Write in English for an English summary, Traditional Chinese for a Chinese summary, etc.

  Save your custom prompt anywhere and use:
    python3 summarize.py transcript.txt --prompt path/to/your_prompt.md
    python3 pipeline.py "URL" --prompt path/to/your_prompt.md
-->

# Your prompt title here

Video URL: {{url}}

Write your instructions to Claude here. For example:
- Summarize the key points
- List the main topics covered
- Identify any action items

## Transcript

{{transcript}}
