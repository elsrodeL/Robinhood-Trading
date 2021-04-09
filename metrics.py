# Lukas Elsrode - Calculation and data proecssing file
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib
import yfinance as yf
import requests

def get_pricestream_data(Stock):
    '''Returns the Price Data in a list 
    '''
    rv = []
    stream = Stock.price_stream()

    p = float(next(stream))
    while p:
        rv.append(float(p))
        p = next(stream)
    return rv

def pricestream_max_min_price(Stock):
    '''returns (max,min) of stock price 
    '''
    prices = get_pricestream_data(Stock)
    return max(prices), min(prices)

def max_min_price(Stock,cycles=2):
    '''returns (max,min) of stock price
       after a num of cycles
    '''
    cycles = cycles
    p = [0,10000]
    while cycles > 0:
        m,n = pricestream_max_min_price(Stock)
        if p[0] < m:
            p[0] = m
        if p[1] > n:
            p[1] = n
        cycles -= 1
    return p[0],p[1]
        
def curr_mean_price(Stock,cycles=2):
    '''returns (max,min) of stock price
       after a num of cycles
    '''
    rv = []
    for _ in range(cycles):
        prices = get_pricestream_data(Stock)
        rv.append(np.mean(prices))
    cycles -= 1
    return np.mean(rv)
        
def show_live_volitility(Stock):
    '''returns plot of current trades 
    '''
    prices = get_pricestream_data(Stock)
    plt.plot([i for i,j in enumerate(prices)],prices)
    plt.xlabel('Time (s)')
    plt.ylabel('Stock Price ($)')
    plt.title('Price Volitility of  ' + Stock.symbol)
    fname = Stock.symbol + '_liveVol.png'
    plt.savefig(fname)
    return

def get_stoplossprice(buy_price, win_price, ratio=2):
    '''Returns price at which to sell off given expected risk reward ratio
    '''
    out_price = (buy_price*(1 + ratio) - win_price)/ratio
    return out_price

def get_prices(Stock):
    ''' returns np array of all-time closing prices
    '''
    df = Stock.get_data()
    return pd.to_numeric(df['Close'])

def show_prices(Stock):
    '''Plots prices as function of time
    '''
    prices = get_prices(Stock)
    dates = matplotlib.dates.date2num(prices.index)
    plt.plot(dates,prices)
    plt.title(Stock.symbol + 'Price vs. t')
    plt.savefig(Stock.symbol + 'Hist.png')
    return 

# returns of every day 
def return_series(Stock, show=True):
    '''returns a np array of returns from previous day
    '''
    series = get_prices(Stock)
    if series == None:
        return None
        
    shifted_series = series.shift(1,axis=0)
    rv = series/shifted_series -1
    
    if show:
        rv.hist()
        plt.title('Daily Returns of ' + Stock.symbol)
        plt.show()
    return rv

# log of that daily return 
def log_return_series(Stock,show=True):
    series = get_prices(Stock)
    shifted_series = series.shift(1,axis=0)
    rv = pd.Series(np.log(series/shifted_series))
    if show:
        rv.hist()
        plt.title('Daily Log Returns of ' + Stock.symbol)
        plt.show()
    return rv
# years since company tradable 
def get_years_passed(Stock):
    series = get_prices(Stock)
    # curr and start date
    curr, start = series.index[-1], series.index[0]
    curr, start = str(curr),str(start)
    curr, start = curr.split('-'), start.split('-')
    curr[2], start[2] = curr[2][0:2], start[2][0:2]
    # double map lists and sum
    res = list(map(lambda c,s : int(c) - int(s),curr,start))
    fac = [1,1/12,1/365.25]
    return sum(list(map(lambda r,f : r*f ,fac,res)))

def calc_annulized_volitilty(Stock):
    '''how volitile are daily earnings ?
    '''
    returns = log_return_series(Stock)
    years_past = get_years_passed(Stock)
    entries_per_year = returns.shape[0]/years_past
    return returns.std() * np.sqrt(entries_per_year)

def calc_cagr(Stock):
    '''Calculate Compounded annual growth rate
    '''
    series = get_prices(Stock)
    value_factor = series.iloc[-1] / series.iloc[0]
    year_past = get_years_passed(Stock)
    return (value_factor **(1/year_past)) -1

def calc_sharpe_ratio(Stock, benchmark_rate=1.1):
    '''Risk free rate of return 
    '''
    cagr = calc_cagr(Stock)
    volitily = calc_annulized_volitilty(Stock)
    return (cagr - benchmark_rate)/volitily
