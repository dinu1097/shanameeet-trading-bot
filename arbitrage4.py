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

# Trade history log
trade_log = []

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
    new_trades = []

    # Long: Buy from TradersHub, Sell to ATFX
    if atfx["bid"] > th["ask"]:
        profit = round(((atfx["bid"] - th["ask"]) / th["ask"]) * 100, 4)
        new_trades.append({
            "Time": datetime.now().strftime('%H:%M:%S'),
            "Symbol": symbol,
            "Sell Broker": "ATFX",
            "Sell Price": atfx["bid"],
            "Buy Broker": "TradersHub",
            "Buy Price": th["ask"],
            "Profit %": profit,
            "Type": "Long"
        })

    # Short: Buy from ATFX, Sell to TradersHub
    if th["bid"] > atfx["ask"]:
        profit = round(((th["bid"] - atfx["ask"]) / atfx["ask"]) * 100, 4)
        new_trades.append({
            "Time": datetime.now().strftime('%H:%M:%S'),
            "Symbol": symbol,
            "Sell Broker": "TradersHub",
            "Sell Price": th["bid"],
            "Buy Broker": "ATFX",
            "Buy Price": atfx["ask"],
            "Profit %": profit,
            "Type": "Short"
        })

    return new_trades

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

        price_table = []
        new_trades = []

        for symbol in stocks:
            if symbol not in prices_atfx or symbol not in prices_th:
                continue
            atfx = prices_atfx[symbol]
            th = prices_th[symbol]

            price_table.append([symbol, atfx["ask"], atfx["bid"], th["ask"], th["bid"]])
            arbitrage_opps = detect_arbitrage(symbol, atfx, th)
            if arbitrage_opps:
                trade_log.extend(arbitrage_opps)
                new_trades.extend(arbitrage_opps)

        # Show current price comparison
        print(tabulate(
            price_table,
            headers=["Symbol", "ATFX Ask", "ATFX Bid", "TradersHub Ask", "TradersHub Bid"],
            tablefmt="fancy_grid"
        ))

        # Show detected arbitrage trades
        if new_trades:
            print("\n🚀 New Arbitrage Opportunities:\n")
            print(tabulate(
                [[t["Time"], t["Symbol"], t["Sell Broker"], t["Sell Price"], t["Buy Broker"], t["Buy Price"], t["Profit %"], t["Type"]] for t in new_trades],
                headers=["Time", "Symbol", "Sell Broker", "Sell Price", "Buy Broker", "Buy Price", "Profit %", "Type"],
                tablefmt="fancy_grid"
            ))
        else:
            print("\n❌ No new arbitrage found.")

        # Show full trade history
        if trade_log:
            print("\n📈 Trade History:\n")
            print(tabulate(
                [[t["Time"], t["Symbol"], t["Sell Broker"], t["Sell Price"], t["Buy Broker"], t["Buy Price"], t["Profit %"], t["Type"]] for t in trade_log],
                headers=["Time", "Symbol", "Sell Broker", "Sell Price", "Buy Broker", "Buy Price", "Profit %", "Type"],
                tablefmt="grid"
            ))

        time.sleep(1)

if __name__ == "__main__":
    main_loop()
