
.. code:: ipython3

    # Load gemini
    from context import gemini
    from gemini  import data, engine, helpers
    
    # Global Imports
    import pandas as pd
    import numpy as np
    
    # Build mean reversion strategy
    from talib.abstract import *

.. code:: ipython3

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

.. code:: ipython3

    def logic(account, lookback):
        try:
            lookback = helpers.period(lookback)
            today = lookback.loc(0)
            
            # Selling
            if today.touch_upper:
                exit_price = today.upper
                for position in account.positions:  
                    if position.type == 'long':
                        account.close_position(position, 1, exit_price)
    
            if today.crossing_up:
                exit_price = today.close
                for position in account.positions:  
                    if position.type == 'long':
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

.. code:: ipython3

    # Apply strategy to example
    df = pd.read_csv("data/BTC_USD.csv", header=0, index_col=0)
    df['date'] = pd.to_datetime(df['date'])
    df.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>date</th>
          <th>low</th>
          <th>high</th>
          <th>open</th>
          <th>close</th>
          <th>volume</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>2017-02-15 16:00:00</td>
          <td>1009.70000399</td>
          <td>1018.00000000</td>
          <td>1010.09990931</td>
          <td>1014.83589839</td>
          <td>225268.43507453</td>
        </tr>
        <tr>
          <th>1</th>
          <td>2017-02-16 00:00:00</td>
          <td>1011.60000000</td>
          <td>1032.13660417</td>
          <td>1011.60000000</td>
          <td>1021.75360065</td>
          <td>316925.44590378</td>
        </tr>
        <tr>
          <th>2</th>
          <td>2017-02-16 08:00:00</td>
          <td>1021.75360206</td>
          <td>1039.95700000</td>
          <td>1024.70000000</td>
          <td>1035.00000000</td>
          <td>215385.30718065</td>
        </tr>
        <tr>
          <th>3</th>
          <td>2017-02-16 16:00:00</td>
          <td>1033.50000001</td>
          <td>1045.00000000</td>
          <td>1035.00000000</td>
          <td>1039.49925987</td>
          <td>431951.93722578</td>
        </tr>
        <tr>
          <th>4</th>
          <td>2017-02-17 00:00:00</td>
          <td>1035.50000000</td>
          <td>1044.99999989</td>
          <td>1039.49925949</td>
          <td>1043.99999999</td>
          <td>162001.23700635</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    df = bands(df)
    df = touches(df)

.. code:: ipython3

    backtest = engine.backtest(df)

.. code:: ipython3

    output = backtest.start(1000, logic)
    output.tail()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>benchmark_equity</th>
          <th>strategy_equity</th>
          <th>benchmark_return</th>
          <th>strategy_return</th>
        </tr>
        <tr>
          <th>date</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-10-30 16:00:00</th>
          <td>6125.00000000</td>
          <td>39117.46414278</td>
          <td>0.00744468</td>
          <td>0.00000000</td>
        </tr>
        <tr>
          <th>2017-10-31 00:00:00</th>
          <td>6106.99999987</td>
          <td>39117.46414278</td>
          <td>-0.00293878</td>
          <td>0.00000000</td>
        </tr>
        <tr>
          <th>2017-10-31 08:00:00</th>
          <td>6355.00000010</td>
          <td>39117.46414278</td>
          <td>0.04060914</td>
          <td>0.00000000</td>
        </tr>
        <tr>
          <th>2017-10-31 16:00:00</th>
          <td>6450.02162843</td>
          <td>39117.46414278</td>
          <td>0.01495226</td>
          <td>0.00000000</td>
        </tr>
        <tr>
          <th>2017-11-01 00:00:00</th>
          <td>6405.52060937</td>
          <td>39117.46414278</td>
          <td>-0.00689936</td>
          <td>0.00000000</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

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


Feed results into Pyfolio analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    import pyfolio as pf
    %matplotlib inline
    
    # silence warnings
    import warnings
    warnings.filterwarnings('ignore')

.. code:: ipython3

    pf.create_returns_tear_sheet(output['strategy_return'], benchmark_rets=output['benchmark_return'])



.. raw:: html

    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;"><th>Start date</th><td colspan=2>2017-02-15</td></tr>
        <tr style="text-align: right;"><th>End date</th><td colspan=2>2017-11-01</td></tr>
        <tr style="text-align: right;"><th>Total months</th><td colspan=2>36</td></tr>
        <tr style="text-align: right;">
          <th></th>
          <th>Backtest</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Annual return</th>
          <td>228.9%</td>
        </tr>
        <tr>
          <th>Cumulative returns</th>
          <td>3811.7%</td>
        </tr>
        <tr>
          <th>Annual volatility</th>
          <td>47.9%</td>
        </tr>
        <tr>
          <th>Sharpe ratio</th>
          <td>2.72</td>
        </tr>
        <tr>
          <th>Calmar ratio</th>
          <td>9.38</td>
        </tr>
        <tr>
          <th>Stability</th>
          <td>0.96</td>
        </tr>
        <tr>
          <th>Max drawdown</th>
          <td>-24.4%</td>
        </tr>
        <tr>
          <th>Omega ratio</th>
          <td>2.70</td>
        </tr>
        <tr>
          <th>Sortino ratio</th>
          <td>6.84</td>
        </tr>
        <tr>
          <th>Skew</th>
          <td>NaN</td>
        </tr>
        <tr>
          <th>Kurtosis</th>
          <td>NaN</td>
        </tr>
        <tr>
          <th>Tail ratio</th>
          <td>2.50</td>
        </tr>
        <tr>
          <th>Daily value at risk</th>
          <td>-5.5%</td>
        </tr>
        <tr>
          <th>Alpha</th>
          <td>0.99</td>
        </tr>
        <tr>
          <th>Beta</th>
          <td>0.44</td>
        </tr>
      </tbody>
    </table>



.. raw:: html

    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th>Worst drawdown periods</th>
          <th>Net drawdown in %</th>
          <th>Peak date</th>
          <th>Valley date</th>
          <th>Recovery date</th>
          <th>Duration</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>24.42</td>
          <td>2017-09-12</td>
          <td>2017-09-15</td>
          <td>2017-09-21</td>
          <td>8</td>
        </tr>
        <tr>
          <th>1</th>
          <td>23.89</td>
          <td>2017-07-10</td>
          <td>2017-07-16</td>
          <td>2017-07-20</td>
          <td>9</td>
        </tr>
        <tr>
          <th>2</th>
          <td>19.66</td>
          <td>2017-06-13</td>
          <td>2017-06-15</td>
          <td>2017-06-25</td>
          <td>9</td>
        </tr>
        <tr>
          <th>3</th>
          <td>18.51</td>
          <td>2017-03-17</td>
          <td>2017-03-25</td>
          <td>2017-04-16</td>
          <td>20</td>
        </tr>
        <tr>
          <th>4</th>
          <td>9.61</td>
          <td>2017-05-28</td>
          <td>2017-05-28</td>
          <td>2017-05-29</td>
          <td>1</td>
        </tr>
      </tbody>
    </table>



.. image:: output_10_2.png

