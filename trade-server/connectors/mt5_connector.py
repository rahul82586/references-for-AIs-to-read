try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

import logging
import threading
import multiprocessing
import time
import os
import json
import queue
from datetime import datetime
from typing import Dict, List, Any, Optional

from connectors.base_connector import BaseConnector
from core.event_bus import bus
from core.events import EVT_MARKET_UPDATE, EVT_STATUS_LOG

logger = logging.getLogger(__name__)

# IPC Protocol Commands
CMD_CONNECT = "CONNECT"
CMD_DISCONNECT = "DISCONNECT"
CMD_SUBSCRIBE = "SUBSCRIBE"
CMD_UNSUBSCRIBE = "UNSUBSCRIBE"
CMD_SUBSCRIBE_BOOK = "SUBSCRIBE_BOOK"
CMD_UNSUBSCRIBE_BOOK = "UNSUBSCRIBE_BOOK"
CMD_PLACE_ORDER = "PLACE_ORDER"
CMD_CLOSE_POSITION = "CLOSE_POSITION"
CMD_GET_BALANCE = "GET_BALANCE"
CMD_GET_SYMBOLS = "GET_SYMBOLS"
CMD_GET_POSITIONS = "GET_POSITIONS"
CMD_GET_ORDERS = "GET_ORDERS"
CMD_CANCEL_ORDER = "CANCEL_ORDER"
CMD_GET_HISTORY = "GET_HISTORY"
CMD_GET_HISTORY_DEALS = "GET_HISTORY_DEALS"
CMD_MODIFY_POSITION = "MODIFY_POSITION"
CMD_STOP = "STOP"

# IPC Protocol Updates
UP_TICK = "TICK"
UP_STATUS = "STATUS"
UP_ERROR = "ERROR"
UP_ORDER_RESULT = "ORDER_RESULT"
UP_BALANCE = "BALANCE"
UP_SYMBOLS = "SYMBOLS"
UP_POSITIONS = "POSITIONS"
UP_ORDERS = "ORDERS"
UP_HISTORY = "HISTORY"
UP_HISTORY_DEALS = "HISTORY_DEALS"
UP_BOOK = "BOOK"

class MT5Worker(multiprocessing.Process):
    """
    Dedicated process for a single MT5 terminal instance.
    Solves the global state conflict in the MT5 Python library.
    """
    def __init__(self, instance_id: str, path: str, login: int, password: str, server: str, 
                 cmd_queue: multiprocessing.Queue, res_queue: multiprocessing.Queue):
        super().__init__(name=f"MT5Worker-{instance_id}", daemon=True)
        self.instance_id = instance_id
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self.cmd_queue = cmd_queue
        self.res_queue = res_queue
        
        self._is_running = True
        self._is_connected = False
        self._active_symbols = set()
        self._active_book_symbols = set()

    def run(self):
        """Worker process entry point."""
        logging.getLogger().setLevel(logging.WARNING)
        print(f"MT5Worker[{self.instance_id}] started (PID: {os.getpid()})")
        
        if not MT5_AVAILABLE:
            self.res_queue.put({"type": UP_ERROR, "message": "MetaTrader5 package not installed"})
            return

        while self._is_running:
            try:
                # 1. Process Commands (non-blocking)
                while not self.cmd_queue.empty():
                    cmd = self.cmd_queue.get(block=False)
                    self._handle_command(cmd)

                # 2. Polling Loop for Ticks (if connected)
                if self._is_connected and self._active_symbols:
                    self._poll_ticks()

                # 3. Polling Loop for DOM Books (if connected)
                if self._is_connected and self._active_book_symbols:
                    self._poll_books()

                time.sleep(0.05) # 50ms loop

            except Exception as e:
                logger.error(f"MT5Worker[{self.instance_id}] loop error: {e}")
                self.res_queue.put({"type": UP_ERROR, "message": f"Worker loop error: {e}"})
                time.sleep(1.0)

        # Cleanup on exit
        if self._is_connected:
            mt5.shutdown()
        logger.info(f"MT5Worker[{self.instance_id}] exiting")

    def _handle_command(self, cmd: dict):
        ctype = cmd.get("type")
        logger.info(f"MT5Worker[{self.instance_id}] received command: {ctype}")
        
        if ctype == CMD_CONNECT:
            self._connect()
        elif ctype == CMD_DISCONNECT:
            self._disconnect()
        elif ctype == CMD_SUBSCRIBE:
            symbol = cmd.get("symbol")
            if symbol:
                selected = mt5.symbol_select(symbol, True)
                if not selected:
                    err = mt5.last_error()
                    logger.warning(f"MT5Worker[{self.instance_id}] FAILED to select symbol {symbol}. last_error: {err}")
                else:
                    self._active_symbols.add(symbol)
                    logger.info(f"MT5Worker[{self.instance_id}]: Subscribed to {symbol}")
        elif ctype == CMD_UNSUBSCRIBE:
            symbol = cmd.get("symbol")
            if symbol in self._active_symbols:
                self._active_symbols.remove(symbol)
        elif ctype == CMD_SUBSCRIBE_BOOK:
            symbol = cmd.get("symbol")
            if symbol:
                selected = mt5.symbol_select(symbol, True)
                if not selected:
                    err = mt5.last_error()
                    logger.warning(f"MT5Worker[{self.instance_id}] FAILED to select symbol {symbol} for DOM book. last_error: {err}")
                ok = mt5.market_book_add(symbol)
                if ok:
                    self._active_book_symbols.add(symbol)
                    logger.info(f"MT5Worker[{self.instance_id}]: Subscribed to DOM book for {symbol}")
                else:
                    err = mt5.last_error()
                    logger.warning(f"MT5Worker[{self.instance_id}] market_book_add({symbol}) failed. last_error: {err}")
        elif ctype == CMD_UNSUBSCRIBE_BOOK:
            symbol = cmd.get("symbol")
            if symbol in self._active_book_symbols:
                mt5.market_book_release(symbol)
                self._active_book_symbols.remove(symbol)
                logger.info(f"MT5Worker[{self.instance_id}]: Unsubscribed DOM book for {symbol}")
        elif ctype == CMD_GET_BALANCE:
            self._get_balance()
        elif ctype == CMD_GET_SYMBOLS:
            self._get_symbols()
        elif ctype == CMD_GET_POSITIONS:
            self._get_positions()
        elif ctype == CMD_GET_ORDERS:
            self._get_orders()
        elif ctype == CMD_CANCEL_ORDER:
            self._cancel_order(cmd)
        elif ctype == CMD_GET_HISTORY:
            self._get_history(cmd)
        elif ctype == CMD_GET_HISTORY_DEALS:
            self._get_history_deals(cmd)
        elif ctype == CMD_PLACE_ORDER:
            self._place_order(cmd)
        elif ctype == CMD_CLOSE_POSITION:
            self._close_position(cmd)
        elif ctype == CMD_MODIFY_POSITION:
            self._modify_position(cmd)
        elif ctype == CMD_STOP:
            self._is_running = False

    def _connect(self):
        kwargs = {"path": self.path} if self.path else {}
        if self.login:
            kwargs.update({
                "login": self.login,
                "password": self.password,
                "server": self.server
            })
        
        ok = mt5.initialize(**kwargs)
        if ok:
            self._is_connected = True
            logger.info(f"MT5Worker[{self.instance_id}] Connected to {self.login}")
            
            # Calibrate broker timezone offset dynamically using active live symbols
            broker_tz_offset = 0
            symbols = mt5.symbols_get()
            if symbols:
                current_utc = time.time()
                # Find active/selected symbols in the terminal
                candidates = [s.name for s in symbols if s.select]
                
                # Fallback to checking first 150 symbols in the directory if none are selected
                if not candidates:
                    candidates = [s.name for s in symbols[:150]]
                
                latest_tick_time = 0
                for sym_name in candidates:
                    mt5.symbol_select(sym_name, True)
                    tick = mt5.symbol_info_tick(sym_name)
                    if tick and tick.time > 0:
                        if tick.time > latest_tick_time:
                            latest_tick_time = tick.time
                
                found_live = False
                if latest_tick_time > 0:
                    offset = float(latest_tick_time) - current_utc
                    temp_tz = int(round(offset / 1800.0) * 1800)
                    age = abs(offset - temp_tz)
                    if age < 300 and -43200 <= temp_tz <= 50400:
                        broker_tz_offset = temp_tz
                        found_live = True
                        logger.info(f"MT5Worker[{self.instance_id}] Dynamically calibrated timezone offset: {broker_tz_offset}s ({broker_tz_offset/3600.0}h) using tick with age {age}s")
                
                # Fallback to EET/EEST (UTC+3 summer / UTC+2 winter) if no live symbols are found (e.g. weekend closed Forex)
                if not found_live:
                    is_dst = time.localtime().tm_isdst > 0
                    broker_tz_offset = 10800 if is_dst else 7200  # UTC+3 or UTC+2
                    logger.info(f"MT5Worker[{self.instance_id}] Calibration tick was stale or not found. Defaulting to EET/EEST offset: {broker_tz_offset}s")
            
            self.res_queue.put({
                "type": UP_STATUS, 
                "connected": True, 
                "message": f"Connected to {self.login}",
                "broker_tz_offset": broker_tz_offset
            })
        else:
            err = mt5.last_error()
            self.res_queue.put({"type": UP_ERROR, "message": f"Init failed: {err}"})

    def _disconnect(self):
        mt5.shutdown()
        self._is_connected = False
        self.res_queue.put({"type": UP_STATUS, "connected": False})

    def _poll_ticks(self):
        for symbol in list(self._active_symbols):
            try:
                if not self._is_connected:
                    break
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    self.res_queue.put({
                        "type": UP_TICK,
                        "symbol": symbol,
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "last": tick.last,
                        "time": tick.time
                    }, block=False)
                else:
                    err = mt5.last_error()
                    logger.warning(f"MT5Worker[{self.instance_id}] symbol_info_tick({symbol}) returned None. last_error: {err}")
                    if isinstance(err, tuple) and len(err) > 0 and err[0] == -10001:
                        logger.error(f"MT5Worker[{self.instance_id}] Fatal IPC error in tick poll. Disconnecting...")
                        self._is_connected = False
                        self.res_queue.put({
                            "type": UP_STATUS,
                            "connected": False,
                            "message": "MT5 terminal disconnected: IPC send failed"
                        })
                        break
            except queue.Full:
                pass
            except Exception as e:
                logger.error(f"MT5Worker[{self.instance_id}] error polling {symbol}: {e}")

    def _poll_books(self):
        for symbol in list(self._active_book_symbols):
            try:
                if not self._is_connected:
                    break
                book = mt5.market_book_get(symbol)
                if book is not None:
                    bids = []
                    asks = []
                    for level in book:
                        price = float(level.price)
                        vol = float(level.volume_real if hasattr(level, "volume_real") else level.volume)
                        if level.type in (1, 3):
                            asks.append({"price": price, "volume": vol})
                        else:
                            bids.append({"price": price, "volume": vol})
                    
                    self.res_queue.put({
                        "type": UP_BOOK,
                        "symbol": symbol,
                        "bids": bids,
                        "asks": asks
                    }, block=False)
                else:
                    err = mt5.last_error()
                    logger.warning(f"MT5Worker[{self.instance_id}] market_book_get({symbol}) returned None. last_error: {err}")
                    if isinstance(err, tuple) and len(err) > 0 and err[0] == -10001:
                        logger.error(f"MT5Worker[{self.instance_id}] Fatal IPC error in book poll. Disconnecting...")
                        self._is_connected = False
                        self.res_queue.put({
                            "type": UP_STATUS,
                            "connected": False,
                            "message": "MT5 terminal disconnected: IPC send failed"
                        })
                        break
            except queue.Full:
                pass
            except Exception as e:
                logger.error(f"MT5Worker[{self.instance_id}] error polling book for {symbol}: {e}")

    def _get_balance(self):
        info = mt5.account_info()
        if info:
            self.res_queue.put({
                "type": UP_BALANCE,
                "data": {
                    "balance": info.balance,
                    "equity": info.equity,
                    "margin": info.margin,
                    "free_margin": info.margin_free
                }
            })

    def _get_symbols(self):
        symbols = mt5.symbols_get()
        if symbols:
            calc_mode_map = {
                0: "Forex",
                1: "Futures",
                2: "CFD",
                3: "CFD Index",
                4: "CFD Leverage",
                32: "Exchange Shares",
                33: "Exchange Futures",
                34: "Exchange CFD",
                35: "Exchange Options",
                36: "Exchange Options Margin",
                37: "Exchange Bonds"
            }
            trade_mode_map = {
                0: "Disabled",
                1: "Long Only",
                2: "Short Only",
                3: "Close Only",
                4: "Full Access"
            }
            
            symbols_list = []
            for s in symbols:
                calc_val = calc_mode_map.get(s.trade_calc_mode, f"Other ({s.trade_calc_mode})")
                trade_val = trade_mode_map.get(s.trade_mode, f"Other ({s.trade_mode})")
                
                symbols_list.append({
                    "name": s.name,
                    "digits": s.digits,
                    "description": s.description,
                    "selected": bool(s.select),
                    "path": getattr(s, "path", s.name),
                    "contract_size": getattr(s, "trade_contract_size", 100000.0),
                    "spread": getattr(s, "spread", 0),
                    "stops_level": getattr(s, "trade_stops_level", 0),
                    "margin_currency": getattr(s, "currency_margin", "USD"),
                    "profit_currency": getattr(s, "currency_profit", "USD"),
                    "calc_mode": calc_val,
                    "trade_mode": trade_val,
                    "exchange": getattr(s, "exchange", "MT5"),
                    "sector": getattr(s, "sector", "Forex"),
                    "tick_size": getattr(s, "trade_tick_size", 0.00001),
                    "tick_value": getattr(s, "trade_tick_value", 1.0)
                })
            
            self.res_queue.put({
                "type": UP_SYMBOLS,
                "symbols": symbols_list
            })

    def _get_history(self, cmd: dict):
        symbol = cmd.get("symbol", "EURUSD")
        from_time = cmd.get("from_time", 0)
        to_time = cmd.get("to_time", int(time.time()))
        
        # Convert timestamps using local timezone to cancel out C-extension Windows time conversion
        dt_from = datetime.fromtimestamp(from_time)
        dt_to = datetime.fromtimestamp(to_time)
        
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, dt_from, dt_to)
        
        if rates is None or len(rates) == 0:
            # Fallback to last 10000 bars (approx. 7 days of M1 data) to cover weekends and avoid gaps
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10000)
            
        rates_list = []
        if rates is not None and len(rates) > 0:
            for r in rates:
                rates_list.append({
                    "t": int(r['time']),
                    "o": float(r['open']),
                    "h": float(r['high']),
                    "l": float(r['low']),
                    "c": float(r['close']),
                    "v": float(r['tick_volume'])
                })
        
        self.res_queue.put({
            "type": UP_HISTORY,
            "symbol": symbol,
            "data": rates_list
        })

    def _get_history_deals(self, cmd: dict):
        try:
            from_time = cmd.get("from_time", 0)
            # Clamp to a safe epoch (2020-01-01) to prevent OSError on Windows and broker sync timeout
            from_time = max(from_time, 1577836800)
            
            to_time = cmd.get("to_time", int(time.time()))
            
            # Convert timestamps using local timezone to cancel out C-extension Windows time conversion
            dt_from = datetime.fromtimestamp(from_time)
            dt_to = datetime.fromtimestamp(to_time)
            
            logger.info(f"MT5Worker[{self.instance_id}] Requesting history deals from {dt_from} to {dt_to}")
            deals = mt5.history_deals_get(dt_from, dt_to)
            deals_list = []
            if deals is not None and len(deals) > 0:
                 for d in deals:
                     deals_list.append({
                         "ticket": str(d.ticket),
                         "order": str(d.order),
                         "time": int(d.time),
                         "symbol": d.symbol,
                         "type": "buy" if d.type == 0 else "sell",
                         "entry": int(d.entry), # 0 = IN, 1 = OUT
                         "volume": float(d.volume),
                         "price": float(d.price),
                         "profit": float(d.profit),
                         "swap": float(d.swap),
                         "commission": float(d.commission),
                         "comment": str(d.comment)
                     })
            
            self.res_queue.put({
                "type": UP_HISTORY_DEALS,
                "data": deals_list
            })
        except Exception as e:
            logger.error(f"MT5Worker[{self.instance_id}] Error in _get_history_deals: {e}")
            self.res_queue.put({
                "type": UP_HISTORY_DEALS,
                "data": []
            })

    def _get_positions(self):
        positions = mt5.positions_get()
        positions_list = []
        if positions:
            for p in positions:
                positions_list.append({
                    "ticket": str(p.ticket),
                    "symbol": p.symbol,
                    "type": "buy" if p.type == 0 else "sell",
                    "volume": p.volume,
                    "price_open": p.price_open,
                    "price_current": p.price_current,
                    "profit": p.profit,
                    "swap": p.swap,
                    "comment": p.comment,
                    "sl": p.sl,
                    "tp": p.tp
                })
        
        self.res_queue.put({
            "type": UP_POSITIONS,
            "data": positions_list
        })

    def _get_orders(self):
        orders = mt5.orders_get()
        orders_list = []
        if orders:
            for o in orders:
                type_str = "buy"
                if o.type == 0: type_str = "buy"
                elif o.type == 1: type_str = "sell"
                elif o.type == 2: type_str = "buy_limit"
                elif o.type == 3: type_str = "sell_limit"
                elif o.type == 4: type_str = "buy_stop"
                elif o.type == 5: type_str = "sell_stop"
                
                orders_list.append({
                    "ticket": str(o.ticket),
                    "symbol": o.symbol,
                    "type": type_str,
                    "volume": float(o.volume_current),
                    "price": float(o.price_open),
                    "sl": float(o.sl),
                    "tp": float(o.tp)
                })
        
        self.res_queue.put({
            "type": UP_ORDERS,
            "data": orders_list
        })

    def _cancel_order(self, cmd: dict):
        ticket = cmd.get("ticket")
        try:
            ticket_int = int(ticket)
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket_int
            }
            logger.info(f"MT5Worker[{self.instance_id}] removing pending order ticket={ticket_int}")
            result = mt5.order_send(request)
            if result is None:
                err = mt5.last_error()
                self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": f"Internal Error: {err}"})
            elif result.retcode not in (mt5.TRADE_RETCODE_DONE, 10008):
                self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": f"{result.comment} ({result.retcode})"})
            else:
                self.res_queue.put({"type": UP_ORDER_RESULT, "success": True, "ticket": ticket_int, "action": "cancel"})
        except Exception as e:
            logger.error(f"MT5Worker[{self.instance_id}] Error cancelling order {ticket}: {e}")
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": str(e)})

    def _place_order(self, cmd: dict):
        symbol = cmd.get("symbol")
        side = cmd.get("side", "").lower()
        volume = float(cmd.get("volume", 0))
        price = cmd.get("price")
        
        type_filling = cmd.get("type_filling", "FOK")
        if type_filling == "IOC":
            filling_mode = mt5.ORDER_FILLING_IOC
        elif type_filling == "RETURN":
            filling_mode = mt5.ORDER_FILLING_RETURN
        else:
            filling_mode = mt5.ORDER_FILLING_FOK
        
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": f"No tick data for {symbol}"})
            return
            
        if price and float(price) > 0:
            # Pending Order
            action = mt5.TRADE_ACTION_PENDING
            trade_price = float(price)
            if side == "buy":
                mt5_type = mt5.ORDER_TYPE_BUY_LIMIT if trade_price < tick.ask else mt5.ORDER_TYPE_BUY_STOP
            else:
                mt5_type = mt5.ORDER_TYPE_SELL_LIMIT if trade_price > tick.bid else mt5.ORDER_TYPE_SELL_STOP
        else:
            # Market Order
            action = mt5.TRADE_ACTION_DEAL
            mt5_type = mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL
            trade_price = tick.ask if side == "buy" else tick.bid
            
        request = {
            "action": action,
            "symbol": symbol,
            "volume": volume,
            "type": mt5_type,
            "price": float(trade_price),
            "deviation": 20,
            "magic": 1001,
            "comment": "trade-server",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        if cmd.get("sl"):
            request["sl"] = float(cmd.get("sl"))
        if cmd.get("tp"):
            request["tp"] = float(cmd.get("tp"))
            
        logger.info(f"MT5Worker[{self.instance_id}] sending order request: {json.dumps(request)}")
        result = mt5.order_send(request)
        
        if result is None:
            err = mt5.last_error()
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": f"Internal Error (None): {err}"})
            return
            
        if result.retcode not in (mt5.TRADE_RETCODE_DONE, 10008):
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": f"{result.comment} ({result.retcode})"})
            return
            
        self.res_queue.put({
            "type": UP_ORDER_RESULT,
            "success": True,
            "ticket": result.order,
            "price": result.price,
            "volume": result.volume,
            "side": side
        })

    def _close_position(self, cmd: dict):
        symbol = cmd.get("symbol")
        ticket = cmd.get("ticket")
        volume = float(cmd.get("volume", 0))
        
        candidate_pos = None
        if not ticket or str(ticket) in ("0", "N/A", "None", ""):
            positions = mt5.positions_get(symbol=symbol)
            if positions:
                candidate_pos = positions[0]
                ticket = candidate_pos.ticket
        else:
            try:
                ticket_int = int(ticket)
                posts = mt5.positions_get(ticket=ticket_int)
                if posts:
                    candidate_pos = posts[0]
            except (ValueError, TypeError):
                pass
        
        if not candidate_pos:
            err_msg = f"Position not found for {symbol} (Ticket: {ticket})"
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": err_msg})
            return

        close_type = mt5.ORDER_TYPE_SELL if candidate_pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_vol = volume if volume > 0 else candidate_pos.volume
        
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": "No tick data for close"})
            return
            
        close_price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask
        side = "sell" if close_type == mt5.ORDER_TYPE_SELL else "buy"
        
        def create_req(filling_mode):
            return {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(close_vol),
                "type": close_type,
                "position": int(ticket),
                "price": float(close_price),
                "deviation": 20,
                "magic": 1001,
                "comment": "trade-server-close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }

        request = create_req(mt5.ORDER_FILLING_IOC)
        result = mt5.order_send(request)
        
        if result and result.retcode == 10030:
            request = create_req(mt5.ORDER_FILLING_RETURN)
            result = mt5.order_send(request)

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            err = result.comment if result else str(mt5.last_error())
            self.res_queue.put({"type": UP_ORDER_RESULT, "success": False, "error": err})
            return
            
        self.res_queue.put({
            "type": UP_ORDER_RESULT,
            "success": True,
            "ticket": result.order,
            "price": result.price,
            "volume": result.volume,
            "side": side
        })

class MT5Connector(BaseConnector):
    """
    Proxy class that manages a dedicated MT5Worker process.
    """
    display_name = "MetaTrader 5"
    connector_id = "mt5"
    
    required_params = {
        "path": {"label": "Terminal Path", "type": "string", "default": ""},
        "login": {"label": "Login", "type": "string", "default": ""},
        "password": {"label": "Password", "type": "password", "default": ""},
        "server": {"label": "Server", "type": "string", "default": ""}
    }

    def __init__(self, config: Dict[str, Any], tag: Optional[str] = None):
        super().__init__(config, tag)
        params = config.get("params", config)
        self.path = os.path.normpath(params.get("path", "")) if params.get("path") else ""
        try:
            self.login = int(params.get("login", 0))
        except ValueError:
            self.login = 0
        self.password = params.get("password", "")
        self.server = params.get("server", "")

        # IPC Queues
        self.cmd_queue = multiprocessing.Queue()
        self.res_queue = multiprocessing.Queue()
        self._order_result_queue = queue.Queue()
        self._positions_queue = queue.Queue()
        self._balance_queue = queue.Queue()
        self._history_queue = queue.Queue()
        self._history_deals_queue = queue.Queue()
        self._symbols_queue = queue.Queue()
        self._orders_queue = queue.Queue()
        self.worker: Optional[MT5Worker] = None
        self.last_error_msg: str = ""
        self.broker_tz_offset: Optional[float] = None
        
        self._res_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def status(self) -> str:
        if self.is_connected:
            return "connected"
        if self.worker and self.worker.is_alive():
            return "connecting"
        return "disconnected"

    def connect(self) -> bool:
        if self.worker and self.worker.is_alive():
            return True

        self.worker = MT5Worker(self.instance_id, self.path, self.login, self.password, self.server, 
                               self.cmd_queue, self.res_queue)
        self.worker.start()
        
        self._stop_event.clear()
        self._res_thread = threading.Thread(target=self._response_loop, daemon=True)
        self._res_thread.start()
        
        self.cmd_queue.put({"type": CMD_CONNECT})
        return True

    def disconnect(self):
        self._stop_event.set()
        if self.cmd_queue:
            self.cmd_queue.put({"type": CMD_STOP})
        if self.worker:
            self.worker.join(timeout=2.0)
            if self.worker.is_alive():
                self.worker.terminate()
        self.is_connected = False

    def _response_loop(self):
        while not self._stop_event.is_set():
            try:
                if not self.res_queue.empty():
                    res = self.res_queue.get(timeout=0.1)
                    self._handle_response(res)
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.error(f"MT5Proxy[{self.instance_id}] response error: {e}")

    def _handle_response(self, res: dict):
        rtype = res.get("type")
        if rtype == UP_TICK:
            if self.broker_tz_offset is None and float(res["time"]) > 0:
                offset = float(res["time"]) - time.time()
                temp_tz = round(offset / 1800.0) * 1800
                age = abs(offset - temp_tz)
                if age < 300 and -43200 <= temp_tz <= 50400:
                    self.broker_tz_offset = temp_tz
                    logger.info(f"MT5Proxy[{self.instance_id}] Dynamically calibrated timezone offset from live tick: {self.broker_tz_offset}s ({self.broker_tz_offset/3600.0}h) (age {age}s)")

            offset_val = self.broker_tz_offset or 0
            tick_obj = {
                "symbol": res["symbol"],
                "bid": float(res["bid"]),
                "ask": float(res["ask"]),
                "last": float(res["last"]),
                "timestamp": float(res["time"]) - offset_val,
                "connector_id": self.instance_id,
                "tag": self.tag
            }
            self._last_ticks[res["symbol"]] = tick_obj
            bus.publish(EVT_MARKET_UPDATE, tick_obj)
        elif rtype == UP_STATUS:
            self.is_connected = res.get("connected", False)
            if "broker_tz_offset" in res:
                self.broker_tz_offset = res["broker_tz_offset"]
                logger.info(f"MT5Proxy[{self.instance_id}] Established timezone offset from connect: {self.broker_tz_offset}s")
            if res.get("message"):
                bus.publish(EVT_STATUS_LOG, res["message"])
        elif rtype == UP_ERROR:
            self.last_error_msg = res['message']
            bus.publish(EVT_STATUS_LOG, f"Error: {res['message']}")
        elif rtype == UP_ORDER_RESULT:
            self._order_result_queue.put(res)
        elif rtype == UP_POSITIONS:
            self._positions_queue.put(res.get("data", []))
        elif rtype == UP_BALANCE:
            self._balance_queue.put(res.get("data", {}))
        elif rtype == UP_HISTORY:
            self._history_queue.put(res.get("data", []))
        elif rtype == UP_HISTORY_DEALS:
            self._history_deals_queue.put(res.get("data", []))
        elif rtype == UP_SYMBOLS:
            self._symbols_queue.put(res.get("symbols", []))
        elif rtype == UP_ORDERS:
            self._orders_queue.put(res.get("data", []))
        elif rtype == UP_BOOK:
            bus.publish("market_book_update", {
                "symbol": res["symbol"],
                "bids": res["bids"],
                "asks": res["asks"]
            })

    def subscribe_symbol(self, symbol: str):
        self.cmd_queue.put({"type": CMD_SUBSCRIBE, "symbol": symbol})

    def unsubscribe_symbol(self, symbol: str):
        self.cmd_queue.put({"type": CMD_UNSUBSCRIBE, "symbol": symbol})

    def get_symbol_list(self) -> List[Dict]:
        while not self._symbols_queue.empty():
            try: self._symbols_queue.get_nowait()
            except: pass

        self.cmd_queue.put({"type": CMD_GET_SYMBOLS})
        try:
            return self._symbols_queue.get(timeout=4.0)
        except queue.Empty:
            logger.warning(f"MT5Proxy[{self.instance_id}] Timeout waiting for symbol list")
            return []

    def get_balance(self) -> Dict[str, float]:
        self.cmd_queue.put({"type": CMD_GET_BALANCE})
        try:
            return self._balance_queue.get(timeout=4.0)
        except queue.Empty:
            return {}

    def get_positions(self) -> List[Dict[str, Any]]:
        self.cmd_queue.put({"type": CMD_GET_POSITIONS})
        try:
            res = self._positions_queue.get(timeout=5.0)
            return res
        except queue.Empty:
            return []

    def get_history(self, symbol: str, from_time: int, to_time: int) -> List[Dict[str, Any]]:
        offset_val = self.broker_tz_offset or 0
        from_time_broker = from_time + offset_val
        to_time_broker = to_time + offset_val

        self.cmd_queue.put({
            "type": CMD_GET_HISTORY,
            "symbol": symbol,
            "from_time": from_time_broker,
            "to_time": to_time_broker
        })
        try:
            raw_history = self._history_queue.get(timeout=6.0)
            aligned_history = []
            for bar in raw_history:
                aligned_history.append({
                    "t": bar["t"] - offset_val,
                    "o": bar["o"],
                    "h": bar["h"],
                    "l": bar["l"],
                    "c": bar["c"],
                    "v": bar["v"]
                })
            return aligned_history
        except queue.Empty:
            return []

    def get_history_deals(self, from_time: int, to_time: int) -> List[Dict[str, Any]]:
        offset_val = self.broker_tz_offset or 0
        from_time_broker = from_time + offset_val
        to_time_broker = to_time + offset_val

        self.cmd_queue.put({
            "type": CMD_GET_HISTORY_DEALS,
            "from_time": from_time_broker,
            "to_time": to_time_broker
        })
        try:
            raw_deals = self._history_deals_queue.get(timeout=6.0)
            aligned_deals = []
            for d in raw_deals:
                aligned_deals.append({
                    "ticket": d["ticket"],
                    "order": d["order"],
                    "time": d["time"] - offset_val,
                    "symbol": d["symbol"],
                    "type": d["type"],
                    "entry": d["entry"],
                    "volume": d["volume"],
                    "price": d["price"],
                    "profit": d["profit"],
                    "swap": d["swap"],
                    "commission": d["commission"],
                    "comment": d["comment"]
                })
            return aligned_deals
        except queue.Empty:
            return []

    def subscribe_book(self, symbol: str):
        self.cmd_queue.put({"type": CMD_SUBSCRIBE_BOOK, "symbol": symbol})

    def unsubscribe_book(self, symbol: str):
        self.cmd_queue.put({"type": CMD_UNSUBSCRIBE_BOOK, "symbol": symbol})

    def get_orders(self) -> List[Dict[str, Any]]:
        while not self._orders_queue.empty():
            try: self._orders_queue.get_nowait()
            except: pass
        self.cmd_queue.put({"type": CMD_GET_ORDERS})
        try:
            return self._orders_queue.get(timeout=4.0)
        except queue.Empty:
            return []

    def place_order(self, symbol: str, side: str, volume: float, price: Optional[float] = None, sl: Optional[float] = None, tp: Optional[float] = None, type_filling: Optional[str] = "FOK") -> Dict[str, Any]:
        self.cmd_queue.put({
            "type": CMD_PLACE_ORDER,
            "symbol": symbol,
            "side": side,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "type_filling": type_filling
        })
        try:
            return self._order_result_queue.get(timeout=6.0)
        except queue.Empty:
            return {"success": False, "error": "Order timeout in IPC"}

    def close_position(self, symbol: str, ticket: Any, volume: float, side: str) -> Dict[str, Any]:
        self.cmd_queue.put({
            "type": CMD_CLOSE_POSITION,
            "symbol": symbol,
            "ticket": ticket,
            "volume": volume,
            "side": side
        })
        try:
            return self._order_result_queue.get(timeout=6.0)
        except queue.Empty:
            return {"success": False, "error": "Close timeout in IPC"}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        self.cmd_queue.put({
            "type": CMD_CANCEL_ORDER,
            "ticket": order_id
        })
        try:
            return self._order_result_queue.get(timeout=6.0)
        except queue.Empty:
            return {"success": False, "error": "Cancel timeout in IPC"}
