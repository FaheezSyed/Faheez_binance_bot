# Binance Trading Bot

A Python-based automated trading bot for Binance Futures, supporting **market orders**, **limit orders**, **OCO orders**, and **TWAP execution**. This bot also includes logging for easier debugging and monitoring.

---

## Features

* **Market Orders**: Buy/sell instantly at the current market price.
* **Limit Orders**: Place orders at a specific price.
* **OCO Orders**: One-Cancels-Other orders for risk management.
* **TWAP Orders**: Time-Weighted Average Price execution to minimize market impact.
* **Logging**: Detailed runtime logs for tracking bot activity.

---

## Prerequisites

* Python 3.10+
* Binance Futures account
* API Key & Secret from Binance

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/binance_trading_bot.git
cd binance_trading_bot
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

3. Install required packages:

```bash
pip install python-binance python-dotenv
```

---

## Configuration

1. Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

---

## Usage

### Running the Bot

You can run the bot scripts directly with Python. Examples:

* **OCO Order**:

```bash
python src/advanced/oco.py BTCUSDT BUY 0.001 66000 63000
```

* **TWAP Order**:

```bash
python src/advanced/twap.py BTCUSDT BUY 0.003 3 10
```

* **Market Order**:

```bash
python src/market_orders.py BTCUSDT 0.001
```

* **Limit Order**:

```bash
python src/limit_orders.py BTCUSDT 0.001 --limit_price 107000
```



### Examples in Python

* **Place Market Order**:

```python
from market_orders import place_market_order
place_market_order(symbol="BTCUSDT", side="BUY", quantity=0.001)
```

* **Place Limit Order**:

```python
from limit_orders import place_limit_order
place_limit_order(symbol="BTCUSDT", side="SELL", price=107000, quantity=0.001)
```

* **Place OCO Order**:

```python
from advanced.oco import place_oco_order
place_oco_order(symbol="BTCUSDT", side="SELL", quantity=0.001, price=35000, stopPrice=34000, stopLimitPrice=33900)
```

* **Execute TWAP**:

```python
from advanced.twap import execute_twap
execute_twap(symbol="BTCUSDT", side="BUY", total_quantity=0.01, interval=60, slices=5)
```

---

## Logging

The bot generates logs in `bot.log` for:

* API calls
* Orders placed and filled
* Errors and exceptions

---

## Folder Structure

```
binance_trading_bot/
├── src/
│   ├── basic_bot.py
│   ├── market_orders.py
│   ├── limit_orders.py
│   └── advanced/
│       ├── oco.py
│       └── twap.py
├── bot.log
└── README.md
```


---

## Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves risk. Use at your own discretion.