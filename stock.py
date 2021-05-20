"""
stock.py ~ Contains implimentation of Stock Class
"""

import robin_stocks
import time
import yfinance as yf

class Stock:
    
    '''
        Stock Object from Robinhood API ~ Serves as main data structure to get both real-time and historical 
        Financial Data
    '''
    
    def __init__(self, ticker):
        self.symbol = ticker
        self.price = float(robin_stocks.get_latest_price(ticker)[0])   
        self.info = None
        self.data = None

    def update(self, latency=0.05):
        time.sleep(latency)
        self.price = float(robin_stocks.get_latest_price(self.symbol)[0])
        return self.price
    
    def price_stream(self, timer=10):
        start_time, end_time = time.perf_counter(), 0
        while (end_time - start_time) <= timer:
            yield self.update()
            end_time = time.perf_counter()
        else:
            yield None

    def get_info(self):
        if type(self.info) == type(None):
            self.info = robin_stocks.get_fundamentals(self.symbol)[0]
        return self.info
    
    def get_data(self):
        if type(self.data) == type(None):
            self.data = yf.download(self.symbol)
        return self.data

    def reset(self):
        self = Stock(self.symbol)
        return self
