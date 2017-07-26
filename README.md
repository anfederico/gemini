<p align="center"><img src="https://github.com/Crypto-AI/Gemini/blob/master/media/logo.png" width="150px"><p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v2.7%20%2F%20v3.6-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
[![GitHub Issues](https://img.shields.io/github/issues/Crypto-AI/Gemini.svg)](https://github.com/Crypto-AI/Gemini/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
<br>
<p align="center"><img src="https://github.com/Crypto-AI/Gemini/blob/master/media/schematic.gif" width="550px"><p>


## Examples

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

#### Loading Data into the Backtester
If you don't have your own data, we've included a useful function for grabbing historical charting data from the Poloniex exchange. In this example, we'll trade the BTC/ETH pair on a 30 minute timeframe. To demonstrate the versatility of our data grabber, we will ignore the last 30 days of data in our backtest and look at the 60 days before then. With the poloniex helper function, it's easy to do that.
```python
import pandas as pd
import poloniex as px

pair = "BTC_ETH"    # Use ETH pricing data on the BTC market
period = 1800       # Use 1800 second candles
daysBack = 30       # Grab data starting 30 days ago
daysData = 60       # From there collect 60 days of data

# Request data from Poloniex
data = px.getPast(pair, period, daysBack, daysData)

# Convert to Pandas dataframe with datetime format
data = pd.DataFrame(data)
data['date'] = pd.to_datetime(data['date'], unit='s')

# Load the data into a backtesting class called Run
r = gemini.Run(data)
```

#### Creating your Strategy
In addition to loading the data, you must define the strategy you want to test. To do this, we'll create a logic function that can be passed to the backtester when you start. The backtester will proceed step-wise through the dataset, copying the current/past datapoints into a variable called "Lookback" to prevent lookahead bias. If the data hasn't already been processed, you may process it within the logic function (this makes the simulation more accurate but significantly increases runtime). You can then use the helper class called "Period" to conveniently reference current and past datapoints. With those, you may execute long, sell, short, and cover positions directly on the "Account" class based on your strategy.


```python
import helpers

def Logic(Account, Lookback):
    try:
        # Process dataframe to collect signals
        Lookback = helpers.getSignals(Lookback)
        
        # Load into period class to simplify indexing
        Lookback = helpers.Period(Lookback)
        
        Today = Lookback.loc(0) # Current candle
        Yesterday = Lookback.loc(-1) # Previous candle
        
        if Today['signal'] == "down":
            if Yesterday['signal'] == "down":
                ExitPrice = Today['close']
                for Position in Account.Positions:  
                    if Position.Type == 'Long':
                        Account.ClosePosition(Position, 0.5, ExitPrice)

        if Today['signal'] == "up":
            if Yesterday['signal'] == "up":
                Risk         = 0.03
                EntryPrice   = Today['close']
                EntryCapital = Account.BuyingPower*Risk
                if EntryCapital >= 0:
                    Account.EnterPosition('Long', EntryCapital, EntryPrice)
     
    except ValueError: 
        pass # Handles lookback errors in beginning of dataset


# Start backtesting custom logic with 1000 (BTC) intital capital
r.Start(1000, Logic)
```

#### Analyzing your Strategy
After the backtest, you can analyze your strategy by printing the results to console. As of now, these include simple statistics of your run but we plan to implement more complicated metrics for a stronger understanding of performance.

```python
r.Results()
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
r.Chart(ShowTrades=False)
```
<p align="center"><img src="https://raw.githubusercontent.com/Crypto-AI/Gemini/master/media/example.png"><p>

## Contributing
Please take a look at our [contributing](https://github.com/Crypto-AI/Gemini/blob/master/CONTRIBUTING.md) guidelines if you're interested in helping!
