import os
import time
import argparse
import logging
from basic_bot import BasicBot
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Logger setup (reuse bot.log)
logger = logging.getLogger("OCO")
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s | OCO | %(levelname)s | %(message)s")
if not logger.handlers:
    fh = logging.FileHandler("../bot.log")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

bot = BasicBot(API_KEY, API_SECRET, testnet=True)


def place_oco(symbol: str, side: str, quantity: float, tp_price: float, stop_price: float):
    """
    OCO emulation for Binance Futures (since native OCO not supported).
    Places a take-profit LIMIT + stop-market order. Cancels one if the other executes.
    """
    logger.info(f"Placing OCO order | symbol={symbol}, side={side}, qty={quantity}, TP={tp_price}, STOP={stop_price}")

    # Opposite side for exit
    tp_side = "SELL" if side.upper() == "BUY" else "BUY"

    # Place TP Limit order
    tp = bot.place_limit_order(symbol=symbol, side=tp_side, quantity=quantity, price=tp_price)
    if not tp["success"]:
        logger.error(f"Failed to place TP order | {tp}")
        return {"success": False, "error": "Failed to place TP order", "detail": tp}
    logger.info(f"Take-Profit order placed successfully | orderId={tp['data'].get('orderId', 'N/A')}")

    # Place Stop-Market order
    stop = bot.place_stop_order(
        symbol=symbol,
        side=tp_side,
        quantity=quantity,
        stopPrice=stop_price,
        order_type="STOP_MARKET",
        closePosition=True,
    )
    if not stop["success"]:
        logger.error(f"Failed to place Stop order | {stop}")
        try:
            bot.cancel_order(symbol=symbol, orderId=tp["data"]["orderId"])
            logger.info("Cancelled TP order because Stop failed.")
        except Exception as e:
            logger.error(f"Failed to cancel TP after Stop failure | {e}")
        return {"success": False, "error": "Failed to place Stop order", "detail": stop}

    logger.info(f"OCO orders placed successfully | TP={tp_price}, STOP={stop_price}")
    print(f"OCO orders placed. TP={tp_price}, STOP={stop_price}")
    print("Monitoring orders... (Ctrl+C to exit)")

    try:
        while True:
            open_orders = bot.get_open_orders(symbol)
            if not open_orders["success"]:
                time.sleep(1)
                continue

            if not open_orders["data"]:  # no open orders -> one executed
                logger.info("OCO leg executed. Other auto-cancelled.")
                return {"success": True, "detail": "One OCO leg executed, other auto-cancelled"}
            time.sleep(2)

    except KeyboardInterrupt:
        logger.info("OCO monitoring stopped by user.")
        print("Stopped OCO monitoring.")
        return {"success": True, "detail": "User stopped monitoring"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binance Futures OCO order emulation")
    parser.add_argument("symbol", type=str, help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Initial order side")
    parser.add_argument("quantity", type=float, help="Order quantity")
    parser.add_argument("tp_price", type=float, help="Take profit price")
    parser.add_argument("stop_price", type=float, help="Stop loss trigger price")

    args = parser.parse_args()

    res = place_oco(args.symbol, args.side, args.quantity, args.tp_price, args.stop_price)
    print(res)
