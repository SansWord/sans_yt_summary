<!--
  Template for creating a custom summarization prompt.

  Available placeholders:
    {{url}}        — the YouTube video URL
    {{transcript}} — the full timed transcript

  {{transcript}} must appear somewhere in the file. The skill automatically wraps the transcript
  content in <transcript>...</transcript> tags at runtime to guard against prompt injection.

  Recommended: include the title and URL at the top of the output, and use
  timestamp links for key points so readers can jump directly to each moment.
  Timestamp link format: [[MM:SS]](https://www.youtube.com/watch?v=VIDEO_ID&t=SECONDS)
  Extract VIDEO_ID from {{url}} and convert MM:SS to total seconds.

  The summary language follows the language of this prompt.
  Save your customized version as summarize_prompts/summarize.md in your
  project directory. The skill will use it automatically on the next run.
-->

# Your prompt title here

URL: {{url}}

## Instructions

Start with:
```
# <video title>
<URL>
```

Then write your instructions. For example:
- Write a 2-3 sentence overview
- List key points with timestamp links: [[MM:SS]](https://www.youtube.com/watch?v=VIDEO_ID&t=SECONDS)
- List takeaways or action items

## Transcript

{{transcript}}
