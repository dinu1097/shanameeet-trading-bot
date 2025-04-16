import tkinter as tk
from tkinter import ttk
import threading
import MetaTrader5 as mt5
import time
from datetime import datetime

# Your existing configurations...
# (brokers, stocks, positions, previous_positions, etc.)

# Shortened for readability
brokers = {"ATFX": {"login": 150000838, "password": "hKT2vc6^", "server": "ATFXGM19-Live"},
           "TradersHub": {"login": 5418, "password": "Trading@112233", "server": "TradersHub-Live"}}

# Forex pairs to track
stocks = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD',
    'NZDUSD', 'USDCAD', 'AUDNZD', 'AUDCAD', 'AUDCHF',
    'AUDJPY', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURGBP',
    'EURAUD', 'EURCHF', 'EURJPY', 'EURNZD', 'EURCAD'
]
positions = {s: {"long": None, "short": None, "long_replacement_count": 0, "short_replacement_count": 0} for s in stocks}
previous_positions = {s: {"long": None, "short": None} for s in stocks}

replacement_threshold = 0.000002
wait_after_replacement = 10
active = False

def log_message(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def fetch_prices():
    prices = {}
    for name, creds in brokers.items():
        if not mt5.initialize(server=creds["server"], login=creds["login"], password=creds["password"]):
            log_message(f"[ERROR] Failed to connect to {name}")
            return None
        broker_prices = {}
        for symbol in stocks:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                broker_prices[symbol] = {"ask": tick.ask, "bid": tick.bid}
        prices[name] = broker_prices
        mt5.shutdown()
    return prices

def open_trade(broker_name, symbol, trade_type, price):
    log_message(f"[TRADE] {trade_type.upper()} {symbol} on {broker_name} @ {price}")

def close_trade(broker_name, symbol, trade_type, price):
    log_message(f"[CLOSE] {trade_type.upper()} {symbol} on {broker_name} @ {price}")

def update_table(tree, data):
    for i in tree.get_children():
        tree.delete(i)
    for row in data:
        tree.insert("", "end", values=row)

def trade_logic_ui(tree):
    global active
    while True:
        if not active:
            time.sleep(1)
            continue

        prices = fetch_prices()
        if prices is None:
            log_message("Price fetch error")
            active = False
            continue

        ui_data = []
        for symbol in stocks:
            # LONG
            best_ask_broker = min(prices.items(), key=lambda x: x[1][symbol]['ask'])
            current_long = positions[symbol]['long']
            if not current_long:
                positions[symbol]['long'] = {"broker": best_ask_broker[0], "price": best_ask_broker[1][symbol]['ask']}
                open_trade(best_ask_broker[0], symbol, "buy", best_ask_broker[1][symbol]['ask'])
            elif best_ask_broker[1][symbol]['ask'] < current_long['price'] - replacement_threshold:
                close_trade(current_long['broker'], symbol, "buy", current_long['price'])
                previous_positions[symbol]['long'] = current_long
                positions[symbol]['long'] = {"broker": best_ask_broker[0], "price": best_ask_broker[1][symbol]['ask']}
                positions[symbol]['long_replacement_count'] += 1
                open_trade(best_ask_broker[0], symbol, "buy", best_ask_broker[1][symbol]['ask'])
                time.sleep(wait_after_replacement)

            # SHORT
            best_bid_broker = max(prices.items(), key=lambda x: x[1][symbol]['bid'])
            current_short = positions[symbol]['short']
            if not current_short:
                positions[symbol]['short'] = {"broker": best_bid_broker[0], "price": best_bid_broker[1][symbol]['bid']}
                open_trade(best_bid_broker[0], symbol, "sell", best_bid_broker[1][symbol]['bid'])
            elif best_bid_broker[1][symbol]['bid'] > current_short['price'] + replacement_threshold:
                close_trade(current_short['broker'], symbol, "sell", current_short['price'])
                previous_positions[symbol]['short'] = current_short
                positions[symbol]['short'] = {"broker": best_bid_broker[0], "price": best_bid_broker[1][symbol]['bid']}
                positions[symbol]['short_replacement_count'] += 1
                open_trade(best_bid_broker[0], symbol, "sell", best_bid_broker[1][symbol]['bid'])
                time.sleep(wait_after_replacement)

            # Prepare UI row for LONG
            long = positions[symbol]['long']
            long_prev = previous_positions[symbol]['long']
            ui_data.append(["LONG", symbol,
                            long['broker'] if long else "None",
                            long_prev['broker'] if long_prev else "None",
                            f"{long['price']:.5f}" if long else "None",
                            f"{long_prev['price']:.5f}" if long_prev else "None",
                            positions[symbol]['long_replacement_count']])

            # Prepare UI row for SHORT
            short = positions[symbol]['short']
            short_prev = previous_positions[symbol]['short']
            ui_data.append(["SHORT", symbol,
                            short['broker'] if short else "None",
                            short_prev['broker'] if short_prev else "None",
                            f"{short['price']:.5f}" if short else "None",
                            f"{short_prev['price']:.5f}" if short_prev else "None",
                            positions[symbol]['short_replacement_count']])

        update_table(tree, ui_data)
        time.sleep(1)

# GUI Setup
def start_ui():
    global active
    root = tk.Tk()
    root.title("Live Arbitrage Trading Bot")

    # Make the window resizeable and responsive
    root.geometry("900x600")  # Default size
    root.minsize(800, 600)  # Minimum size
    root.maxsize(1200, 800)  # Maximum size

    # Table setup
    columns = ("Type", "Symbol", "Current Broker", "Previous Broker", "Current Price", "Previous Price", "Replaced")
    tree = ttk.Treeview(root, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150, stretch=tk.YES)  # Allow column resizing

    tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

    # Make the treeview scrollable
    x_scroll = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    y_scroll = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    x_scroll.grid(row=1, column=0, sticky="ew")
    y_scroll.grid(row=0, column=1, sticky="ns")

    # Button frame setup
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=2, column=0, pady=10)

    def start():
        global active
        active = True
        threading.Thread(target=trade_logic_ui, args=(tree,), daemon=True).start()
        log_message("[BOT] Started")

    def stop():
        global active
        active = False
        log_message("[BOT] Stopped")

    tk.Button(btn_frame, text="Start Bot", command=start, bg="lightgreen").pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(btn_frame, text="Stop Bot", command=stop, bg="tomato").pack(side=tk.LEFT, padx=10, pady=5)

    # Make the main window resizable
    root.grid_rowconfigure(0, weight=1)  # Allow row to expand vertically
    root.grid_columnconfigure(0, weight=1)  # Allow column to expand horizontally

    root.mainloop()

start_ui()
