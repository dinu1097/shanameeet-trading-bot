import MetaTrader5 as mt5
import time
from datetime import datetime
from tabulate import tabulate

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

# Store arbitrage data
arbitrage_log = []

# Fetch price data
def fetch_prices(broker_name, credentials):
    if not mt5.initialize(server=credentials["server"], login=credentials["login"], password=credentials["password"]):
        print(f"[ERROR] Failed to connect to {broker_name}: {mt5.last_error()}")
        return {}
    prices = {}
    for symbol in stocks:
        tick = mt5.symbol_info_tick(symbol)
        if tick and tick.ask > 0 and tick.bid > 0:
            prices[symbol] = {"ask": tick.ask, "bid": tick.bid}
    mt5.shutdown()
    return prices

# Detect arbitrage
def detect_arbitrage(symbol, atfx, th):
    opportunities = []

    if atfx["bid"] > th["ask"]:
        profit = round(((atfx["bid"] - th["ask"]) / th["ask"]) * 100, 4)
        opportunities.append([
            datetime.now().strftime('%H:%M:%S'), symbol,
            "ATFX", atfx["bid"], "TradersHub", th["ask"],
            f"{profit}%", "Long"
        ])

    if th["bid"] > atfx["ask"]:
        profit = round(((th["bid"] - atfx["ask"]) / atfx["ask"]) * 100, 4)
        opportunities.append([
            datetime.now().strftime('%H:%M:%S'), symbol,
            "TradersHub", th["bid"], "ATFX", atfx["ask"],
            f"{profit}%", "Short"
        ])

    return opportunities

# Main loop
def main_loop():
    headers = ["Time", "Symbol", "Sell Broker", "Sell Price", "Buy Broker", "Buy Price", "Profit %", "Type"]
    print("📊 Arbitrage Opportunities\n")
    print(tabulate([headers], tablefmt="plain"))

    while True:
        prices_atfx = fetch_prices("ATFX", brokers["ATFX"])
        prices_th = fetch_prices("TradersHub", brokers["TradersHub"])

        if not prices_atfx or not prices_th:
            print("⚠️ Connection failed. Retrying in 3 sec...")
            time.sleep(3)
            continue

        for symbol in stocks:
            if symbol not in prices_atfx or symbol not in prices_th:
                continue
            atfx = prices_atfx[symbol]
            th = prices_th[symbol]

            new_entries = detect_arbitrage(symbol, atfx, th)
            for entry in new_entries:
                print(tabulate([entry], tablefmt="plain"))

        time.sleep(1)

if __name__ == "__main__":
    main_loop()
