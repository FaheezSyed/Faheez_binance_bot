# src/market_orders.py
import os
import argparse
from decimal import Decimal
from basic_bot import BasicBot
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

bot = BasicBot(API_KEY, API_SECRET, testnet=True)


if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description="Place market buy/sell orders on Binance Futures.")
    parser.add_argument("symbol", type=str, help="Trading pair symbol (e.g., BTCUSDT)")
    parser.add_argument("qty", type=Decimal, help="Order quantity")
    args = parser.parse_args()

    symbol = args.symbol.upper()
    qty = args.qty

    # 1) Get price
    print("Price:", bot.get_price(symbol))

    # 2) Place market buy
    res = bot.place_market_order(symbol=symbol, side="BUY", quantity=qty)
    print("Market buy:", res)

    # 3) Place market sell (reduce only)
    res2 = bot.place_market_order(symbol=symbol, side="SELL", quantity=qty, reduceOnly=True)
    print("Market sell (reduce):", res2)
