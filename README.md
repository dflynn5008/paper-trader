# paper-trader

A minimal Alpaca **paper trading** bot to experiment with automated stock strategies safely.

## What it does

1. Connects to your Alpaca paper account
2. Scans a watchlist of symbols for SMA crossover signals
3. Manages a **virtual $100 portfolio** with position and loss limits
4. Submits paper orders when risk checks pass
5. Sends **Discord alerts** to your phone on trades and errors

## Prerequisites

- Python 3.12+ (for local runs)
- Free [Alpaca paper account](https://app.alpaca.markets/signup)
- Paper API keys from the Alpaca dashboard
- Optional: Discord webhook URL for phone alerts

## Local setup

```powershell
cd C:\Users\dflyn\Projects\paper-trader
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with your paper API keys and optional Discord webhook.

## Run locally

```powershell
python run.py
python test_discord.py   # test Discord alerts
```

Logs are written to `logs/trader.log`.

## GitHub Actions (cloud schedule)

Runs on GitHub's servers — **no need to keep your PC on**.

| Workflow | Market | Schedule |
|----------|--------|----------|
| **Paper Trader** | US stocks | Mon–Fri 21:30 UTC (~4:30 PM Eastern) |
| **Paper Trader Crypto** | Crypto (24/7) | Every hour — trades only on signals |
| **Paper Trader Daily Report** | Summary | Daily at 22:00 UTC (~6 PM Eastern) on Discord |

### Markets at a glance

- **Crypto** — true 24/7 (BTC, ETH, SOL, etc.). Uses hourly bars.
- **US stocks** — regular hours ~9:30 AM–4:00 PM ET, Mon–Fri. Uses daily bars after close.
- Alpaca also offers **24/5 stock trading** for some symbols, but this bot keeps stocks on the weekday daily schedule for now.

Stocks and crypto use **separate virtual $100 portfolios** and separate state files.

### Daily Discord dashboard

No separate web UI yet — your **daily report** lands in Discord with:

- Combined virtual equity and % change
- Stock and crypto positions, P&L, and status
- Current signals per symbol (what the bot is thinking)

Test locally: `python run_report.py`

### Smarter trading (not just blind schedules)

The bot **checks often** but **only trades when filters pass**:

- SMA crossover signal fires
- **Wisdom filter** confirms trend direction (e.g. won't buy if price is still below the slow average)
- **Drawdown guard** blocks new buys if you're down more than 20% from start
- **Capital floor** halts everything if virtual equity hits $0

### 1. Push this repo to GitHub

Create a new **private** repository on GitHub and push:

```powershell
git add .
git commit -m "Add paper trader with GitHub Actions schedule"
git remote add origin https://github.com/YOUR_USER/paper-trader.git
git push -u origin master
```

### 2. Add repository secrets

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `ALPACA_API_KEY` | Your paper API key |
| `ALPACA_SECRET_KEY` | Your paper secret key |
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL (optional) |

### 3. Run manually or wait for schedule

- **Actions** tab → **Paper Trader** → **Run workflow**
- Or wait for the weekday cron job

Portfolio state (`state/portfolio.json`) is cached between runs so P&L and halt status persist.

## Project layout

```
src/paper_trader/
  config.py            # env settings (paper-only guard)
  client.py            # Alpaca client helpers
  data.py              # historical bar fetching
  strategy/            # signal logic
  risk.py              # trade guardrails
  executor.py          # order submission
  notifier.py          # Discord alerts
  portfolio_state.py   # virtual capital tracking
run.py                 # stock entry point
run_crypto.py          # crypto entry point (24/7)
scripts/run_scheduled.ps1  # optional local Windows runner
```

## Safety defaults

- `ALPACA_PAPER=true` is required — the app refuses to start without it
- Virtual capital, position limits, and daily order caps are configurable
- Trading halts if virtual equity hits $0
- Start with paper only; treat live trading as a separate, deliberate step
