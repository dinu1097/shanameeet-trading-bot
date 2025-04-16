import MetaTrader5 as mt5
import time
import os
from tabulate import tabulate

# Broker credentials (DO NOT include 'path' if MT5 terminals are already running)
brokers = {
    "ATFX": {
        "login": 150000838,
        "password": "hKT2vc6^",
        "server": "ATFXGM19-Live"
    },
    "Forex.com": {
        "login": 24755270,
        "password": "drshanemeet@gmail.com",
        "server": "Forex.comGlobalLive532"
    }
}

# Stock symbols to track
stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'INTC', 'BABA']

def fetch_prices(broker_name, credentials):
    print(f"\n🔌 Connecting to {broker_name}...")

    # Connect to the terminal (already running manually)
    if not mt5.initialize(server=credentials["server"], login=credentials["login"], password=credentials["password"]):
        print(f"[ERROR] Failed to connect to {broker_name}: {mt5.last_error()}")
        return {}

    print(f"✅ Connected to {broker_name} successfully.")

    prices = {}
    for symbol in stocks:
        tick = mt5.symbol_info_tick(symbol)
        if tick and tick.ask > 0:
            prices[symbol] = tick.ask
        else:
            print(f"[!] {broker_name} has no valid tick data for {symbol}")

    mt5.shutdown()
    return prices

def compare_prices(prices1, broker1, prices2, broker2):
    results = []
    for stock in stocks:
        price1 = prices1.get(stock)
        price2 = prices2.get(stock)
        if price1 is None or price2 is None:
            continue
        if price2 < price1:
            profit = round(((price1 - price2) / price2) * 100, 2)
            results.append([
                stock,
                broker1, round(price1, 4),
                broker2, round(price2, 4),
                f"{profit} %"
            ])
    return results

def main_loop():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
        print("🔄 Checking for live arbitrage opportunities...\n")

        prices_atfx = fetch_prices("ATFX", brokers["ATFX"])
        prices_forex = fetch_prices("Forex.com", brokers["Forex.com"])

        if prices_atfx and prices_forex:
            print("\n✅ Both brokers are connected and price data received.\n")
        else:
            print("[WARNING] Failed to fetch prices from one or both brokers. Retrying in 10 seconds...")
            time.sleep(10)
            continue

        table = compare_prices(prices_atfx, "ATFX", prices_forex, "Forex.com")
        table += compare_prices(prices_forex, "Forex.com", prices_atfx, "ATFX")  # Check both directions

        if table:
            print(tabulate(
                table,
                headers=["Stock", "Buy Broker", "Buy Price", "Better Broker", "Better Price", "Profit %"],
                tablefmt="fancy_grid"
            ))
        else:
            print("❌ No arbitrage opportunities found at this time.")

        time.sleep(10)

if __name__ == "__main__":
    main_loop()
