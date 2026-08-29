import os
import sqlite3
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)
DB_NAME = "trading_data.db"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8622254541:AAHOwR8hHnfjMrkz4y8udsEuC1jn49EHjII"
TELEGRAM_CHAT_ID = "6915043499"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                pair TEXT,
                label TEXT,
                input_price REAL,
                profit_loss REAL,
                rules_followed TEXT,
                notes TEXT
            )
        """)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS challenge (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_balance REAL
            )
        """)
        conn.execute(
            "INSERT OR IGNORE INTO challenge (id, current_balance) VALUES (1, 100.0);"
        )


def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data", methods=["GET"])
def get_data():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        trades = conn.execute("SELECT * FROM trades ORDER BY id DESC").fetchall()
        balance_row = conn.execute(
            "SELECT current_balance FROM challenge WHERE id = 1"
        ).fetchone()

    trades_list = [dict(row) for row in trades]
    current_balance = balance_row["current_balance"] if balance_row else 100.0

    return jsonify({
        "trades": trades_list,
        "challenge_balance": current_balance,
        "challenge_goal": 1000.0,
    })


@app.route("/api/trade", methods=["POST"])
def add_trade():
    data = request.json
    date = data.get("date")
    pair = data.get("pair", "XAUUSD")
    label = data.get("label")
    input_price = float(data.get("input_price"))
    profit_loss = float(data.get("profit_loss"))
    rules_followed = data.get("rules_followed", "All Followed")
    notes = data.get("notes", "")

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
                INSERT INTO trades (date, pair, label, input_price, profit_loss, rules_followed, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date,
                pair,
                label,
                input_price,
                profit_loss,
                rules_followed,
                notes,
            ),
        )

        conn.execute(
            """
                UPDATE challenge 
                SET current_balance = current_balance + ? 
                WHERE id = 1
            """,
            (profit_loss,),
        )

    status_emoji = "🟢" if profit_loss >= 0 else "🔴"
    msg = (
        f"{status_emoji} *New Trade Logged!*\n\n"
        f"💱 **Pair:** {pair}\n"
        f"🏷️ **Type:** {label}\n"
        f"💵 **Price:** {input_price}\n"
        f"💰 **P/L:** `${profit_loss}`\n"
        f"📜 **Rules:** {rules_followed}\n"
        f"📝 **Notes:** {notes}"
    )
    send_telegram_alert(msg)

    return jsonify({"status": "success"})


@app.route("/api/reset", methods=["POST"])
def reset_challenge():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM trades")
        conn.execute("UPDATE challenge SET current_balance = 100.0 WHERE id = 1")
    return jsonify({"status": "reset_success"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
