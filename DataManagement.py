import os
import re
import time
import numpy as np
import pandas as pd
import requests_cache
import yfinance as yf
from bs4 import BeautifulSoup
from binance.client import Client
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor


class NewsScraper:
    NEWS_URLS = {
        "last24h": [
            "https://pulse.zerodha.com/"
        ],
        "worldnews": [
            "https://www.moneycontrol.com/news/world/",
            "https://in.investing.com/news/world-news"
        ],
        "indianews": [
            "https://www.moneycontrol.com/news/india/",
            "https://www.businesstoday.in/india"
        ],
        "stocknews": [
            "https://www.moneycontrol.com/news/business/stocks/",
            "https://www.businesstoday.in/markets/company-stock"
        ],
        "iponews": [
            "https://www.moneycontrol.com/news/business/ipo/"
        ],
        "commoditynews": [
            "https://www.moneycontrol.com/news/business/commodities/",
            "https://in.investing.com/news/commodities-news"
        ],
        "cryptonews": [
            "https://www.moneycontrol.com/news/tags/cryptocurrency.html",
            "https://in.investing.com/news/cryptocurrency-news"
        ]
    }

    def __init__(self, news_type = "last24h"):
        if news_type not in self.NEWS_URLS:
            raise Exception(f"Invalid News Type.\n Following are the types:{', '.join(self.NEWS_URLS.keys())}")
        self.htmls = []
        self.links = []
        self.parse_data = []
        self.news_type = news_type
    
    def _useZerodhaParser(self, html):
        ########  Pulse By Zerodha Scraper  ########
        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.find("ul", id = "news").find_all("li", class_ = "box item")
        titles, descriptions, links = [], [], []
        for block in blocks:
            titles.append(block.find("a").text)
            descriptions.append(block.find("div", class_ = "desc").text)
            links.append(block.find("a").get("href"))
        return ({"Titles": titles, "Descriptions": descriptions, "Links":links})
    
    def _useInvestingParser(self, html):
        ########  In.Investing Scraper  ########
        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.find_all("article", attrs={"data-test":"article-item"})
        titles, descriptions, links = [], [], []
        for block in blocks:
            titles.append(block.find("a", attrs={"data-test":"article-title-link"}).text)
            descriptions.append(block.find("p", attrs={"data-test":"article-description"}).text)
            links.append(block.find("a", attrs={"data-test":"article-title-link"}).get("href"))
        return ({"Titles": titles, "Descriptions": descriptions, "Links":links})
    
    def _useMoneycontrolParser(self, html):
        ########  MoneyControl Scraper  ########
        soup = BeautifulSoup(html, 'html.parser')
        blocks = soup.find("ul", id = "cagetory").find_all("li", class_ = "clearfix")
        titles, descriptions, links = [], [], []
        for block in blocks:
            titles.append(block.find("h2").find("a").text)
            descriptions.append(block.find("p").text)
            links.append(block.find("h2").find("a").get("href"))
        return ({"Titles": titles, "Descriptions": descriptions, "Links":links})
    
    def _useBusinesstodayParser(self, html):
        ########  BusinessToday Scraper  ########
        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.find("div", class_ = "section-listing-LHS").find_all("div", class_ = "widget-listing")
        titles, descriptions, links = [], [], []
        for block in blocks:
            titles.append(block.find("h2").find("a").text)
            descriptions.append(block.find("p").text)
            links.append(block.find("h2").find("a").get("href"))
        return ({"Titles": titles, "Descriptions": descriptions, "Links":links})
    
    def _usePlaywright(self, url):
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                page = browser.new_page()
                page.goto(url, wait_until='domcontentloaded')
                html = page.content()
                self.htmls.append(html)
                self.links.append(url)
                browser.close()
        except Exception as e:
            raise Exception(f"Error using Playwright Firefox\n {e}")

    def scrapePages(self):
        urls = self.NEWS_URLS[self.news_type]
        with ThreadPoolExecutor() as executor:
            try:
                executor.map(self._usePlaywright, urls)
            except Exception as e:
                raise Exception(f"Error in scraping with Playwright Firefox\n {e}")
                
    def parsePages(self):
        if not all([self.htmls, self.links]):
            raise Exception(f"Error in Parsing Pages")
        scraped_data = list(zip(self.htmls, self.links))
        parsers = [
            ("moneycontrol", self._useMoneycontrolParser),
            ("businesstoday", self._useBusinesstodayParser),
            ("investing", self._useInvestingParser),
            ("zerodha", self._useZerodhaParser)
        ]
        for html, link in scraped_data:
            for source, parser_func in parsers:
                if re.search(rf"{source}", link):
                    self.parse_data.append(parser_func(html=html))
                    break
                    
    def getData(self):
        if not self.parse_data:
            raise Exception(f"Error in getting news data")
        news_df_list = []
        for news_dict in self.parse_data:
            news_df_list.append(pd.DataFrame(news_dict))
        merged_df = pd.concat(news_df_list, axis=0, ignore_index=True)
        return merged_df.to_dict()


class StockScraper:
    
    def __init__(self, ticker, interval, api):
        self.API_CONFIG = {
            'yfinance': {
                'interval_map': {
                    "1min": "1m", "5min": "5m", "1hr": "1h", "1day": "1d", "1week": "1wk", "1mon": "1mo"
                },
                'days_map': {
                    "1min": 8, "5min": 59, "1hr": 364*2, "1day": 364*10, "1week": 364*20, "1mon": 364*20
                },
                'fetch': self._useYfinance
            },
            'binance': {
                'interval_map': {
                    "1min": "1m", "5min": "5m", "1hr": "1h", "1day": "1d", "1week": "1w", "1mon": "1M"
                },
                'days_map': {
                    "1min": 2, "5min": 10, "1hr": 150, "1day": 364*6, "1week": 364*6, "1mon": 364*6
                },
                'fetch': self._useBinance
            }
        }        
        if api not in self.API_CONFIG:
            raise Exception(f"Unsupported API\n Following are the APIs: yfinance, binance")
        if interval not in self.API_CONFIG[api]["interval_map"]:
            raise Exception(f"Unsupported Interval\n Following are the Intervals: 1min, 5min, 1hr, 1day, 1week, 1mon")
        self.ticker = ticker
        self.interval = interval
        self.api = api

    def _useYfinance(self, ticker, interval, start_date, end_date):
        # 1m,5m,1h,1d,1wk,1mo
        session = requests_cache.CachedSession("yfinance.cache")
        session.headers["User-agent"] = "data-retriever"
        try:
            data = yf.download(
                tickers = ticker,
                interval=interval,
                start=start_date,
                end=end_date,
                session=session,
            )
            data.columns = ["Close", "High", "Low", "Open", "Volume"]
            data = data[["Open", "High", "Low", "Close", "Volume"]]
            return data.to_dict()
        except Exception as e:
            raise Exception(f"Error occured using Yfinance\n {e}")
    
    def _useBinance(self, ticker, interval, start_date, end_date):
         # 1m,5m,1h,1d,1w,1M
        client = Client()
        try: 
            data = pd.DataFrame(client.get_historical_klines(
                symbol = ticker, 
                interval = interval, 
                start_str = start_date,
                end_str = end_date
            ))
            data = data.iloc[:,:6] 
            data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            data.set_index('Date', inplace=True)
            data.index = pd.to_datetime(data.index, unit='ms')
            data = data.astype(float)
            return data.to_dict()
        except Exception as e:
            raise Exception(f"Error occured using Binance\n {e}")

    def getData(self):
        config = self.API_CONFIG[self.api]
        try: 
            start_date = (datetime.today() - timedelta(days=config['days_map'][self.interval])).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        except Exception as e:
            raise Exception(f"Error in getting ticker data\n {e}")
        return config['fetch'](self.ticker, config['interval_map'][self.interval], start_date, end_date)