import json
import pandas as pd
from backtesting import Backtest
from fastapi import FastAPI, Response, HTTPException

from Prediction import PREDICTORS
from Screener import StockScreener
from DataManagement import NewsScraper, StockScraper
from ImageAnalysis import MovementClassifier, PatternClassifier
from Strategies import STRATEGIES, STRATEGY_OPTIMIZATION, prepareData

app = FastAPI()

@app.get("/get-ticker-data")
def getStockData(ticker: str, interval: str, api: str):
    try:
        scraper = StockScraper(ticker=ticker, interval=interval, api=api)
        return scraper.getData()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-news-data")
def getNewsData(news_type: str):
    try:
        scraper = NewsScraper(news_type=news_type)
        scraper.scrapePages()
        scraper.parsePages()
        return scraper.getData()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-stock-screener")
def getStockScreener(screener_type: str):
    try:
        screener = StockScreener(screener_type=screener_type)
        return screener.getData()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-prediction")
def getStockPrediction(predictor: str, ticker: str, interval: str, api: str, days_ahead: int):
    try:
        if predictor not in PREDICTORS:
            raise HTTPException(status_code=404, detail="Predictor not found")
        model = PREDICTORS[predictor](ticker=ticker, interval=interval, api=api, days_ahead=days_ahead)
        model.train()
        model.forecast()
        return model.getData()
    except Exception as e:
        raise HTTPException(stattus_code=500, detail=str(e))

@app.get("/backtest")
def getBacktestResults(ticker: str, interval: str, api: str, s_name: str):
    try:
        if (s_name not in STRATEGIES) or (s_name not in STRATEGY_OPTIMIZATION):
            raise HTTPException(status_code=404, detail="Strategy not found")
        s_class = STRATEGIES[s_name]
        optimization_params = STRATEGY_OPTIMIZATION[s_name]
        scraper = StockScraper(ticker=ticker, interval=interval, api=api)
        df = pd.DataFrame(scraper.getData())
        df = df.rename_axis('Date')
        df.dropna(inplace=True)
        bt = Backtest(df, s_class, cash=10000000)
    
        results_best_returns = bt.optimize(
            **optimization_params["params"],
            maximize='Equity Final [$]',
            constraint=optimization_params.get("constraint", None),
            method='skopt')
        
        results_best_winrate = bt.optimize(
            **optimization_params["params"],
            maximize='Win Rate [%]',
            constraint=optimization_params.get("constraint", None),
            method='skopt')
        return prepareData(results_best_returns, results_best_winrate)
    except Exception as e:
        raise HTTPException(stattus_code=500, detail=str(e))

@app.get("/image-analysis/movement-classify")
def movementClassify(ticker: str, interval: str, api: str):
    try:
        model = MovementClassifier(ticker = ticker, interval = interval, api = api)
        model.train()
        model.classify()
        return Response(content=model.getContent(), media_type="image/png")
    except Exception as e:
        raise HTTPException(stattus_code=500, detail=str(e))

@app.get("/image-analysis/pattern-classify")
def patternClassify(ticker: str, interval: str, api: str):
    try:
        model = PatternClassifier(ticker = ticker, interval = interval, api = api)
        model.train()
        model.classify()
        return Response(content=model.getContent(), media_type="image/png")
    except Exception as e:
        raise HTTPException(stattus_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=2000)