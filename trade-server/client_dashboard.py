import asyncio
import json
import threading
import time
import urllib.request
import urllib.error
import msgpack
import websockets
import sys

# Base server URLs
REST_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/marketdata"

# Global state
subscribed_symbols = set()
tick_monitor_active = False

def print_header(title):
    print("\n" + "=" * 50)
    print(f" {title.upper()} ".center(50, "="))
    print("=" * 50)

def http_get(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            return 200, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode('utf-8'))
        except Exception:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def http_post(url, data_dict=None):
    try:
        payload = json.dumps(data_dict or {}).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return 200, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode('utf-8'))
        except Exception:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def get_status():
    code, data = http_get(f"{REST_URL}/api/v1/status")
    if code == 200 and isinstance(data, dict):
        status = data.get("data", {}).get("status", "unknown")
        login = data.get("data", {}).get("login", "N/A")
        return status, login
    return "error", "N/A"

def connect_broker():
    print_header("Login to MT5 Broker")
    try:
        login_str = input("Enter MT5 Login ID (e.g. 50021345): ").strip()
        password = input("Enter Password: ").strip()
        server = input("Enter Server Name (e.g. MetaQuotes-Demo): ").strip()
        path = input("Enter MT5 Terminal Path (Leave empty for default): ").strip()
        
        login_id = int(login_str) if login_str.isdigit() else 0
        
        payload = {
            "login": login_id,
            "password": password,
            "server": server
        }
        if path:
            payload["path"] = path

        print("\nSending login request to trade-server...")
        code, data = http_post(f"{REST_URL}/api/v1/connect", payload)
        
        if code == 200 and isinstance(data, dict):
            if data.get("status") == "success":
                print("\n[SUCCESS] Connected to MetaTrader 5 successfully!")
            else:
                print(f"\n[FAILED] Server rejected login: {data.get('message')}")
        else:
            print(f"\n[FAILED] Server returned code {code}: {data}")
    except ValueError:
        print("\n[ERROR] Login ID must be a numeric integer.")
    except Exception as e:
        print(f"\n[ERROR] Could not connect: {e}")

def disconnect_broker():
    print_header("Disconnect from Broker")
    code, data = http_post(f"{REST_URL}/api/v1/disconnect")
    if code == 200:
        print("\n[SUCCESS] Disconnected from MT5 broker.")
    else:
        print(f"\n[FAILED] Disconnect failed: {data}")

def list_all_symbols():
    print_header("All Broker Symbols")
    code, syms = http_get(f"{REST_URL}/api/symbols/all")
    if code == 200 and isinstance(syms, list):
        if not syms:
            print("No symbols returned. Make sure the broker is connected!")
            return
        
        print(f"Total symbols available: {len(syms)}\n")
        print(f"{'SYMBOL':<15}{'DIGITS':<10}{'DESCRIPTION'}")
        print("-" * 50)
        # Display first 30 symbols to keep output clean, with option to search
        for s in syms[:30]:
            symbol_name = s.get("symbol", "N/A")
            digits = s.get("digits", 5)
            desc = s.get("description", "")
            print(f"{symbol_name:<15}{digits:<10}{desc}")
        if len(syms) > 30:
            print(f"\n... and {len(syms) - 30} more symbols.")
    else:
        print(f"Failed to fetch symbols (code {code}): {syms}")

def subscribe_symbol():
    print_header("Subscribe to Symbol")
    symbol = input("Enter Symbol to subscribe (e.g. ETHUSD, EURUSD): ").strip().upper()
    if not symbol:
        return
    
    status, _ = get_status()
    if status != "connected":
        print("\n[WARNING] Broker is disconnected! Ticks will only stream once logged in.")
        
    code, data = http_post(f"{REST_URL}/api/v1/subscribe", {"symbol": symbol})
    if code == 200:
        subscribed_symbols.add(symbol)
        print(f"\n[SUCCESS] Subscribed to {symbol} successfully!")
    else:
        print(f"\n[FAILED] Subscribe failed (code {code}): {data}")

def list_subscribed():
    print_header("Active Subscriptions")
    if not subscribed_symbols:
        print("No symbols subscribed in this dashboard instance yet.")
    else:
        for s in sorted(subscribed_symbols):
            print(f"  • {s}")

# Background async loop for Websocket tick receiver
async def ws_receiver():
    global tick_monitor_active
    while tick_monitor_active:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("\n[WS] Connected to Live Tick Feed WebSocket.")
                
                # Resubscribe to our symbols on connection
                for sym in subscribed_symbols:
                    await ws.send(json.dumps({"action": "sub", "symbol": sym}))
                
                while tick_monitor_active:
                    try:
                        # WS streams msgpack binary packages
                        data_bytes = await ws.recv()
                        msg = msgpack.unpackb(data_bytes, raw=False)
                        
                        # Only handle price ticks here, skip DOM book packets
                        if isinstance(msg, dict) and msg.get("type") == "book":
                            continue
                            
                        s = msg.get("s", "UNKNOWN")
                        p = msg.get("p", 0.0)
                        b = msg.get("b", 0.0)
                        a = msg.get("a", 0.0)
                        ts = msg.get("ts", 0)
                        
                        time_str = time.strftime('%H:%M:%S', time.localtime(ts / 1000.0))
                        print(f"   [TICK] {time_str} | {s:<10} | Price: {p:<10.5f} | Bid: {b:<10.5f} | Ask: {a:<10.5f}")
                    except websockets.ConnectionClosed:
                        print("\n[WS] Connection closed. Reconnecting...")
                        break
                    except Exception as e:
                        print(f"\n[WS] Error processing frame: {e}")
                        break
        except Exception as e:
            print(f"\n[WS] Could not connect to WebSocket: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

def run_ws_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws_receiver())

def start_tick_monitor():
    global tick_monitor_active
    if not subscribed_symbols:
        print("\n[WARNING] Please subscribe to at least one symbol first!")
        return
    
    print_header("Starting Real-time Ticks")
    print("Press ENTER to return to menu and stop tick display.")
    print("-" * 50)
    
    tick_monitor_active = True
    ws_thread = threading.Thread(target=run_ws_loop, daemon=True)
    ws_thread.start()
    
    input()
    tick_monitor_active = False
    print("\nTick monitor stopped.")

# Background async loop for Websocket DOM receiver
dom_monitor_active = False

async def ws_dom_receiver():
    global dom_monitor_active
    while dom_monitor_active:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("\n[WS] Connected to Live DOM WebSocket.")
                
                # Subscribe to book data for our symbols
                for sym in subscribed_symbols:
                    await ws.send(json.dumps({"action": "sub_book", "symbol": sym}))
                
                while dom_monitor_active:
                    try:
                        data_bytes = await ws.recv()
                        msg = msgpack.unpackb(data_bytes, raw=False)
                        
                        if isinstance(msg, dict) and msg.get("type") == "book":
                            s = msg.get("s", "UNKNOWN")
                            bids = msg.get("bids", [])
                            asks = msg.get("asks", [])
                            
                            print(f"\n--- DOM Book Update for {s} ---")
                            print(f"{'ASK SIZE':<12} | {'PRICE':<12} | {'BID SIZE':<12}")
                            print("-" * 45)
                            # Asks (descending price, so top of book is highest ask)
                            sorted_asks = sorted(asks, key=lambda x: x.get("price", 0.0), reverse=True)
                            for ask in sorted_asks[:5]:
                                print(f"{ask.get('volume', 0.0):<12.2f} | {ask.get('price', 0.0):<12.5f} |")
                            print("-" * 45)
                            # Bids (descending price, so top of book is highest bid)
                            sorted_bids = sorted(bids, key=lambda x: x.get("price", 0.0), reverse=True)
                            for bid in sorted_bids[:5]:
                                print(f"{'':<12} | {bid.get('price', 0.0):<12.5f} | {bid.get('volume', 0.0):<12.2f}")
                            print("=" * 45)
                    except websockets.ConnectionClosed:
                        print("\n[WS] Connection closed. Reconnecting...")
                        break
                    except Exception as e:
                        print(f"\n[WS] Error processing frame: {e}")
                        break
        except Exception as e:
            print(f"\n[WS] Could not connect to WebSocket: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

def run_ws_dom_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws_dom_receiver())

def start_dom_monitor():
    global dom_monitor_active
    if not subscribed_symbols:
        print("\n[WARNING] Please subscribe to at least one symbol first!")
        return
    
    print_header("Starting Real-time DOM Monitoring")
    print("Press ENTER to return to menu and stop DOM display.")
    print("-" * 50)
    
    dom_monitor_active = True
    ws_thread = threading.Thread(target=run_ws_dom_loop, daemon=True)
    ws_thread.start()
    
    input()
    dom_monitor_active = False
    print("\nDOM monitor stopped.")

def get_open_positions():
    print_header("Open Positions (Active Trades)")
    code, data = http_get(f"{REST_URL}/api/v1/positions")
    if code == 200 and isinstance(data, dict):
        positions = data.get("data", [])
        if not positions:
            print("No open positions found.")
            return
        print(f"Total open positions: {len(positions)}\n")
        print(f"{'TICKET':<12}{'SYMBOL':<10}{'TYPE':<8}{'VOLUME':<8}{'OPEN':<10}{'CURRENT':<10}{'PROFIT':<10}")
        print("-" * 75)
        for p in positions:
            ticket = p.get("ticket", "N/A")
            symbol = p.get("symbol", "N/A")
            ptype = p.get("type", "N/A")
            vol = p.get("volume", 0.0)
            open_price = p.get("price_open", 0.0)
            curr_price = p.get("price_current", 0.0)
            profit = p.get("profit", 0.0)
            print(f"{ticket:<12}{symbol:<10}{ptype:<8}{vol:<8.2f}{open_price:<10.5f}{curr_price:<10.5f}{profit:<10.2f}")
    else:
        print(f"Failed to fetch positions (code {code}): {data}")

def get_closed_deals():
    print_header("Closed Deals (Historical Trades)")
    code, data = http_get(f"{REST_URL}/api/v1/history-deals")
    if code == 200 and isinstance(data, dict):
        deals = data.get("data", [])
        if not deals:
            print("No historical deals found.")
            return
        print(f"Total historical deals: {len(deals)}\n")
        print(f"{'TICKET':<12}{'SYMBOL':<10}{'TYPE':<8}{'ENTRY':<8}{'VOLUME':<8}{'PRICE':<10}{'PROFIT':<10}")
        print("-" * 75)
        for d in deals:
            ticket = d.get("ticket", "N/A")
            symbol = d.get("symbol", "N/A")
            dtype = d.get("type", "N/A")
            entry = "IN" if d.get("entry") == 0 else "OUT" if d.get("entry") == 1 else str(d.get("entry"))
            vol = d.get("volume", 0.0)
            price = d.get("price", 0.0)
            profit = d.get("profit", 0.0)
            print(f"{ticket:<12}{symbol:<10}{dtype:<8}{entry:<8}{vol:<8.2f}{price:<10.5f}{profit:<10.2f}")
    else:
        print(f"Failed to fetch historical deals (code {code}): {data}")

def main_menu():
    while True:
        status, login = get_status()
        
        print("\n" + "=" * 50)
        print("          MT5 BROKER CLIENT DASHBOARD          ")
        print("=" * 50)
        print(f" Trade-Server Status: {status.upper()}")
        print(f" Active Account:      {login}")
        print(f" Local Subscriptions: {', '.join(subscribed_symbols) if subscribed_symbols else 'None'}")
        print("=" * 50)
        print("  1. Login to MT5 Broker")
        print("  2. Disconnect Broker")
        print("  3. List All Available Broker Symbols")
        print("  4. Subscribe to a Symbol")
        print("  5. View Active Subscriptions")
        print("  6. Start Live Tick Monitoring")
        print("  7. Start Live DOM (Depth of Market) Monitoring")
        print("  8. Get Open Positions (Active Trades)")
        print("  9. Get Closed Deals (Historical Trades)")
        print("  10. Refresh Status")
        print("  11. Exit")
        print("=" * 50)
        
        choice = input("Enter choice (1-11): ").strip()
        
        if choice == "1":
            connect_broker()
        elif choice == "2":
            disconnect_broker()
        elif choice == "3":
            list_all_symbols()
        elif choice == "4":
            subscribe_symbol()
        elif choice == "5":
            list_subscribed()
        elif choice == "6":
            start_tick_monitor()
        elif choice == "7":
            start_dom_monitor()
        elif choice == "8":
            get_open_positions()
        elif choice == "9":
            get_closed_deals()
        elif choice == "10":
            continue
        elif choice == "11":
            print("\nExiting dashboard. Goodbye!")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice. Please select 1-11.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting dashboard.")
