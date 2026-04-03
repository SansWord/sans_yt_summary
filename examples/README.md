# Examples

This folder shows how different `summarize.md` prompts produce different results from the same video.

You can use any prompt file in three ways:

**Reference directly** — no copying needed:
> "Use examples/just-do-it/prompts/tweet.md to summarize https://..."

**Copy and reference by filename:**
```bash
cp examples/just-do-it/prompts/tweet.md summarize_prompts/tweet.md
```
> "Use tweet.md to summarize https://..."

**Set as your default** — used automatically on every run:
```bash
mkdir -p summarize_prompts
cp examples/just-do-it/prompts/key-quotes.md summarize_prompts/summarize.md
```

## Available examples

| Folder | Video | What it demonstrates |
|--------|-------|----------------------|
| [just-do-it](./just-do-it/) | Shia LaBeouf "Just Do It" | 4 different prompt styles on the same 1-minute video |
