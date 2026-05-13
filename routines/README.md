# Cloud Routine Prompts

Paste each file verbatim into its Claude Code cloud routine. Do not paraphrase.
The env-var check block and the commit-and-push step are load-bearing.

| File | Cron (America/Chicago) | Purpose |
|------|------------------------|---------|
| pre-market.md | `0 6 * * 1-5` | Research, write trade ideas |
| market-open.md | `30 8 * * 1-5` | Execute trades, set stops |
| midday.md | `0 12 * * 1-5` | Cut losers, tighten stops |
| daily-summary.md | `0 15 * * 1-5` | EOD snapshot, ClickUp recap |
| weekly-review.md | `0 16 * * 5` | Weekly stats, letter grade |

## Prerequisites before creating routines

1. Install the Claude GitHub App on this repo.
2. Enable "Allow unrestricted branch pushes" on each routine's environment.
3. Add all env vars (ALPACA_API_KEY, ALPACA_SECRET_KEY, PERPLEXITY_API_KEY,
   CLICKUP_API_KEY, CLICKUP_WORKSPACE_ID, CLICKUP_CHANNEL_ID) to the routine —
   NOT to a .env file in the repo.
