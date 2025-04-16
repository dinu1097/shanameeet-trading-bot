import MetaTrader5 as mt5
from datetime import datetime

# Connection credentials
account = 5418
password = "Trading@112233"
server = "TradersHub-Live"

# Initialize connection
if not mt5.initialize(login=account, password=password, server=server):
    print("initialize() failed, error code =", mt5.last_error())
    quit()

print("MT5 initialized successfully")

# Get all available symbols
symbols = mt5.symbols_get()

if symbols is None:
    print("Failed to get symbols")
    mt5.shutdown()
    quit()

# Collect stock-like symbols with valid bid/ask prices
valid_stocks = []
for s in symbols:
    if not mt5.symbol_select(s.name, True):
        continue
    tick = mt5.symbol_info_tick(s.name)
    if tick and tick.bid > 0 and tick.ask > 0:
        valid_stocks.append((s.name, tick.bid, tick.ask, tick.time))
    if len(valid_stocks) >= 100:
        break

# Print results
print("\nSymbol\t\tBid\t\tAsk\t\tTime")
print("-" * 60)
for name, bid, ask, tick_time in valid_stocks:
    print(f"{name}\t{bid:.5f}\t{ask:.5f}\t{datetime.fromtimestamp(tick_time)}")

# Shutdown
mt5.shutdown()
