import pandas as pd
import yfinance as yf
from yfinance import EquityQuery
from binance.client import Client

class StockScreener: 
    
    def __init__(self, screener_type = "daygainers"):
        self.screener_map = {
            "daygainers": {
                "sortField": "percentchange",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region", "in"]),
                    EquityQuery("LTE", ["percentchange", 3]),
                    EquityQuery("GTE", ["intradaymarketcap", 2000000000]),
                    EquityQuery("GTE", ["intradayprice", 5]),
                    EquityQuery("GT", ["dayvolume", 15000])
                ])
            },
            "daylosers": {
                "sortField": "percentchange",
                "sortAsc": True,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region", "in"]),
                    EquityQuery("LTE", ["percentchange", 3]),
                    EquityQuery("GTE", ["intradaymarketcap", 2000000000]),
                    EquityQuery("GTE", ["intradayprice", 5]),
                    EquityQuery("GT", ["dayvolume", 15000])
                ])
            },
            "undervaluedsmallcap": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("BTWN", ["peratio.lasttwelvemonths",0,15]),
                    EquityQuery("LT", ["pegratio_5y",0.8]),
                    EquityQuery("BTWN", ["intradaymarketcap",100000000,1000000000])
                ])
            },
            "undervaluedlargecap": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("BTWN", ["peratio.lasttwelvemonths",0,20]),
                    EquityQuery("LT", ["pegratio_5y",1]),
                    EquityQuery("BTWN", ["intradaymarketcap",10000000000,100000000000])
                ])
            },
            "technologysector": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("GTE", ["quarterlyrevenuegrowth.quarterly",25]),
                    EquityQuery("GTE", ["epsgrowth.lasttwelvemonths",25]),
                    EquityQuery("EQ", ["sector", "Technology"])
                ])
            },
            "energysector": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("GTE", ["quarterlyrevenuegrowth.quarterly",25]),
                    EquityQuery("GTE", ["epsgrowth.lasttwelvemonths",25]),
                    EquityQuery("EQ", ["sector", "Energy"])
                ])
            },
            "healthcaresector": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("GTE", ["quarterlyrevenuegrowth.quarterly",25]),
                    EquityQuery("GTE", ["epsgrowth.lasttwelvemonths",25]),
                    EquityQuery("EQ", ["sector", "Healthcare"])
                ])
            },
            "estatesector": {
                "sortField": "eodvolume",
                "sortAsc": True,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("GTE", ["quarterlyrevenuegrowth.quarterly",25]),
                    EquityQuery("GTE", ["epsgrowth.lasttwelvemonths",25]),
                    EquityQuery("EQ", ["sector", "Real Estate"])
                ])
            },
            "industrialsector": {
                "sortField": "eodvolume",
                "sortAsc": False,
                "query": EquityQuery("AND", [
                    EquityQuery("EQ", ["region","in"]),
                    EquityQuery("GTE", ["quarterlyrevenuegrowth.quarterly",25]),
                    EquityQuery("GTE", ["epsgrowth.lasttwelvemonths",25]),
                    EquityQuery("EQ", ["sector", "Industrials"])
                ])
            }
        }
        if screener_type not in self.screener_map:
            raise ValueError(f"Invalid Screener Type. Valid types are: {', '.join(self.screener_map.keys())}")
        self.screener_type = screener_type
        self.columns = ["symbol", "marketCap","regularMarketVolume",
                        "regularMarketPrice","regularMarketChange","regularMarketChangePercent",
                        "regularMarketDayHigh","regularMarketDayLow",
                        "fiftyTwoWeekHigh","fiftyTwoWeekLow","fiftyDayAverage","twoHundredDayAverage"]

    def getData(self):
        try:
            response = yf.screen(query=self.screener_map[self.screener_type]["query"],
                                 sortField=self.screener_map[self.screener_type]["sortField"],
                                 sortAsc=self.screener_map[self.screener_type]["sortAsc"],size = 25)
            df = pd.DataFrame(response["quotes"])
            df = df.loc[:,self.columns]
            return df.to_dict()
        except Exception as e:
            raise Exception(f"Error getting screener data\n {e}")