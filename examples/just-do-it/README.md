# Example: Shia LaBeouf "Just Do It"

**Video:** [Shia LaBeouf "Just Do It" Motivational Speech](https://www.youtube.com/watch?v=ZXsQAXx_ao0)  
**Duration:** ~1 minute  
**By:** LaBeouf, Rönkkö & Turner

This example uses the same short video to show how different `summarize.md` prompts produce very different outputs — from a standard structured summary to tweet-ready copy.

## Prompts

| File | Style | Best for |
|------|-------|----------|
| [standard.md](./prompts/standard.md) | Default structured summary | General use |
| [key-quotes.md](./prompts/key-quotes.md) | Extract notable quotes with timestamps | Speeches, interviews |
| [action-items.md](./prompts/action-items.md) | Distill into actionable takeaways only | Productivity, learning |
| [tweet.md](./prompts/tweet.md) | Compress into a tweet thread | Sharing, social media |

## Outputs

See [outputs/](./outputs/) for what each prompt produces on this video.

## How to try it

1. Copy a prompt to your project:
   ```bash
   mkdir -p summarize_prompts
   cp examples/just-do-it/prompts/key-quotes.md summarize_prompts/summarize.md
   ```
2. Ask Claude to summarize the video:
   > "Summarize this video: https://www.youtube.com/watch?v=ZXsQAXx_ao0"
