# Trading Bot

Autonomous AI trading agent powered by Claude Code. Runs five scheduled workflows per trading day on Alpaca. All state lives in Git.

## Quick Start

1. Copy `env.template` to `.env` and fill in credentials.
2. Open this repo in Claude Code.
3. Run `/portfolio` to verify account connectivity.

## Execution Modes

- **Local**: slash commands in `.claude/commands/` using `.env`
- **Cloud**: scheduled routines in `routines/` using env vars set on the routine

## Key Files

- `CLAUDE.md` — agent rulebook, auto-loaded every session
- `memory/` — persistent state (committed to main after every run)
- `scripts/` — API wrappers (alpaca, perplexity, clickup)
- `routines/` — cloud routine prompts (paste verbatim into Claude Code routines)
- `.claude/commands/` — local slash commands

## Schedule (America/Chicago, weekdays)

| Routine | Cron | Purpose |
|---------|------|---------|
| pre-market | `0 6 * * 1-5` | Research catalysts, write trade ideas |
| market-open | `30 8 * * 1-5` | Execute approved trades, set stops |
| midday | `0 12 * * 1-5` | Cut losers, tighten stops on winners |
| daily-summary | `0 15 * * 1-5` | EOD snapshot, ClickUp recap |
| weekly-review | `0 16 * * 5` | Weekly stats, letter grade, strategy updates |
