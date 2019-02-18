import bokeh.plotting
import pandas as pd
import numpy as np
import time

# Local imorts
from . import exchange, helpers

class run():
    def __init__(self, data):
        self.data = data

    def start(self, initial_capital, logic):
        
        self.account = exchange.account(initial_capital)

        # Enter backtest ---------------------------------------------  
        for index, today in self.data.iterrows():
    
            # Update account variables
            self.account.date = today['date']
            self.account.equity.append(self.account.total_value(today['close']))

            # Execute trading logic
            lookback = self.data[0:index+1]
            logic(self.account, lookback)

            # Cleanup empty positions
            self.account.purge_positions()     
        # ------------------------------------------------------------

    def results(self):          
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
        print("sells        : {0}".format(sells))
        print("shorts       : {0}".format(shorts))
        print("covers       : {0}".format(covers))
        print("--------------------")
        print("Total Trades : {0}".format(longs + sells + shorts + covers))
        print("\n---------------------------------------")
    
    def chart(self, show_trades=False):
        bokeh.plotting.output_file("chart.html", title="Equity Curve")
        p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title="Equity Curve")
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