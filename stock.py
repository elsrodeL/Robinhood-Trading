import robin_stocks
import json
import time
import metrics
import yfinance as yf
import concurrent.futures

# schedualar to make it run daily 
# https: // datatofish.com/python-script-windows-scheduler/

#login to accout
def login():
    f = open('client_secrets.json',)
    data = json.load(f)
    username, password = data['client'], data['client_secret']
    robin_stocks.login(username, password)
    f.close()
    return 

login()

# Create Stock Object -- Creates a generator
class Stock:
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

# Create a Trade Object -- Trades Stock Object given the generator
class Speed_Trader:
    def __init__(self,stock):
        
        self.stock = stock
        self.sell_price, self.buy_price = metrics.max_min_price(self.stock)
        
        # get a min != max value to work with 
        while self.buy_price == self.sell_price:
            self.sell_price, self.buy_price = metrics.max_min_price(self.stock)
    
        self.stop_price = metrics.get_stoplossprice(self.buy_price,self.sell_price)
        self.is_holding = False
        self.reccord = [None] * 2
    
    def buy(self, ticker, amount=1):
        robin_stocks.order(ticker, quantity=amount, orderType='market', side='buy', trigger='immediate')

    def sell(self, ticker, amount=1):
        robin_stocks.order(ticker, quantity=amount, orderType='market', side='sell', trigger='immediate')

    def trade(self,max_cycles=20,DROPOUT_TIME=100):
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
                    return self.reccord

            #try moving to next price spit out by generator
            try:
                p = float(next(stream))
            except:
                break
        
        # Price-stream ends
        # Tap another Price Stream
        if max_cycles != 0:
            max_cycles -= 1
            self.trade(max_cycles)
        
        # Don't Tap another Price Stream 
        else:
            # Didn't buy anything - Move on to something else
            if self.is_holding == False:
                return None
            
            # Bought-in
            else:
                target = self.sell_price 
                bought = self.reccord[0]
                time.sleep(DROPOUT_TIME)
                self = Speed_Trader(self.stock)
                self.sell_price = target
                self.is_holding = True
                self.stop_price = metrics.get_stoplossprice(bought,self.sell_price)
                if DROPOUT_TIME > 0:
                    DROPOUT_TIME -= 5
                    self.trade(max_cycles=2,DROPOUT_TIME=DROPOUT_TIME)
                else:
                    #self.sell(self.stock.symbol)
                    self.reccord[1] = self.stock.update()
                    return self.reccord
                        
                        
# Run Trading Strategies Concurently 
def TRADE_STOCKS(stocks,TRADER):
    # Run - Trading strategy concurently
    traders = list(map(lambda s: Speed_Trader(s), stocks))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = executor.map(TRADER.trade,traders)
        for r in res:
            print(r)


# Test-Stocks
tests = [Stock(i) for i in ['XELB','AMC']]
for t in tests:
    print(t.symbol)

t_start = time.perf_counter() 
TRADE_STOCKS(tests,Speed_Trader)
t_end = time.perf_counter()
print(f'Traded stocks in {t_end - t_start} (s)')
