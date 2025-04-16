import MetaTrader5 as mt5
import time
import os
from tabulate import tabulate
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
        opportunities.append({
            "Symbol": symbol,
            "Sell Broker": "ATFX",
            "Sell Price": atfx["bid"],
            "Buy Broker": "TradersHub",
            "Buy Price": th["ask"],
            "Profit %": profit,
            "Type": "Long"
        })
    if th["bid"] > atfx["ask"]:
        profit = round(((th["bid"] - atfx["ask"]) / atfx["ask"]) * 100, 4)
        opportunities.append({
            "Symbol": symbol,
            "Sell Broker": "TradersHub",
            "Sell Price": th["bid"],
            "Buy Broker": "ATFX",
            "Buy Price": atfx["ask"],
            "Profit %": profit,
            "Type": "Short"
        })
    return opportunities

# Main loop
def main_loop():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n⏱ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Scanning...\n")

        prices_atfx = fetch_prices("ATFX", brokers["ATFX"])
        prices_th = fetch_prices("TradersHub", brokers["TradersHub"])

        if not prices_atfx or not prices_th:
            print("⚠️ One or both brokers failed to connect. Retrying in 3 sec...")
            time.sleep(3)
            continue

        table = []
        opportunities = []

        for symbol in stocks:
            if symbol not in prices_atfx or symbol not in prices_th:
                continue
            atfx = prices_atfx[symbol]
            th = prices_th[symbol]

            table.append([symbol, atfx["ask"], atfx["bid"], th["ask"], th["bid"]])
            opps = detect_arbitrage(symbol, atfx, th)
            opportunities.extend(opps)

        print(tabulate(
            table,
            headers=["Symbol", "ATFX Ask", "ATFX Bid", "TradersHub Ask", "TradersHub Bid"],
            tablefmt="fancy_grid"
        ))

        if opportunities:
            print("\n🚀 Arbitrage Detected:\n")
            print(tabulate(
                [[o['Symbol'], o['Sell Broker'], o['Sell Price'], o['Buy Broker'], o['Buy Price'], o['Profit %'], o['Type']] for o in opportunities],
                headers=["Symbol", "Sell Broker", "Sell Price", "Buy Broker", "Buy Price", "Profit %", "Type"],
                tablefmt="fancy_grid"
            ))
        else:
            print("\n❌ No arbitrage found.")

        time.sleep(1)

if __name__ == "__main__":
    main_loop()
