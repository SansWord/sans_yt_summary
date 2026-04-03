# Examples

This folder shows how different `summarize.md` prompts produce different results from the same video.

Copy any prompt from `prompts/` to your project's `summarize_prompts/summarize.md` to use it:

```bash
mkdir -p summarize_prompts
cp examples/just-do-it/prompts/key-quotes.md summarize_prompts/summarize.md
```

Or ask Claude directly:
> "I want to customize the YouTube summary prompt"

## Available examples

| Folder | Video | What it demonstrates |
|--------|-------|----------------------|
| [just-do-it](./just-do-it/) | Shia LaBeouf "Just Do It" | 4 different prompt styles on the same 1-minute video |
