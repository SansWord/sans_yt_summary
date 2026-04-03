# Example: Shia LaBeouf "Just Do It"

**Video:** [Shia LaBeouf "Just Do It" Motivational Speech](https://www.youtube.com/watch?v=ZXsQAXx_ao0)  
**Duration:** ~1 minute  
**By:** LaBeouf, Rönkkö & Turner

This example uses the same short video to show how different `summarize.md` prompts produce very different outputs — from a standard structured summary to tweet-ready copy.

## Prompts

| Prompt | Style | Best for | Output |
|--------|-------|----------|--------|
| [standard.md](./prompts/standard.md) | Default structured summary | General use | [view](./outputs/standard.md) |
| [key-quotes.md](./prompts/key-quotes.md) | Extract notable quotes with timestamps | Speeches, interviews | [view](./outputs/key-quotes.md) |
| [action-items.md](./prompts/action-items.md) | Distill into actionable takeaways only | Productivity, learning | [view](./outputs/action-items.md) |
| [tweet.md](./prompts/tweet.md) | Compress into a tweet thread | Sharing, social media | [view](./outputs/tweet.md) |
| [summarize_system_design_zh.md](./prompts/summarize_system_design_zh.md) | System design analysis in Traditional Chinese | Tech interviews — ⚠️ this video is clearly not a system design video | [view](./outputs/summarize_system_design_zh.md) |

## How to try it

**Option A — Reference the prompt file directly (no copying needed):**
> "Use examples/just-do-it/prompts/key-quotes.md to summarize https://www.youtube.com/watch?v=ZXsQAXx_ao0"

**Option B — Copy to your project and reference by filename:**
```bash
cp examples/just-do-it/prompts/tweet.md summarize_prompts/tweet.md
```
> "Use tweet.md to summarize https://www.youtube.com/watch?v=ZXsQAXx_ao0"

**Option C — Set as your default prompt:**
```bash
mkdir -p summarize_prompts
cp examples/just-do-it/prompts/key-quotes.md summarize_prompts/summarize.md
```
> "Summarize this video: https://www.youtube.com/watch?v=ZXsQAXx_ao0"
