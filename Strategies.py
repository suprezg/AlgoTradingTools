import numpy as np
import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy

def sma(close, length = 10):
    return ta.sma(close = close, length = length)

def rsi(close, length = 14):
    return ta.rsi(close = close, length = length)

def ema(close, length = 10):
    return ta.ema(close, length = length)

def atr(high, low, close, length = 14):
    return ta.atr(high = high, low = low, close = close, length = length)

def rh(high, window = 10):
    return high.rolling(window = window).max()

def rl(low, window = 10):
    return low.rolling(window = window).min()

def macd(close, fast = 12, slow = 26, signal = 9):
    df = ta.macd(close = close, fast = fast, slow = slow, signal = signal)
    macd_line = df.iloc[0:,0]
    signal_line = df.iloc[0:,2]
    return (macd_line, signal_line)

def bbands(close, length = 5, std = 2):
    df = ta.bbands(close = close, length = length, std = std)
    lower_band = df.iloc[0:,0]
    mid_band = df.iloc[0:,1]
    upper_band = df.iloc[0:,2]
    return (lower_band, mid_band, upper_band)

def stoch(index, high, low, close, k = 14, d = 3):
    df = ta.stoch(high = high, low = low, close = close, k = k, d = d)
    df2 = pd.DataFrame(np.NaN, index = index[0:k-1] ,columns = df.columns)
    df = pd.concat([df2, df])
    k_line = df.iloc[:,0]
    d_line = df.iloc[:,1]
    return (k_line, d_line)

class SmaCross(Strategy):
    """
        Sma Cross Strategy
        if fast sma crosses above slow sma
            then we close our previous position and buy fresh and set stoploss
        if slow sma crosses above fast sma 
            then we close our previous positions and sell fresh and set stoploss
    """
    n1 = 10   # Fast SMA Length
    n2 = 20   # Slow SMA Length
    n3 = 14   # ATR Length
    n4 = 2    # Stop Loss Coefficient
    
    def init(self):
        try:
            self.fast_sma = self.I(sma, self.data.Close.s, self.n1)
            self.slow_sma = self.I(sma, self.data.Close.s, self.n2)
            self.atr = self.I(atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n3)
        except Exception as e:
            raise Exception("Error Initializing Parameters") from e

    def next(self):
        if (self.fast_sma[-2] < self.slow_sma[-2] and self.fast_sma[-1] > self.slow_sma[-1]):
            stoploss = self.data.Close[-1] - (self.n4 * self.atr[-1])
            self.position.close()
            self.buy(sl = stoploss)

        elif (self.fast_sma[-2] > self.slow_sma[-2] and self.fast_sma[-1] < self.slow_sma[-1]):
            stoploss = self.data.Close[-1] + (self.n4 * self.atr[-1])
            self.position.close()
            self.sell(sl = stoploss)


class RsiEmaCross(Strategy):
    """
        EMA & RSI Strategy
        if current closing price is above slow ema and fast ema 
            if rsi crosses above a certain threshold
                then we will calculate the stop loss and buy
        if current closing price is below slow ema or fast ema and if there are any previous long positions
            then we close our long position
    """
    n1 = 50     # Fast EMA Length
    n2 = 200    # Slow EMA Length
    n3 = 14     # RSI Length
    n4 = 14     # ATR Length
    n5 = 2      # Stop Loss Coefficient
    
    def init(self):
        self.fast_ema = self.I(ema, self.data.Close.s, self.n1)
        self.slow_ema = self.I(ema, self.data.Close.s, self.n2)
        self.rsi = self.I(rsi, self.data.Close.s, self.n3)
        self.atr = self.I(atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n4)
    
    def next(self):
         if (self.data.Close[-1] > self.slow_ema[-1] and self.data.Close[-1] > self.fast_ema[-1]):
             if (self.rsi[-2] < 70 and self.rsi[-1] > 70): 
                 if (not self.position.is_long):
                     stoploss = self.data.Close[-1] - (self.n5 * self.atr[-1])
                     self.buy(sl = stoploss)
         elif ((self.data.Close[-1] < self.slow_ema[-1] or self.data.Close[-1] < self.fast_ema[-1]) and 
               self.position.is_long):
                 self.position.close()


class MACDEmaCrossover(Strategy):
    """
        MACD Strategy
        if macd line crosses above signal line and current closing price is above slow ema and we are not currently
        in any long position
            then we buy
        else if macd line crosses below signal line or current closing price is below slow ema 
                then we close all our long positions
    """
    n1 = 12    # MACD Fast EMA Length
    n2 = 26    # MACD Slow EMA Length
    n3 = 9     # MACD Singal Length
    n4 = 200   # Slow EMA Length
    n5 = 14    # ATR Length
    n6 = 2     # Stop Loss Coefficient
    
    def init(self):
        self.macd_line, self.signal_line = self.I(macd, self.data.Close.s, self.n1, self.n2, self.n3)
        self.slow_ema = self.I(ema, self.data.Close.s, self.n2)
        self.atr = self.I(atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n5)

    def next(self):
        if (self.macd_line[-2] < self.signal_line[-2] and 
            self.macd_line[-1] > self.signal_line[-1] and 
            self.data.Close[-1] > self.slow_ema[-1] and 
            not self.position.is_long):
                stoploss = self.data.Close[-1] - (self.n5 * self.atr[-1])
                self.buy(sl = stoploss)
        elif ((self.macd_line[-2] > self.signal_line[-2] and self.macd_line[-1] < self.signal_line[-1]) or 
              self.data.Close[-1] < self.slow_ema[-1]):
            if (self.position.is_long):
                self.position.close()


class BollingerBandBreakout(Strategy):
    """
        Bolling Bands Strategy
        if previous day closing price is below lower band and previous day rsi is less than rsi low threshold and
        current closing pricee is more than previous day high and bandwidth is more than band width threshold
            if we have any short positions
                then we close our positions
            if we dont have any long position
                then we calculate sl and tp using atr and buy
        if previous day closing price is above the upperband and previous day rsi is more than rsi high threshold
        and current closing price is less than previous day low and bandwidth is more than band width threshold
            if we have any long positions
                then we close our positions
            if we dont have any short positions
                then we calculate sl and tp using atr and sell
                
    """
    n1 = 30      # BBANDS Length
    n2 = 2       # BBANDS STD
    n3 = 14      # RSI Length
    n4 = 14      # ATR Length
    n5 = 3       # Stop loss Coefficient
    n6 = 2       # Take Profit Coefficient
    n7 = 30      # RSI Low Threshold
    n8 = 70      # RSI High Threshold
    n9 = 0.0015  # BBANDS Width Threshold

    def init(self):
        self.lower_band, self.mid_band, self.upper_band = self.I(bbands, self.data.Close.s, self.n1, self.n2)
        self.band_width = (self.upper_band - self.lower_band)/self.mid_band
        self.rsi = self.I(rsi, self.data.Close.s, self.n3)
        self.atr = self.I(atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n4)

    def next(self):
        if (self.data.Close[-2] < self.lower_band[-2] and self.rsi[-2] < self.n7 and 
            self.data.Close[-1] > self.data.High[-2] and self.band_width[-1] > self.n9):
            if (self.position.is_short):
                self.position.close()
            if (not self.position.is_long):
                stoploss = self.data.Close[-1] - (self.n5 * self.atr[-1])
                takeprofit = self.data.Close[-1] + (self.n6 * self.atr[-1])
                self.buy(sl = stoploss, tp = takeprofit)
        elif (self.data.Close[-2] > self.upper_band[-2] and self.rsi[-2] > self.n8 and 
              self.data.Close[-1] < self.data.Low[-2] and self.band_width[-1] > self.n9):
            if (self.position.is_long):
                self.position.close()
            if (not self.position.is_short):
                stoploss = self.data.Close[-1] + (self.n5 * self.atr[-1])
                takeprofit = self.data.Close[-1] - (self.n6 * self.atr[-1])
                self.sell(sl = stoploss, tp = takeprofit)


class SMATrendFollowing(Strategy):
    """
        SMA Strategy
        if we dont have any position and current closing price is above sma
            then we buy
        if we have any position and current closing price is below sma
            then we close our positions
    """
    n1 = 50    # SMA Length

    def init(self):
        self.sma = self.I(sma, self.data.Close.s, self.n1)

    def next(self):
        if not self.position and self.data.Close[-1] > self.sma[-1]:
            self.buy()
        elif self.position and self.data.Close[-1] < self.sma[-1]:
            self.position.close()

class StochasticCrossover(Strategy):
    """
        Stochastic Oscillator Strategy
        if we dont have any positions
            if k line crosses above d line and k line is less than over sold threshold
                then we calculate the stoploss and buy
        if we have any positions
            if d line crosses above k line and k line is more than over bought threshold
                then we close our current positions
    """
    n1 = 14    # k Length
    n2 = 3     # d Length
    n3 = 14    # ATR Length
    n4 = 2     # Stop Loss Coefficient
    n6 = 20    # Over Sold Threshold
    n7 = 80    # Over Bought Threshold

    def init(self):
        self.k_line, self.d_line = self.I(stoch, self.data.index, self.data.High.s, self.data.Low.s, 
                                          self.data.Close.s, self.n1, self.n2)
        self.atr = self.I(atr, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n3)

    def next(self):
        if not self.position: 
            if self.k_line[-2] < self.d_line[-2] and self.k_line[-1] > self.d_line[-1] and self.k_line[-1] < self.n6:
                stoploss = self.data.Close[-1] - (self.n4 * self.atr[-1])
                self.buy(sl = stoploss)
        else:
            if self.d_line[-2] < self.k_line[-2] and self.d_line[-1] > self.k_line[-1] and self.k_line[-1] > self.n7:
                self.position.close()

STRATEGIES = {
    "SmaCross": SmaCross,
    "RsiEmaCross": RsiEmaCross,
    "MACDEmaCrossover": MACDEmaCrossover,
    "BollingerBandBreakout": BollingerBandBreakout,
    "SMATrendFollowing": SMATrendFollowing,
    "StochasticCrossover": StochasticCrossover
}

STRATEGY_OPTIMIZATION = {
    "SmaCross": {
        "params": {
            "n1": range(5, 30, 1),
            "n2": range(10, 60, 2),
            "n3": [12, 13, 14, 15, 16],
            "n4": [2, 3, 4]
        },
        "constraint": lambda param: param.n1 < param.n2
    },
    "RsiEmaCross": {
        "params": {
            "n1": range(25, 76, 5),
            "n2": range(150, 251, 10),
            "n3": range(11, 18, 1),
            "n4": [12, 13, 14, 15, 16],
            "n5": [2, 3, 4]
        }
    },
    "MACDEmaCrossover": {
        "params": {
            "n1": range(8, 17, 1),
            "n2": range(18, 35, 1),
            "n3": [8, 9, 10],
            "n4": range(150, 251, 10),
            "n5": [12, 13, 14, 15, 16],
            "n6": [2, 3, 4]
        }
    },
    "BollingerBandBreakout": {
        "params": {
            "n1": [25, 30, 35],
            "n2": [1.5, 2, 2.5],
            "n3": [12, 13, 14, 15, 16],
            "n4": [12, 13, 14, 15, 16],
            "n5": [2, 3, 4],
            "n6": [2, 3, 4, 5, 6, 7, 8, 9],
            "n7": [25, 30, 35],
            "n8": [25, 30, 35],
            "n9": [0.003, 0.006, 0.008, 0.03, 0.06, 0.08]
        }
    },
    "SMATrendFollowing": {
        "params": {
            "n1": range(30, 81, 5)
        }
    },
    "StochasticCrossover": {
        "params": {
            "n1": [12, 13, 14, 15],
            "n2": [3, 4, 5],
            "n3": [12, 13, 14, 15],
            "n4": [2, 3, 4],
            "n6": [15, 20, 25],
            "n7": [75, 80, 85]
        }
    }
}

def prepareData(results_best_returns, results_best_winrate):
    return ({
        "results_best_returns" : {
            "Win Rate %": results_best_returns["Win Rate [%]"],
            "Return %": results_best_returns["Return [%]"],
            "Trades": {
                "EntryPrice": results_best_returns['_trades']["EntryPrice"],
                "ExitPrice": results_best_returns['_trades']["ExitPrice"],
                "Profit&Loss": results_best_returns['_trades']["PnL"],
                "EntryTime": results_best_returns['_trades']["EntryTime"],
                "ExitTime": results_best_returns['_trades']["ExitTime"]
            }
        },
        "results_best_winrate" : {
            "Win Rate %": results_best_winrate["Win Rate [%]"],
            "Return %": results_best_winrate["Return [%]"],
            "Trades": {
                "EntryPrice": results_best_winrate['_trades']["EntryPrice"],
                "ExitPrice": results_best_winrate['_trades']["ExitPrice"],
                "Profit&Loss": results_best_winrate['_trades']["PnL"],
                "EntryTime": results_best_winrate['_trades']["EntryTime"],
                "ExitTime": results_best_winrate['_trades']["ExitTime"]
            }
        }
    })