<!--
  This is a template for creating your own summarization prompt.

  Available placeholders:
    {{url}}        — replaced with the YouTube video URL
    {{transcript}} — replaced with the full timed transcript

  Both placeholders are required. {{transcript}} must appear somewhere
  in the file so the transcript content is included in the prompt.

  The language of the summary output will match the language of this prompt.
  Write in English for an English summary, French for a French summary, etc.

  Save your customized version as summarize_prompts/summarize.md in your
  project directory. The skill will use it automatically on the next run.
-->

# Your prompt title here

Video URL: {{url}}

Write your instructions here. For example:
- Summarize the key points
- List the main topics covered
- Identify any action items

## Transcript

{{transcript}}
