"""

traders.py ~ includes diffrent trading bot classes 
and a function to make the traders trade stocks concurrently 
using a Threadpool Executor

"""

import metrics
import time
import robin_stocks
import concurrent.futures


# Run Trading Strategies Concurrently
def TRADE_STOCKS(stocks, Trader):
    # Run - Trading strategy concurrently
    traders = list(map(lambda s: Trader(s), stocks))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = executor.map(Trader.trade, traders)
        for r in res:
            print(r)


# Trader buys in at local min and sells at local max
class Flux_Trader:
    def __init__(self, Stock):
        self.stock = Stock
        # Scan the current fluctuating price data for a local minimum and maximum
        self.sell_price, self.buy_price = metrics.max_min_price(self.stock)
        while self.buy_price == self.sell_price:
            self.sell_price, self.buy_price = metrics.max_min_price(self.stock)
        # Get a price to cut your losses and sellout at 
        self.stop_price = metrics.get_stoplossprice(self.buy_price, self.sell_price)
        # Are you currently holding said stock
        self.is_holding = False
        # What did you buy and sell the stock for 
        self.reccord = [None] * 2

    def buy(self, ticker, amount=1):
        robin_stocks.order(ticker, quantity=amount,
                           orderType='market', side='buy', trigger='immediate')

    def sell(self, ticker, amount=1):
        robin_stocks.order(ticker, quantity=amount,
                           orderType='market', side='sell', trigger='immediate')

    def profit(self):
        if self.reccord[1] and self.reccord[0]:
            return self.reccord[1] - self.reccord[0]
        return 0 
    
    def trade(self,trading_cycles=15,breaktime=5):
        # get the trader to tap into the price stream of the stock
        stream = self.stock.price_stream()
        p = float(next(stream))
        while p:
            # not holding - need to buy when price falls below local min
            if self.is_holding == False:
                if p <= self.buy_price:
                    #self.buy(self.stock.symbol)
                    self.reccord[0] = p
                    self.is_holding = True
            # holding - need to sell when price rises above local max
            else:
                if p >= self.sell_price or p < self.stop_price:
                    #self.sell(self.stock.symbol)
                    self.reccord[1] = p
                    self.is_holding = False
                    return self.profit()
        
            #try moving to next price spit out by generator
            try:
                p = float(next(stream))
            except:
                break
        # Price-stream ends
        # we already sold and we are done 
        if self.is_holding == False:
            return self.profit()
        
        # Tap another Price Stream
        elif trading_cycles != 0:
            trading_cycles -= 1
            # Give other traders a shot at trading their stocks 
            time.sleep(breaktime)
            self.trade(trading_cycles)

        # if it's below stop-loss sell else deal with it tomorrow
        if self.stock.update() <= self.stop_price:
            #self.sell(self.stock.symbol)
            return self.profit()

        ## TODO - Write into the json file called 'selling.json'
        return 'Queued - ' + self.stock.symbol + 'To sell tomorrow'

# Finds the best stock for a given capital acquisition
class Value_Trader(object):
    def __init__(self,capital):
        return self