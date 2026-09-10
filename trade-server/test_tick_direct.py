import MetaTrader5 as mt5
import json
import time

def test_direct():
    print("Reading credentials from lps.json...")
    try:
        with open("C:/Users/DELL/Desktop/New-folder-my/lps.json", "r") as f:
            lps = json.load(f)
        
        # Get MT5 credentials
        params = lps["profiles"]["MT5_Primary"]["params"]
        login = int(params["login"])
        password = params["password"]
        server = params["server"]
        path = params.get("path", "")
        
        # Clean path up
        path = path.replace("\\\\", "\\")
        
        print(f"Login ID: {login}")
        print(f"Server: {server}")
        print(f"Terminal Path: {path}")
    except Exception as e:
        print(f"Error reading lps.json: {e}")
        return

    print("\nInitializing MetaTrader 5...")
    if path:
        initialized = mt5.initialize(path=path, login=login, password=password, server=server)
    else:
        initialized = mt5.initialize(login=login, password=password, server=server)
        
    if not initialized:
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        return
        
    print("Successfully connected to MT5 broker!")
    
    # Check account info
    acc_info = mt5.account_info()
    if acc_info:
        print(f"Account Balance: {acc_info.balance}")
        print(f"Account Equity: {acc_info.equity}")
        
    # Test BTCUSD
    symbol = "BTCUSD"
    print(f"\nSelecting symbol {symbol}...")
    selected = mt5.symbol_select(symbol, True)
    if not selected:
        print(f"Failed to select symbol {symbol}: {mt5.last_error()}")
    else:
        print(f"Symbol {symbol} selected successfully!")
        
        # Poll tick data 5 times
        print("\nPolling ticks for BTCUSD:")
        for i in range(5):
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"  [{i+1}] Time: {tick.time} | Bid: {tick.bid} | Ask: {tick.ask} | Last: {tick.last}")
            else:
                print(f"  [{i+1}] tick is None! last_error: {mt5.last_error()}")
            time.sleep(1.0)
            
    # Test EURUSD
    symbol_forex = "EURUSD"
    print(f"\nSelecting symbol {symbol_forex}...")
    selected_forex = mt5.symbol_select(symbol_forex, True)
    if not selected_forex:
        print(f"Failed to select symbol {symbol_forex}: {mt5.last_error()}")
    else:
        print(f"Symbol {symbol_forex} selected successfully!")
        
        # Poll tick data 5 times
        print(f"\nPolling ticks for {symbol_forex}:")
        for i in range(5):
            tick = mt5.symbol_info_tick(symbol_forex)
            if tick:
                print(f"  [{i+1}] Time: {tick.time} | Bid: {tick.bid} | Ask: {tick.ask} | Last: {tick.last}")
            else:
                print(f"  [{i+1}] tick is None! last_error: {mt5.last_error()}")
            time.sleep(1.0)
            
    mt5.shutdown()
    print("\nMT5 shutdown completed.")

if __name__ == "__main__":
    test_direct()
