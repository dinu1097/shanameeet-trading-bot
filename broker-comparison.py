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

# Updated Forex pairs to track
stocks = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD',
    'NZDUSD', 'USDCAD', 'AUDNZD', 'AUDCAD', 'AUDCHF',
    'AUDJPY', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURGBP',
    'EURAUD', 'EURCHF', 'EURJPY', 'EURNZD', 'EURCAD'
]

# Simulated holdings state
holdings = {}  # stock: {"broker": name, "price": value, "side": "long"/"short", "time": timestamp}


def fetch_prices(broker_name, credentials):
    print(f"🔌 Connecting to {broker_name}...")
    if not mt5.initialize(server=credentials["server"], login=credentials["login"], password=credentials["password"]):
        print(f"[ERROR] Failed to connect to {broker_name}: {mt5.last_error()}")
        return {}

    prices = {}
    for symbol in stocks:
        tick = mt5.symbol_info_tick(symbol)
        if tick and tick.ask > 0 and tick.bid > 0:
            prices[symbol] = {
                "ask": tick.ask,
                "bid": tick.bid
            }
        else:
            print(f"[!] {broker_name} has no valid tick data for {symbol}")
    mt5.shutdown()
    return prices


def check_arbitrage(stock, broker1, price1, broker2, price2, current_time):
    result = None
    holding = holdings.get(stock)

    # Enforce cooldown of 60 seconds between trades
    if holding and current_time - holding["time"] < 60:
        return None

    # Check LONG arbitrage: buy lower, sell higher
    if price2["ask"] < price1["bid"]:
        profit_pct = round(((price1["bid"] - price2["ask"]) / price2["ask"]) * 100, 2)
        if holding:
            result = {
                "Stock": stock,
                "Sell Broker": holding["broker"],
                "Sell Price": holding["price"],
                "Buy Broker": broker2,
                "Buy Price": price2["ask"],
                "Profit %": profit_pct,
                "Type": "Long"
            }
        holdings[stock] = {"broker": broker2, "price": price2["ask"], "side": "long", "time": current_time}

    # Check SHORT arbitrage: sell higher, buy lower
    elif price2["bid"] > price1["ask"]:
        profit_pct = round(((price2["bid"] - price1["ask"]) / price1["ask"]) * 100, 2)
        if holding:
            result = {
                "Stock": stock,
                "Sell Broker": holding["broker"],
                "Sell Price": holding["price"],
                "Buy Broker": broker1,
                "Buy Price": price1["ask"],
                "Profit %": profit_pct,
                "Type": "Short"
            }
        holdings[stock] = {"broker": broker1, "price": price1["ask"], "side": "short", "time": current_time}

    return result


def main_loop():
    print("🚀 Starting live arbitrage simulation between ATFX and TradersHub...\n")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n⏱ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Checking arbitrage opportunities...\n")

        prices_atfx = fetch_prices("ATFX", brokers["ATFX"])
        prices_th = fetch_prices("TradersHub", brokers["TradersHub"])

        if not prices_atfx or not prices_th:
            print("[⚠️] Failed to get prices from one or both brokers. Retrying in 10 seconds...\n")
            time.sleep(10)
            continue

        # Price comparison table
        price_table = []
        for stock in stocks:
            p1 = prices_atfx.get(stock)
            p2 = prices_th.get(stock)
            if p1 and p2:
                price_table.append([
                    stock,
                    round(p1["ask"], 5), round(p1["bid"], 5),
                    round(p2["ask"], 5), round(p2["bid"], 5)
                ])

        print(tabulate(
            price_table,
            headers=["Symbol", "ATFX Ask", "ATFX Bid", "TradersHub Ask", "TradersHub Bid"],
            tablefmt="fancy_grid"
        ))

        # Arbitrage opportunity table
        opportunities = []
        current_time = time.time()

        for stock in stocks:
            price_atfx = prices_atfx.get(stock)
            price_th = prices_th.get(stock)
            if not price_atfx or not price_th:
                continue

            result1 = check_arbitrage(stock, "ATFX", price_atfx, "TradersHub", price_th, current_time)
            if result1:
                opportunities.append(result1)

            result2 = check_arbitrage(stock, "TradersHub", price_th, "ATFX", price_atfx, current_time)
            if result2:
                opportunities.append(result2)

        if opportunities:
            print("\n💰 Arbitrage Opportunities:\n")
            print(tabulate(
                [[r['Stock'], r['Sell Broker'], r['Sell Price'], r['Buy Broker'], r['Buy Price'], r['Profit %'], r['Type']] for r in opportunities],
                headers=["Symbol", "Sell Broker", "Sell Price", "Buy Broker", "Buy Price", "Profit %", "Type"],
                tablefmt="fancy_grid"
            ))
        else:
            print("\n❌ No arbitrage opportunities found.")

        time.sleep(10)


if __name__ == "__main__":
    main_loop()
