.. _using-gemini-page:

.. image:: ../media/logo.png
  :width: 100
  :align: center

Using Gemini
============

.. toctree::
   :maxdepth: 3
   :caption: Contents:

Initialize Backtest
-------------------
Once your import or download data, you must initialize that backtesting engine with your data. This will simply create a backtesting class with your data pre-loaded.

.. code-block:: python

    import data

    # Higher timeframes (>= daily)
    df = data.get_htf_candles("BTC_USD", "Bitfinex", "3-DAY", "2019-01-12 00:00:00", "2019-02-01 00:00:00")

    # Lower timeframes (< daily)
    df = data.get_ltf_candles("USDC_BTC", "30-MIN", "2019-01-12 00:00:00", "2019-02-01 00:00:00")

    # Loading data into the backtester
    import engine

    backtest = engine.backtest(df)

Define Stategy
--------------
In addition to loading the data, you must define the strategy you want to test. To do this, we'll create a logic function that can be passed to the backtester when you start. The backtester will proceed step-wise through the dataset, copying the current/past datapoints into a variable called "Lookback" to prevent lookahead bias. If the data hasn't already been processed, you may process it within the logic function (this makes the simulation more accurate but significantly increases runtime). You can then use the helper class called "Period" to conveniently reference current and past datapoints. With those, you may execute long, sell, short, and cover positions directly on the "Account" class based on your strategy.

Basic
~~~~~
A basic mock strategy example

.. code-block:: python

    def logic(account, lookback):
        try:
            # Process dataframe to collect signals
            lookback = helpers.get_signals(lookback)
            
            # Load into period class to simplify indexing
            lookback = helpers.period(lookback)
            
            today = lookback.loc(0) # Current candle
            yesterday = lookback.loc(-1) # Previous candle
            
            if today['signal'] == "down":
                if yesterday['signal'] == "down":
                    exit_price = today['close']
                    for position in acount.positions:
                        if position.type == 'long':
                            account.close_position(position, 0.5, exit_price)

            if today['signal'] == "up":
                if yesterday['signal'] == "up":
                    risk          = 0.03
                    entry_price   = today['close']
                    entry_capital = account.buying_power*risk
                    if entry_capital >= 0:
                        account.enter_position('long', entry_capital, entry_price)
         
        except ValueError: 
            pass # Handles lookback errors in beginning of dataset

Advanced
~~~~~~~~
A real mean reversion strategy example

.. code-block:: python

    import pandas as pd
    import numpy as np
    from talib.abstract import *

    def bands(df, timeperiod=26, nbdevup=2.6, nbdevdn=2.6, matype=0):
        cols = ['high', 'low', 'open', 'close', 'volume']
        HLOCV = {key: df[key].values for key in df if key in cols}
        u, m, l = BBANDS(HLOCV, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)
        df['upper']  = u
        df['middle'] = m
        df['lower']  = l
        return df

    def touches(df):
        df['touch_upper'] = df.high >= df.upper
        df['touch_lower'] = df.low  <= df.lower
        df['crossing_dn'] = (df.close < df.middle) & (df.open > df.middle)
        df['crossing_up'] = (df.close > df.middle) & (df.open < df.middle)
        return df

    def logic(account, lookback):
        try:
            lookback = bands(lookback)
            lookback = touches(lookback)
            lookback = helpers.period(lookback)
            today = lookback.loc(0)

            # Selling
            if today.touch_upper:
                exit_price = today.upper
                for position in account.positions:
                    if position.type_ == 'long':
                        account.close_position(position, 1, exit_price)

            if today.crossing_up:
                exit_price = today.close
                for position in account.positions:
                    if position.type_ == 'long':
                        account.close_position(position, 1, exit_price)

            # Buying
            if today.touch_lower | today.crossing_dn:
                risk          = 1
                entry_price   = today.lower
                entry_capital = account.buying_power*risk
                if entry_capital > 0:
                    account.enter_position('long', entry_capital, entry_price)

            if today.crossing_dn:
                risk          = 1
                entry_price   = today.close
                entry_capital = account.buying_power*risk
                if entry_capital > 0:
                    account.enter_position('long', entry_capital, entry_price)

        except Exception as e:
            print(e)
        pass # Handles lookback errors in beginning of dataset

Run Backtest
------------
Running the backtest is as simple as running the following one-liner.

.. code-block:: python

    backtest.start(1000, logic)

.. image:: ../media/schematic.gif
  :width: 500
  :align: center


Performance Statistics
----------------------
After the backtest, you can analyze your strategy by printing the results to console. As of now, these include simple statistics of your run but we plan to implement more complicated metrics for a stronger understanding of performance.

.. code-block:: python

    backtest.results()

.. parsed-literal::

    -------------- Results ----------------
    
    Buy and Hold : 534.15%
    Net Profit   : 5341.47
    Strategy     : 3811.75%
    Net Profit   : 38117.46
    Longs        : 30
    sells        : 31
    shorts       : 0
    covers       : 0
    --------------------
    Total Trades : 61
    
    ---------------------------------------

Equity Curve
------------
You can visualize the performance of your strategy by comparing the equity curve with a buy and hold baseline. The equity curve simply tracks your account value throughout the backtest and will optionally show where your algorithm made its trades including longs, sells, shorts, and covers.

.. code-block:: python

    backtest.chart()

.. image:: ../media/example.png
  :width: 700
  :align: center
