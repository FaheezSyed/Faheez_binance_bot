# src/limit_orders.py
import os
import time
import argparse
import logging
from decimal import Decimal
from basic_bot import BasicBot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
bot = BasicBot(API_KEY, API_SECRET, testnet=True)

# Configure logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser(description="Place a limit order on Binance Futures.")
    parser.add_argument("symbol", type=str, help="Trading pair symbol (e.g., BTCUSDT)")
    parser.add_argument("qty", type=Decimal, help="Order quantity")
    parser.add_argument("--limit_price", type=Decimal, default=None, help="Limit price for the order (optional)")
    args = parser.parse_args()

    symbol = args.symbol.upper()
    qty = args.qty
    limit_price = args.limit_price

    # Get current market price
    price_resp = bot.get_price(symbol)
    if not price_resp["success"]:
        logging.error(f"Failed to get price for {symbol}: {price_resp}")
        raise SystemExit

    # Defensive check if Binance returns dict or list
    if isinstance(price_resp["data"], dict):
        current_price = float(price_resp["data"]["price"])
    else:
        current_price = float(price_resp["data"][0]["price"])

    # Calculate limit price if not provided
    if limit_price is None:
        limit_price = round(current_price * 1.01, 2)
        logging.info(f"No limit price provided. Calculated limit price: {limit_price}")

    logging.info(f"Current market price of {symbol}: {current_price}")
    logging.info(f"Placing limit SELL for {qty} {symbol} at {limit_price}")

    r = bot.place_limit_order(symbol=symbol, side="SELL", quantity=qty, price=limit_price)
    if r.get("success"):
        logging.info(f"Limit order placed successfully: {r}")
    else:
        logging.error(f"Failed to place limit order: {r}")

    # Wait and check open orders
    time.sleep(2)
    open_orders = bot.get_open_orders(symbol)
    logging.info(f"Open orders for {symbol}: {open_orders}")

    # Also print to console
    print(f"Current market price: {current_price}")
    print(f"Limit order response: {r}")
    print(f"Open orders: {open_orders}")
