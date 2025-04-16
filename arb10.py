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
active = False

# Store long and short positions
positions = {symbol: {"long": None, "short": None, "long_replacement_count": 0, "short_replacement_count": 0} for symbol in stocks}
previous_positions = {symbol: {"long": None, "short": None} for symbol in stocks}

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
    log_message(f"[TRADE] {trade_type.upper()} ({'LONG' if trade_type == 'buy' else 'SHORT'}) {symbol} on {broker_name} @ {price}")

def close_trade(broker_name, symbol, trade_type, price):
    log_message(f"[CLOSE] {trade_type.upper()} ({'LONG' if trade_type == 'buy' else 'SHORT'}) {symbol} on {broker_name} @ {price}")

def trade_logic():
    global active
    header_printed = False
    while True:
        if not active:
            time.sleep(1)
            continue

        prices = fetch_prices()
        if prices is None:
            log_message("Stopped due to price fetching error")
            active = False
            continue

        if not header_printed:
            print(f"{'Symbol':<12}{'Long Broker':<15}{'Long Price':<12}{'Short Broker':<15}{'Short Price':<12}{'Long Replaced':<18}{'Short Replaced':<18}")
            print("="*95)
            header_printed = True

        for symbol in stocks:
            # Long Logic
            best_ask_broker = min(prices.items(), key=lambda x: x[1][symbol]['ask'])
            best_ask_price = best_ask_broker[1][symbol]['ask']
            current_long = positions[symbol]["long"]

            if current_long is None or best_ask_price < current_long["price"]:
                if current_long is not None:
                    close_trade(current_long["broker"], symbol, "buy", current_long["price"])
                    positions[symbol]["long_replacement_count"] += 1
                positions[symbol]["long"] = {"broker": best_ask_broker[0], "price": best_ask_price}
                open_trade(best_ask_broker[0], symbol, "buy", best_ask_price)

            # Short Logic
            best_bid_broker = max(prices.items(), key=lambda x: x[1][symbol]['bid'])
            best_bid_price = best_bid_broker[1][symbol]['bid']
            current_short = positions[symbol]["short"]

            if current_short is None or best_bid_price > current_short["price"]:
                if current_short is not None:
                    close_trade(current_short["broker"], symbol, "sell", current_short["price"])
                    positions[symbol]["short_replacement_count"] += 1
                positions[symbol]["short"] = {"broker": best_bid_broker[0], "price": best_bid_price}
                open_trade(best_bid_broker[0], symbol, "sell", best_bid_price)

            # Print only if changed
            if positions[symbol]["long"] != previous_positions[symbol]["long"]:
                long_broker = positions[symbol]["long"]["broker"]
                long_price = positions[symbol]["long"]["price"]
                print(f"[TRADE] BUY (LONG) {symbol} on {long_broker} @ {long_price}")
                print(f"{symbol:<12}{long_broker:<15}{long_price:<12}{positions[symbol]['short']['broker'] if positions[symbol]['short'] else 'None':<15}{positions[symbol]['short']['price'] if positions[symbol]['short'] else 'None':<12}{positions[symbol]['long_replacement_count']:<18}{positions[symbol]['short_replacement_count']:<18}")
                previous_positions[symbol]["long"] = positions[symbol]["long"]

            if positions[symbol]["short"] != previous_positions[symbol]["short"]:
                short_broker = positions[symbol]["short"]["broker"]
                short_price = positions[symbol]["short"]["price"]
                print(f"[TRADE] SELL (SHORT) {symbol} on {short_broker} @ {short_price}")
                print(f"{symbol:<12}{positions[symbol]['long']['broker'] if positions[symbol]['long'] else 'None':<15}{positions[symbol]['long']['price'] if positions[symbol]['long'] else 'None':<12}{short_broker:<15}{short_price:<12}{positions[symbol]['long_replacement_count']:<18}{positions[symbol]['short_replacement_count']:<18}")
                previous_positions[symbol]["short"] = positions[symbol]["short"]

        print("")
        time.sleep(1)

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

# Start bot
start_bot()
trade_logic()
