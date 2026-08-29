# Trading Discipline Journal

A local Python/Flask trading journal for the $100 → $1,000 challenge.

## Features
- Dark trading dashboard
- Trade journal
- Automatic RR calculation
- $5 daily max-loss lock
- Maximum 2 setups/day
- $100 → $1,000 progress
- Equity curve
- Rule checklist
- Rule inputs for FOMO, other signals, flow, key level, MSS and TS
- SQLite database

## Run

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Then:
```bash
pip install -r requirements.txt
python app.py
```

Open:
http://127.0.0.1:5000

## Notes
This is a journal/risk-control prototype, not financial advice or an automated trading system.
The daily lock is based on recorded closed P/L.
For production use, add authentication, PostgreSQL, HTTPS, server-side validation, backups, and a secure Telegram bot token stored in environment variables.
