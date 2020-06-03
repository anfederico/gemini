<p align="center"><img src="https://github.com/anfederico/Gemini/blob/master/media/logo.png" width="150px"><p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v3.6-blue.svg)
[![Build Status](https://travis-ci.org/anfederico/Gemini.svg?branch=master)](https://travis-ci.org/anfederico/Gemini)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
[![GitHub Issues](https://img.shields.io/github/issues/anfederico/Gemini.svg)](https://github.com/anfederico/Gemini/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-GPL-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
<br>
<p align="center"><img src="https://github.com/anfederico/Gemini/blob/master/media/schematic.gif" width="550px"><p>

## Install

```bash
pip3 install git+git://github.com/anfederico/Gemini.git
```

## Load
```python
from gemini import data, engine, helpers
```

## Examples

*For more information, please refer to the [full documentation](https://gemini-docs.readthedocs.io/en/latest/)*

#### Input Data (Optional)
If you have your own data that has/hasn't been processed, you should conform to the following structure. Basically, load your data into a Pandas dataframe object and be sure to convert the dates to datetime format and include the following lowercase column titles.
```text
                                  date         high          low         open        close
                0  2017-07-08 11:00:00  2480.186778  2468.319314  2477.279567  2471.314030  
                1  2017-07-08 11:30:00  2471.314030  2455.014057  2471.202796  2458.073602
                2  2017-07-08 12:00:00  2480.000000  2456.000000  2458.073602  2480.000000 
                3  2017-07-08 12:30:00  2489.004639  2476.334333  2479.402768  2481.481258
                4  2017-07-08 13:00:00  2499.000000  2476.621873  2481.458643  2491.990000 
                5  2017-07-08 13:30:00  2503.503479  2490.314610  2492.440289  2496.005562
                6  2017-07-08 14:00:00  2525.000000  2491.062741  2494.449524  2520.775500
                7  2017-07-08 14:30:00  2521.500036  2510.000000  2520.775500  2518.450645
                8  2017-07-08 15:00:00  2519.817394  2506.054360  2518.451000  2514.484009
```

```
 4195.81 ┤                                                                                         
 4161.76 ┤                                   ╭─╮                                                   
 4127.72 ┤                                   │ ╰╮                                                  
 4093.67 ┤                                   │  │                                                  
 4059.62 ┤                ╭╮                 │  ╰╮                                                 
 4025.58 ┤              ╭─╯╰╮╭╮              │   ╰─╮                                               
 3991.53 ┤             ╭╯   ╰╯│        ╭╮╭╮  │     │                                               
 3957.48 ┤             │      ╰╮      ╭╯╰╯│╭╮│     │                                               
 3923.44 ┤             │       │      │   ╰╯╰╯     │                                               
 3889.39 ┤             │       │   ╭╮╭╯            │                     ╭───╮                     
 3855.34 ┤             │       │  ╭╯││             │                     │   ╰─╮                   
 3821.30 ┤       ╭╮    │       ╰──╯ ╰╯             │     ╭╮   ╭╮        ╭╯     ╰╮  ╭╮ ╭╮          ╭
 3787.25 ┤       ││    │                           │╭╮  ╭╯╰╮ ╭╯│        │       │  │╰─╯╰─╮        │
 3753.21 ┤     ╭╮│╰─╮  │                           ││╰╮╭╯  ╰╮│ │╭──╮    │       │ ╭╯     ╰─╮      │
 3719.16 ┤     │╰╯  │╭─╯                           ╰╯ ╰╯    ╰╯ ╰╯  │    │       ╰─╯        │  ╭─╮╭╯
 3685.11 ┤    ╭╯    ╰╯                                             │    │                  ╰──╯ ╰╯ 
 3651.07 ┤    │                                                    │   ╭╯                          
 3617.02 ┤    │                                                    ╰╮╭─╯                           
 3582.97 ┤    │                                                     ╰╯                             
 3548.93 ┤╮  ╭╯                                                                                    
 3514.88 ┼╰╮╭╯                                                                                     
 3480.83 ┤ ╰╯                                                                                      
```

#### Data Retrieval
If you don't have your own data, we've included useful functions for grabbing low and high timeframe historical data from crypto exchanges. These helper functions will automatically resample your datasets to any desired timeframe and return a Gemini-compatible dataframe.
```python
# Higher timeframes (>= daily)
df = data.get_htf_candles("BTC_USD", "Bitfinex", "3-DAY", "2019-01-12 00:00:00", "2019-02-01 00:00:00")

# Lower timeframes (< daily)
df = data.get_ltf_candles("USDC_BTC", "30-MIN", "2019-01-12 00:00:00", "2019-02-01 00:00:00")
```

#### Loading Data into the Backtester
```python
backtest = engine.backtest(df)
```

#### Creating your Strategy
In addition to loading the data, you must define the strategy you want to test. To do this, we'll create a logic function that can be passed to the backtester when you start. The backtester will proceed step-wise through the dataset, copying the current/past datapoints into a variable called "Lookback" to prevent lookahead bias. If the data hasn't already been processed, you may process it within the logic function (this makes the simulation more accurate but significantly increases runtime). You can then use the helper class called "Period" to conveniently reference current and past datapoints. With those, you may execute long, sell, short, and cover positions directly on the "Account" class based on your strategy.


```python
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

# Start backtesting custom logic with 1000 (BTC) intital capital
backtest.start(1000, logic)
```

#### Analyzing your Strategy
After the backtest, you can analyze your strategy by printing the results to console. As of now, these include simple statistics of your run but we plan to implement more complicated metrics for a stronger understanding of performance.

```python
backtest.results()
```

```text
Buy and Hold : -3.03%
Net Profit   : -30.26
Strategy     : 40.0%
Net Profit   : 400.01
Longs        : 156
Sells        : 137
Shorts       : 0
Covers       : 0
--------------------
Total Trades : 293
```

#### Visualizing the Equity Curve
You can visualize the performance of your strategy by comparing the equity curve with a buy and hold baseline. The equity curve simply tracks your account value throughout the backtest and will optionally show where your algorithm made its trades including longs, sells, shorts, and covers.
```python
backtest.chart()
```

<p align="center"><img src="https://raw.githubusercontent.com/anfederico/Gemini/master/media/example.png"><p>

#### Real Example
Please take a look at our real example of a [mean reversion strategy](https://github.com/anfederico/Gemini/blob/master/examples/mean_reversion.ipynb)
