# src/basic_bot.py
import logging
import time
import os
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


class BasicBot:
    """Simplified Binance Futures testnet bot wrapper.

    Methods return dict: {"success": bool, "data": ..., "error": ...}
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, log_file: str = "bot.log"):
        # logging
        self.logger = logging.getLogger("BasicBot")
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(fmt)
            self.logger.addHandler(ch)
            fh = logging.FileHandler(log_file)
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)

        self.logger.info("Initializing Binance Client (testnet=%s)", testnet)
        # the python-binance Client takes testnet=True for test environments
        self.client = Client(api_key, api_secret, testnet=testnet)
        time.sleep(0.05)
        self.logger.info("Client initialized")

    def _log_api_call(self, method_name: str, params: dict, response: object = None, error: Exception = None):
        self.logger.debug("API Call -> %s | params=%s", method_name, params)
        if response is not None:
            self.logger.debug("API Response <- %s | len=%d", method_name, len(str(response)))
        if error is not None:
            self.logger.error("API Error <- %s | %s", method_name, repr(error))

    def _execute(self, fn, method_name: str, params: dict):
        try:
            resp = fn(**params) if params else fn()
            self._log_api_call(method_name, params, response=resp)
            return {"success": True, "data": resp}
        except (BinanceAPIException, BinanceRequestException, Exception) as e:
            self._log_api_call(method_name, params, error=e)
            return {"success": False, "error": str(e)}

    # Market helpers
    def get_price(self, symbol: str):
        return self._execute(
            self.client.futures_symbol_ticker,
            "futures_symbol_ticker",
            {"symbol": symbol}
        )

    def get_account(self):
        return self._execute(
            self.client.futures_account,
            "futures_account",
            {}
        )

    def get_balance(self):
        return self._execute(
            self.client.futures_account_balance,
            "futures_account_balance",
            {}
        )
    def get_open_orders(self, symbol: str = None):
        params = {"symbol": symbol} if symbol else {}
        return self._execute(self.client.futures_get_open_orders, "futures_get_open_orders", params)


    # Orders
    def place_market_order(self, symbol: str, side: str, quantity: float, reduceOnly: bool = False):
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "reduceOnly": reduceOnly,
        }
        return self._execute(self.client.futures_create_order, "futures_create_order(MARKET)", params)


    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        timeInForce: str = "GTC",
        reduceOnly: bool = False,
    ):
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": timeInForce,
            "quantity": quantity,
            "price": str(price),
            "reduceOnly": reduceOnly,
        }
        return self._execute(self.client.futures_create_order, "futures_create_order(LIMIT)", params)


    def place_stop_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stopPrice: float,
        order_type: str = "STOP_MARKET",
        price: float = None,
        closePosition: bool = False,
        reduceOnly: bool = False,
    ):
        # Supports STOP_MARKET / STOP (stop-limit) and TAKE_PROFIT variants
        if order_type in ("STOP_MARKET", "TAKE_PROFIT_MARKET"):
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "stopPrice": str(stopPrice),
                "closePosition": closePosition,
                "reduceOnly": reduceOnly,
            }
        elif order_type in ("STOP", "TAKE_PROFIT"):
            if price is None:
                return {"success": False, "error": "price required for stop-limit type"}
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "stopPrice": str(stopPrice),
                "price": str(price),
                "timeInForce": "GTC",
                "reduceOnly": reduceOnly,
            }
        else:
            return {"success": False, "error": f"Unsupported order_type: {order_type}"}

        return self._execute(self.client.futures_create_order, f"futures_create_order({order_type})", params)


    def cancel_order(self, symbol: str, orderId: int = None, origClientOrderId: str = None):
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        return self._execute(self.client.futures_cancel_order, "futures_cancel_order", params)

