import MetaTrader5 as mt5
import time
from datetime import datetime

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

# Store long and short positions, including replacement counts
positions = {symbol: {"long": None, "short": None, "long_replacement_count": 0, "short_replacement_count": 0} for symbol in stocks}

# Logger function to log the status
def log_message(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

# Fetch prices
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

# Trade simulation
def open_trade(broker_name, symbol, trade_type, price):
    log_message(f"[TRADE] {trade_type.upper()} ({'LONG' if trade_type == 'buy' else 'SHORT'}) {symbol} on {broker_name} @ {price}")

def close_trade(broker_name, symbol, trade_type, price):
    log_message(f"[CLOSE] {trade_type.upper()} ({'LONG' if trade_type == 'buy' else 'SHORT'}) {symbol} on {broker_name} @ {price}")

# Main logic
def trade_logic():
    global active
    while True:
        if not active:
            time.sleep(1)
            continue

        prices = fetch_prices()
        if prices is None:
            log_message("Stopped due to price fetching error")
            active = False
            continue

        # Clear the screen to update the table
        print("\033[H\033[J")

        # Print a header for the table
        print(f"{'Symbol':<10}{'Long Broker':<15}{'Long Price':<10}{'Short Broker':<15}{'Short Price':<10}{'Long Replaced':<15}{'Short Replaced':<15}")
        print("="*95)

        for symbol in stocks:
            # Long Logic
            best_ask_broker = min(prices.items(), key=lambda x: x[1][symbol]['ask'])
            current_long = positions[symbol]["long"]
            if current_long is None:
                positions[symbol]["long"] = {"broker": best_ask_broker[0], "price": best_ask_broker[1][symbol]['ask']}
                open_trade(best_ask_broker[0], symbol, "buy", best_ask_broker[1][symbol]['ask'])
            elif best_ask_broker[1][symbol]['ask'] < current_long["price"] - replacement_threshold:
                close_trade(current_long["broker"], symbol, "buy", current_long["price"])
                positions[symbol]["long"] = {"broker": best_ask_broker[0], "price": best_ask_broker[1][symbol]['ask']}
                positions[symbol]["long_replacement_count"] += 1  # Increment replacement count
                open_trade(best_ask_broker[0], symbol, "buy", best_ask_broker[1][symbol]['ask'])
                log_message(f"[REPLACEMENT] {symbol} LONG position replaced (Count: {positions[symbol]['long_replacement_count']})")
                time.sleep(wait_after_replacement)

            # Short Logic
            best_bid_broker = max(prices.items(), key=lambda x: x[1][symbol]['bid'])
            current_short = positions[symbol]["short"]
            if current_short is None:
                positions[symbol]["short"] = {"broker": best_bid_broker[0], "price": best_bid_broker[1][symbol]['bid']}
                open_trade(best_bid_broker[0], symbol, "sell", best_bid_broker[1][symbol]['bid'])
            elif best_bid_broker[1][symbol]['bid'] > current_short["price"] + replacement_threshold:
                close_trade(current_short["broker"], symbol, "sell", current_short["price"])
                positions[symbol]["short"] = {"broker": best_bid_broker[0], "price": best_bid_broker[1][symbol]['bid']}
                positions[symbol]["short_replacement_count"] += 1  # Increment replacement count
                open_trade(best_bid_broker[0], symbol, "sell", best_bid_broker[1][symbol]['bid'])
                log_message(f"[REPLACEMENT] {symbol} SHORT position replaced (Count: {positions[symbol]['short_replacement_count']})")
                time.sleep(wait_after_replacement)

            # Print the current state of positions in the table
            long_broker = positions[symbol]["long"]["broker"] if positions[symbol]["long"] else "None"
            long_price = positions[symbol]["long"]["price"] if positions[symbol]["long"] else "None"
            short_broker = positions[symbol]["short"]["broker"] if positions[symbol]["short"] else "None"
            short_price = positions[symbol]["short"]["price"] if positions[symbol]["short"] else "None"
            long_replacement_count = positions[symbol]["long_replacement_count"]
            short_replacement_count = positions[symbol]["short_replacement_count"]
            print(f"{symbol:<10}{long_broker:<15}{long_price:<10}{short_broker:<15}{short_price:<10}{long_replacement_count:<15}{short_replacement_count:<15}")
        
        print("="*95)
        time.sleep(1)

# Start and stop control
def start_bot():
    global active
    if not active:
        active = True
        log_message("[BOT] Started")

def stop_bot():
    global active
    if active:
        active = False
        log_message("[BOT] Stopped")

# Example control to start/stop bot
start_bot()  # Start the bot
trade_logic()  # Run the main trading logic

# To stop the bot, just call `stop_bot()` whenever needed.
