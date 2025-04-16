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

# Confirm connection
print("MT5 initialized successfully")

# Choose the symbol (try GOOGL or GOOG depending on what ATFX uses)
symbol = "EURUSD"

# Check if the symbol is available
if not mt5.symbol_select(symbol, True):
    print(f"Failed to select symbol {symbol}")
    mt5.shutdown()
    quit()

# Get the latest tick
tick = mt5.symbol_info_tick(symbol)
if tick:
    print(f"{symbol} bid: {tick.bid}, ask: {tick.ask}, time: {datetime.fromtimestamp(tick.time)}")
else:
    print(f"Failed to get tick data for {symbol}")

# Shutdown MT5 connection
mt5.shutdown()
