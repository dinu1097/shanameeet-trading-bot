import MetaTrader5 as mt5
import time
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk

# Broker credentials
brokers = {
    "ATFX": {
        "login": 150000838,
        "password": "hKT2vc6^",
        "server": "ATFXGM19-Live"
    },
    "TradersHub": {
        "login": 5418,
        "password": "Trading@112233",
        "server": "TradersHub-Live"
    }
}

# Forex pairs to track
stocks = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD',
    'NZDUSD', 'USDCAD', 'AUDNZD', 'AUDCAD', 'AUDCHF',
    'AUDJPY', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURGBP',
    'EURAUD', 'EURCHF', 'EURJPY', 'EURNZD', 'EURCAD'
]

# Settings
lot_size = 0.01
replacement_threshold = 0.0002  # X points (e.g., 20 points = 0.0002)
wait_after_replacement = 10  # X seconds
active = False
current_positions = {"long": None, "short": None}

# Store current best positions
best_long = None
best_short = None

# Fetch broker prices
def fetch_prices(broker_name, credentials):
    if not mt5.initialize(server=credentials["server"], login=credentials["login"], password=credentials["password"]):
        return {}
    prices = {}
    for symbol in stocks:
        tick = mt5.symbol_info_tick(symbol)
        if tick and tick.ask > 0 and tick.bid > 0:
            prices[symbol] = {"ask": tick.ask, "bid": tick.bid}
    mt5.shutdown()
    return prices

# Simulate opening trade
def open_trade(broker_name, symbol, trade_type, price):
    log_message(f"[TRADE] {trade_type.upper()} on {broker_name} {symbol} @ {price}")

# Execute initial trades
def execute_initial_trades(symbol, prices):
    global best_long, best_short
    lowest_ask = min(prices.items(), key=lambda x: x[1][symbol]['ask'])
    highest_bid = max(prices.items(), key=lambda x: x[1][symbol]['bid'])

    best_long = {"broker": lowest_ask[0], "price": lowest_ask[1][symbol]['ask']}
    best_short = {"broker": highest_bid[0], "price": highest_bid[1][symbol]['bid']}

    open_trade(best_long["broker"], symbol, "buy", best_long["price"])
    open_trade(best_short["broker"], symbol, "sell", best_short["price"])

# Check and replace trades if better opportunity found
def check_replacement(symbol, prices):
    global best_long, best_short
    replaced = False

    new_best_ask = min(prices.items(), key=lambda x: x[1][symbol]['ask'])
    new_best_bid = max(prices.items(), key=lambda x: x[1][symbol]['bid'])

    if new_best_ask[1][symbol]['ask'] < best_long["price"] - replacement_threshold:
        best_long = {"broker": new_best_ask[0], "price": new_best_ask[1][symbol]['ask']}
        open_trade(best_long["broker"], symbol, "buy", best_long["price"])
        replaced = True

    if new_best_bid[1][symbol]['bid'] > best_short["price"] + replacement_threshold:
        best_short = {"broker": new_best_bid[0], "price": new_best_bid[1][symbol]['bid']}
        open_trade(best_short["broker"], symbol, "sell", best_short["price"])
        replaced = True

    return replaced

# Verify all broker connections
def check_all_connections():
    for name, creds in brokers.items():
        if not mt5.initialize(server=creds["server"], login=creds["login"], password=creds["password"]):
            return False
        mt5.shutdown()
    return True

# Logger for GUI
log_entries = []
def log_message(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entries.append(f"[{timestamp}] {msg}")
    if len(log_entries) > 100:
        log_entries.pop(0)
    log_text.set("\n".join(log_entries))

# Main bot logic

def main_logic():
    global active
    while True:
        if not active:
            time.sleep(1)
            continue

        if not check_all_connections():
            log_message("[DISCONNECTED] One or more brokers disconnected. Stopping...")
            update_status("Stopped", "red")
            active = False
            continue

        prices = {name: fetch_prices(name, creds) for name, creds in brokers.items()}
        if not all(prices.values()):
            log_message("[ERROR] Failed to fetch prices. Retrying...")
            time.sleep(3)
            continue

        for symbol in stocks:
            execute_initial_trades(symbol, prices)
        break

        while active:
            if not check_all_connections():
                log_message("[DISCONNECTED] Broker lost connection. Halting...")
                update_status("Stopped", "red")
                active = False
                break

            prices = {name: fetch_prices(name, creds) for name, creds in brokers.items()}
            for symbol in stocks:
                if check_replacement(symbol, prices):
                    time.sleep(wait_after_replacement)
            time.sleep(1)

# GUI with tkinter
app = tk.Tk()
app.title("Arbitrage Trading Bot")
app.geometry("600x400")

status_label = tk.Label(app, text="Stopped", font=("Helvetica", 16), fg="white", bg="red", width=20)
status_label.pack(pady=10)

def update_status(text, color):
    status_label.config(text=text, bg=color)

log_text = tk.StringVar()
log_display = tk.Label(app, textvariable=log_text, justify="left", anchor="nw", bg="black", fg="lime", font=("Courier", 9), width=70, height=15)
log_display.pack(padx=10, pady=5)

# Button functions
def start_bot():
    global active
    if not active:
        active = True
        update_status("Started", "green")
        log_message("[BOT] Started")

def stop_bot():
    global active
    if active:
        active = False
        update_status("Stopped", "red")
        log_message("[BOT] Stopped")

btn_frame = tk.Frame(app)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="Start", width=10, command=start_bot, bg="green", fg="white")
stop_btn = tk.Button(btn_frame, text="Stop", width=10, command=stop_bot, bg="red", fg="white")
start_btn.grid(row=0, column=0, padx=10)
stop_btn.grid(row=0, column=1, padx=10)

# Launch logic thread
threading.Thread(target=main_logic, daemon=True).start()

# Run GUI loop
app.mainloop()
