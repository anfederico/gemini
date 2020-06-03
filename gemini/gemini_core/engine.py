import bokeh.plotting
import pandas as pd
import numpy as np
import warnings
import time

# Local imorts
from . import exchange, helpers

class backtest():
    """An object representing a backtesting simulation."""
    def __init__(self, data):
        """Initate the backtest.

        :param data: An HLOCV+ pandas dataframe with a datetime index
        :type data: pandas.DataFrame

        :return: A bactesting simulation
        :rtype: backtest
        """  
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas dataframe")

        missing = set(['high', 'low', 'open', 'close', 'volume'])-set(data.columns)
        if len(missing) > 0:
            msg = "Missing {0} column(s), dataframe must be HLOCV+".format(list(missing))
            warnings.warn(msg)

        self.data = data

    def start(self, initial_capital, logic):
        """Start backtest.

        :param initial_capital: Starting capital to fund account
        :type initial_capital: float
        :param logic: A function that will be applied to each lookback period of the data
        :type logic: function

        :return: A bactesting simulation
        :rtype: backtest
        """
        self.tracker = []
        self.account = exchange.account(initial_capital)

        # Enter backtest ---------------------------------------------  
        for index, today in self.data.iterrows():
    
            date = today['date']
            equity = self.account.total_value(today['close'])

            # Handle stop loss
            for p in self.account.positions:
                if p.type == "long":
                    if p.stop_hit(today['low']):
                        self.account.close_position(p, 1.0, today['low'])
                if p.type == "short":
                    if p.stop_hit(today['high']):
                        self.account.close_position(p, 1.0, today['high'])

            self.account.purge_positions()

            # Update account variables
            self.account.date = date
            self.account.equity.append(equity)

            # Equity tracking
            self.tracker.append({'date': date, 
                                 'benchmark_equity' : today['close'],
                                 'strategy_equity' : equity})

            # Execute trading logic
            lookback = self.data[0:index+1]
            logic(self.account, lookback)

            # Cleanup empty positions
            self.account.purge_positions()     
        # ------------------------------------------------------------

        # For pyfolio
        df = pd.DataFrame(self.tracker)
        df['benchmark_return'] = (df.benchmark_equity-df.benchmark_equity.shift(1))/df.benchmark_equity.shift(1)
        df['strategy_return'] = (df.strategy_equity-df.strategy_equity.shift(1))/df.strategy_equity.shift(1)
        df.index = df['date']
        del df['date']
        return df

    def results(self):   
        """Print results"""           
        print("-------------- Results ----------------\n")
        being_price = self.data.iloc[0]['open']
        final_price = self.data.iloc[-1]['close']

        pc = helpers.percent_change(being_price, final_price)
        print("Buy and Hold : {0}%".format(round(pc*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.initial_capital, pc), 2)))
        
        pc = helpers.percent_change(self.account.initial_capital, self.account.total_value(final_price))
        print("Strategy     : {0}%".format(round(pc*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.initial_capital, pc), 2)))

        longs  = len([t for t in self.account.opened_trades if t.type == 'long'])
        sells  = len([t for t in self.account.closed_trades if t.type == 'long'])
        shorts = len([t for t in self.account.opened_trades if t.type == 'short'])
        covers = len([t for t in self.account.closed_trades if t.type == 'short'])

        print("Longs        : {0}".format(longs))
        print("Sells        : {0}".format(sells))
        print("Shorts       : {0}".format(shorts))
        print("Covers       : {0}".format(covers))
        print("--------------------")
        print("Total Trades : {0}".format(longs + sells + shorts + covers))
        print("\n---------------------------------------")
    
    def chart(self, show_trades=False, title="Equity Curve"):
        """Chart results.

        :param show_trades: Show trades on plot
        :type show_trades: bool
        :param title: Plot title
        :type title: str
        """     
        bokeh.plotting.output_file("chart.html", title=title)
        p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title=title)
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'
        shares = self.account.initial_capital/self.data.iloc[0]['open']
        base_equity = [price*shares for price in self.data['open']]      
        p.line(self.data['date'], base_equity, color='#CAD8DE', legend='Buy and Hold')
        p.line(self.data['date'], self.account.equity, color='#49516F', legend='Strategy')
        p.legend.location = "top_left"

        if show_trades:
            for trade in self.account.opened_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='green', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='red', alpha=0.5)
                except:
                    pass

            for trade in self.account.closed_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='blue', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='orange', alpha=0.5)
                except:
                    pass
        
        bokeh.plotting.show(p)
