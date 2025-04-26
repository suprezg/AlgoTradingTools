import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler

from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from DataManagement import StockScraper

class FbProphetPredictor:
    
    def __init__(self, ticker, interval, api, days_ahead):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.forecast_df = np.nan
            
            self.days_ahead = days_ahead
            
            self.fitted = np.nan
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing FbProphetPredictor") from e
    
    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.reset_index()
            # self.df = self.df.dropna()
            self.df[['ds','y']] = self.df[['Date', 'Close']]
            self.df['ds'] = self.df['ds'].dt.tz_localize(None)
            self.df.drop(['Date','Open','High','Low','Close','Volume'],axis=1,inplace=True)
        except Exception as e:
            raise Exception("Error preparing data in FbProphetPredictor") from e

    def train(self):
        try:
            self.fitted = Prophet(daily_seasonality=True)
            self.fitted.fit(self.df)
        except Exception as e:
            raise Exception("Error training Prophet model") from e

    def forecast(self):
        try:
            future = self.fitted.make_future_dataframe(self.days_ahead)
            forecast = self.fitted.predict(future)
            self.forecast_df = pd.DataFrame({
                'Date' : pd.to_datetime(forecast.ds[-self.days_ahead:]), 
                'Forecast' : forecast.yhat[-self.days_ahead:]
            })
        except Exception as e:
            raise Exception("Error forecasting with Prophet model") from e

    def getData(self):
        try:
            if self.forecast_df is None:
                raise Exception("No forecast data available. Ensure forecast() was run successfully.")
            return self.forecast_df.to_dict()
        except Exception as e:
            raise Exception("Error retrieving forecast data from FbProphetPredictor") from e


class ArimaPredictor:

    def __init__(self, ticker, interval, api, days_ahead):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.forecast_df = np.nan
            self.days_ahead = days_ahead
            self.fitted = np.nan
            
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing ArimaPredictor") from e

    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.asfreq('B').ffill()
            self.df = self.df['Close'].to_frame()
            # self.df = self.df.dropna()
        except Exception as e:
            raise Exception("Error preparing data in ArimaPredictor") from e

    def train(self):
        try:
            model = ARIMA(self.df, order=(2,2,0))
            self.fitted = model.fit()
        except Exception as e:
            raise Exception("Error training ARIMA model") from e

    def forecast(self):
        try:
            forecast_values = self.fitted.forecast(steps = self.days_ahead)
            forecast_dates = pd.date_range(start=self.df.index[-1] + timedelta(days=1), periods=self.days_ahead)
            self.forecast_df = pd.DataFrame({
                'Date' : forecast_dates,
                'Forecast' : forecast_values
            })
        except Exception as e:
            raise Exception("Error forecasting with ARIMA model") from e

    def getData(self):
        try:
            if self.forecast_df is None:
                raise Exception("No forecast data available. Ensure forecast() was run successfully.")
            return self.forecast_df.to_dict()
        except Exception as e:
            raise Exception("Error retrieving forecast data from ArimaPredictor") from e

class SarimaPredictor:

    def __init__(self, ticker, interval, api, days_ahead):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.forecast_df = np.nan
            self.days_ahead = days_ahead
            self.fitted = np.nan
    
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing SarimaPredictor") from e

    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.asfreq('B').ffill()
            self.df = self.df['Close'].to_frame()
            # self.df = self.df.dropna()
        except Exception as e:
            raise Exception("Error preparing data in SarimaPredictor") from e

    def train(self):
        try:
            model = SARIMAX(self.df, order=(4,2,1), seasonal_order=(2,1,0,7))
            self.fitted = model.fit()
        except Exception as e:
            raise Exception("Error training SARIMA model") from e

    def forecast(self):
        try:
            forecast_values = self.fitted.forecast(steps = self.days_ahead)
            forecast_dates = pd.date_range(start=self.df.index[-1] + timedelta(days=1), periods=self.days_ahead)
            self.forecast_df = pd.DataFrame({
                'Date' : forecast_dates,
                'Forecast' : forecast_values
            })
        except Exception as e:
            raise Exception("Error forecasting with SARIMA model") from e

    def getData(self):
        try:
            if self.forecast_df is None:
                raise Exception("No forecast data available. Ensure forecast() was run successfully.")
            return self.forecast_df.to_dict()
        except Exception as e:
            raise Exception("Error retrieving forecast data from SarimaPredictor") from e


class SarimaxPredictor:

    def __init__(self, ticker, interval, api, days_ahead):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.forecast_df = np.nan
            self.days_ahead = days_ahead
            self.fitted = np.nan
            
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing SarimaxPredictor") from e

    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.asfreq('B').ffill()
            self.df = self.df[['Close','Volume']]
            self.df['ema_100'] = self._ema(self.df["Close"],100)
            self.df['rsi'] = self._rsi(self.df["Close"])
            self.df['macd'] = self._macd(self.df["Close"])
            self.df['obv'] = self._obv(self.df["Close"], self.df["Volume"])
            self.df = self.df[['ema_100', 'rsi', 'macd', 'obv', 'Close']]
            self.df = self.df.dropna()
        except Exception as e:
            raise Exception("Error preparing data in SarimaxPredictor") from e

    def _ema(self, close, period=20):
        try:
            return close.ewm(span=period, adjust=False).mean()
        except Exception as e:
            raise Exception("Error computing EMA") from e
    
    def _rsi(self, close, period=14):
        try:
            delta = close.diff()
            gain, loss = delta.copy(), delta.copy()
            gain[gain < 0] = 0
            loss[loss > 0] = 0
            avg_gain = gain.rolling(period).mean()
            avg_loss = abs(loss.rolling(period).mean())
            rs = avg_gain / avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))
            return rsi
        except Exception as e:
            raise Exception("Error computing RSI") from e
    
    def _macd(self, close, fast_period=12, slow_period=26, signal_period=9):
        try:
            fast_ema = close.ewm(span=fast_period, adjust=False).mean()
            slow_ema = close.ewm(span=slow_period, adjust=False).mean()
            macd_line = fast_ema - slow_ema
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
            histogram = macd_line - signal_line
            return macd_line
        except Exception as e:
            raise Exception("Error computing MACD") from e

    def _obv(self, close, volume):
        try:
            obv = np.where(close > close.shift(), volume, np.where(close < close.shift(), -volume, 0)).cumsum()
            return obv
        except Exception as e:
            raise Exception("Error computing OBV") from e

    def _generate_future_indicators(self, df, future_dates, last_close):
        try:
            future_df = pd.DataFrame(index=future_dates)
            future_df['Close'] = last_close
            future_df['ema_100'] = df['ema_100'].iloc[-1]
            future_df['rsi'] = df['rsi'].iloc[-1]
            future_df['macd'] = df['macd'].iloc[-1]
            future_df['obv'] = df['obv'].iloc[-1]
            return future_df[['ema_100', 'rsi', 'macd', 'obv']]
        except Exception as e:
            raise Exception("Error generating future indicators for SarimaxPredictor") from e
    
    def train(self):
        try:
            model = SARIMAX(self.df['Close'], order=(2,0,2), seasonal_order=(2,1,0,7), 
                            exog = self.df[['ema_100', 'rsi', 'macd', 'obv']],
                            enforce_stationarity=False, enforce_invertibility=False)
            self.fitted = model.fit(maxiter = 1000, method = "powell")
        except Exception as e:
            raise Exception("Error training SARIMAX model") from e
    
    def forecast(self):
        try:
            forecast_dates = pd.date_range(start=self.df.index[-1] + timedelta(days=1), periods=self.days_ahead)
            future_exog = self._generate_future_indicators(self.df, forecast_dates, self.df['Close'].iloc[-1])
            forecast_values = self.fitted.forecast(steps=self.days_ahead, exog=future_exog)
            self.forecast_df = pd.DataFrame({
                'Date' : forecast_dates,
                'Forecast' : forecast_values
            })
        except Exception as e:
            raise Exception("Error forecasting with SARIMAX model") from e

    def getData(self):
        try:
            if self.forecast_df is None:
                raise Exception("No forecast data available. Ensure forecast() was run successfully.")
            return self.forecast_df.to_dict()
        except Exception as e:
            raise Exception("Error retrieving forecast data from SarimaxPredictor") from e

PREDICTORS = {
    "fbprophet": FbProphetPredictor,
    "arima": ArimaPredictor,
    "sarima": SarimaPredictor,
    "sarimax": SarimaxPredictor
}