# 📈 Algo Trading Tools
A FastAPI–powered toolkit for retrieving, analyzing, and predicting stock and crypto data.  
Includes endpoints for ticker data, news, screeners, time-series prediction, image-based pattern recognition, and backtesting strategies.

## 🧩 Project Structure
```text
.
├── app.py               # FastAPI server exposing all endpoints
├── DataManagement.py    # Fetches & processes stock data (Binance, yfinance)
├── ImageAnalysis.py     # YOLOv8-based pattern & movement classification
├── Prediction.py        # Time-series prediction models
├── Screener.py          # Stock screener (gainers, losers, etc.)
└── Strategies.py        # Backtesting & optimization of trading strategies
```

## 🚀 Endpoints & Parameter Reference
For each endpoint, see the parameter tables below, plus example URLs and placeholders for sample JSON/image responses.

### 1. `GET /get-ticker-data`
Fetch stock or crypto OHLCV data.

| Parameter | Type   | Allowed Values                                                       | Description                                                                                     |
|-----------|--------|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `ticker`  | string | Any valid ticker (e.g. `AAPL`, `BTCUSDT`). For NSE/BSE append `.NS`/`.BO`. | Ticker symbol. Use crypto symbols only with `api=binance`.                                       |
| `interval`| string | `1min`, `5min`, `1hr`, `1day`, `1week`, `1mon`                        | Data interval/frequency.                                                                        |
| `api`     | string | `yfinance`, `binance`                                                | Data source API.                                                                                |

**Example URLs:**
```bash
# NSE stock (yfinance)
localhost:2000/get-ticker-data?ticker=ITC.NS&interval=5min&api=yfinance

# BSE stock (yfinance)
localhost:2000/get-ticker-data?ticker=ITC.BO&interval=1week&api=yfinance

# Crypto (binance)
localhost:2000/get-ticker-data?ticker=BTCUSDT&interval=1min&api=binance
```

<details>
<summary>Sample JSON Response</summary>
```json
```
</details>

### 2. `GET /get-news-data`
Scrapes and returns news items.

| Parameter    | Type   | Allowed Values                               | Description                     |
|--------------|--------|----------------------------------------------|---------------------------------|
| `news_type`  | string | `last24h`, `worldnews`, `indianews`, `stocknews`, `iponews`, `cryptonews` | Category or timeframe of news. |

**Example URL:**
```bash
# Last 24 Hour News
localhost:2000/get-news-data?news_type=last24h
```

<details>
<summary>Sample JSON Response</summary>
```json
```
</details>

### 3. `GET /get-stock-screener`
Uses yfinance to screen stocks based on predefined criteria.

| Parameter         | Type   | Allowed Values                                                                          | Description                         |
|-------------------|--------|-----------------------------------------------------------------------------------------|-------------------------------------|
| `screener_type`   | string | `daygainers`, `daylosers`, `undervaluedsmallcap`, `undervaluedlargecap`, `technologysector`, `energysector`, `healthsector`, `estatesector`, `industrialsector` | Screening criteria or sector filter.|

**Example URLs:**
```bash
# Undervalued small-cap stocks
localhost:2000/get-stock-screener?screener_type=undervaluedsmallcap

# All health sector stocks
localhost:2000/get-stock-screener?screener_type=healthsector
```

<details>
<summary>Sample JSON Response</summary>
```json
```
</details>

### 4. `GET /stock-prediction`
Forecast future price via time-series models.

| Parameter    | Type    | Allowed Values                         | Description                                                                           |
|--------------|---------|----------------------------------------|---------------------------------------------------------------------------------------|
| `predictor`  | string  | `fbprophet`, `arima`, `sarima`, `sarimax` | Time-series model to use.                                                             |
| `ticker`     | string  | Same as `/get-ticker-data`             | Ticker symbol.                                                                        |
| `interval`   | string  | Same as `/get-ticker-data`             | Data interval.                                                                        |
| `api`        | string  | Same as `/get-ticker-data`             | Data source API.                                                                      |
| `days_ahead` | integer | `1–365`                                | Number of days into the future to forecast.                                           |

**Example URL:**
```bash
# Stock Prediction using Sarimax Model
localhost:2000/stock-prediction?predictor=sarimax&ticker=ITC.NS&interval=5min&api=yfinance&days_ahead=30
```

<details>
<summary>Sample JSON Response</summary>
```json
```
</details>

### 5. `GET /backtest`
Backtests trading strategies and optimizes for returns or win rate.

| Parameter  | Type   | Allowed Values                                                                                                                  | Description                                      |
|------------|--------|---------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| `ticker`   | string | Same as `/get-ticker-data`                                                                                                      | Ticker symbol.                                   |
| `interval` | string | Same as `/get-ticker-data`                                                                                                      | Data interval.                                   |
| `api`      | string | Same as `/get-ticker-data`                                                                                                      | Data source API.                                 |
| `s_name`   | string | `SmaCross`, `RsiEmaCross`, `MACDEmaCrossover`, `BollingerBandBreakout`, `SMATrendFollowing`, `StochasticCrossover`               | Strategy name for backtesting/optimization.      |

**Example URL:**
```bash
# Backtesting a Stock on SmaCross Strategy
localhost:2000/backtest?ticker=ITC.NS&interval=1day&api=yfinance&s_name=SmaCross
```

<details>
<summary>Sample JSON Response Template</summary>
```json
```
</details>

### 6. Image-Based Analysis

#### a. Movement Classification
```
GET /image-analysis/movement-classify
```
| Parameter  | Type   | Allowed Values                  | Description                        |
|------------|--------|---------------------------------|------------------------------------|
| `ticker`   | string | Same as `/get-ticker-data`      | Ticker symbol.                     |
| `interval` | string | Same as `/get-ticker-data`      | Data interval.                     |
| `api`      | string | Same as `/get-ticker-data`      | Data source API.                   |

**Example URL:**
```bash
localhost:2000/image-analysis/movement-classify?ticker=ITC.NS&interval=1hr&api=yfinance
```

<details>
<summary>Sample Image Response</summary>
</details>

#### b. Pattern Classification
```
GET /image-analysis/pattern-classify
```
| Parameter  | Type   | Allowed Values                  | Description                        |
|------------|--------|---------------------------------|------------------------------------|
| `ticker`   | string | Same as `/get-ticker-data`      | Ticker symbol.                     |
| `interval` | string | Same as `/get-ticker-data`      | Data interval.                     |
| `api`      | string | Same as `/get-ticker-data`      | Data source API.                   |

**Example URL:**
```bash
localhost:2000/image-analysis/pattern-classify?ticker=ITC.NS&interval=1hr&api=yfinance
```

<details>
<summary>Sample Image Response</summary>
</details>

## 🔧 Installation
1. Clone the repo  
   ```bash
   git clone https://github.com/suprezg/AlgoTradingTools.git
   cd stock-analysis-tools
   ```
2. Create & activate a virtualenv  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

## 🏁 Quick Start

```bash
python app.py
```
Then use your browser, `curl`, or Postman at `http://localhost:2000`.

## 📄 License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
