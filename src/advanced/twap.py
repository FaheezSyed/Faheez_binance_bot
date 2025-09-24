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
logger = logging.getLogger("TWAP")
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s | TWAP | %(levelname)s | %(message)s")
if not logger.handlers:
    fh = logging.FileHandler("../bot.log")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

bot = BasicBot(API_KEY, API_SECRET, testnet=True)


def twap_execute(symbol: str, side: str, total_qty: float, slices: int, interval_seconds: int = 60):
    """
    Simple TWAP (Time Weighted Average Price).
    Splits total order into N slices and executes at intervals.
    """
    qty_per = round(total_qty / slices, 6)
    results = []

    logger.info(f"Starting TWAP | symbol={symbol}, side={side}, total_qty={total_qty}, slices={slices}, interval={interval_seconds}s")
    print(f"TWAP executing {total_qty} {symbol} in {slices} slices ({qty_per} each)...")

    for i in range(slices):
        logger.info(f"Placing TWAP slice {i+1}/{slices} | qty={qty_per}")
        print(f"Slice {i+1}/{slices}: placing {side} order for {qty_per}")
        r = bot.place_market_order(symbol=symbol, side=side.upper(), quantity=qty_per)
        if r["success"]:
            logger.info(f"TWAP slice {i+1} executed successfully | order={r['data']}")
        else:
            logger.error(f"TWAP slice {i+1} failed | error={r['error']}")
        results.append(r)
        time.sleep(interval_seconds)

    logger.info("TWAP execution completed.")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binance Futures TWAP strategy")
    parser.add_argument("symbol", type=str, help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument("quantity", type=float, help="Total quantity")
    parser.add_argument("slices", type=int, help="Number of slices")
    parser.add_argument("interval", type=int, help="Interval between slices (seconds)")

    args = parser.parse_args()

    res = twap_execute(args.symbol, args.side, args.quantity, args.slices, args.interval)
    print(res)
