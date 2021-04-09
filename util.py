import robin_stocks
import metrics

# Generate some test tickers

top_100 = [Stock(i['symbol']) for i in robin_stocks.get_top_100()]
top_movers = [Stock(i['symbol']) for i in robin_stocks.get_top_movers()]
top_down = [Stock(i['symbol']) for i in robin_stocks.get_top_movers_sp500('down')]
reports_soon = [Stock(i['symbol']) for i in robin_stocks.get_watchlist_by_name('Upcoming Earnings')['results']]
saved = [Stock(i['symbol']) for i in robin_stocks.get_watchlist_by_name('My First List')['results']]
arg = [Stock(i['symbol']) for i in robin_stocks.get_watchlist_by_name('Agriculture')['results']]
eng = [Stock(i['symbol']) for i in robin_stocks.get_watchlist_by_name('Energy & Water')['results']]
holding = [Stock(i) for i in list(robin_stocks.account.build_holdings().keys())]
swingers = [Stock(i['symbol']) for i in robin_stocks.get_watchlist_by_name('Daily Movers')['results']]


#Pre-sellected Stocks in holding to sell at value price
SELLING_LIST = {'CCIV': 35,
                'FUBO': 45,
                'CRON': 15,
                'BNGO': 17,
                'ET': 15,
                'WNW': 22,
                'RIOT': 72,
                'NIO': 51,
                'PRLD': 75,
                'TLS': 41,
                'BDSX': 30,
                'NNOX': 56,
                'NOVA': 54}


def check_to_sell(selling=SELLING_LIST):
    holdings = robin_stocks.build_holdings()
    for k, v in selling.items():
        stock = Stock(k)
        # if meets price then sell
        if stock.price > v:
            qsell = float(holdings[k]['quantity'])
            robin_stocks.order(
                k, quantity=qsell, orderType='market', side='sell', trigger='immediate')
            print(f'{stock.symbol} SOLD at {stock.price}')
    return


check_to_sell()


def filterby_long_term_metrics(stocks):
    rv = []
    for s in stocks:
        # try getting a metric for a stock
        try:
            cagr, sratio = metrics.calc_cagr(s), metrics.calc_sharpe_ratio(s)
            if sratio > 0 and cagr > 0:
                rv.append(s)
        except:
            pass
    return rv


def filterby_price(stocks, price_celling):
    rv = []
    for s in stocks:
        if s.update() <= price_celling:
            rv.append(s)
    return rv
