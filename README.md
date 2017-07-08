<p align="center"><img src="https://raw.githubusercontent.com/Crypto-AI/Gemini/master/media/gemini-logo.png" width="100px"><p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v2.7%20%2F%20v3.6-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
[![GitHub Issues](https://img.shields.io/github/issues/Crypto-AI/Gemini.svg)](https://github.com/anfederico/flaskex/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<br><br>

## Account Class
The account class represents (as you probably guessed) an account on an arbitrary exchange. The account starts with capital and can buy/sell the asset in what is simulated as open positions.

## Run Class
The run class is the meat and bones of the backtester. It starts off with a fresh account class, a dataset (preprocessed with your signals), and some logic as to how the account class should behave. You'll set a lookback period and the run class will iterate through the dataset and apply the custom logic on the lookback period. At the end of the dataset, you can graph the equity curve along with indicators of where positions were opened and closed.

## Contributing
Please take a look at our [contributing](https://github.com/Crypto-AI/Gemini/blob/master/CONTRIBUTING.md) guidelines if you're interested in helping!

## Examples

#### Input Data (Pandas Dataframe)
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
#### Optional Setup
If you don't have your own data, we've included a useful function for grabbing historical charting data from the Poloniex exchange. In this example, we'll trade the BTC/ETH pair on a 30 minute timeframe. For demonstration purposes, we want to ignore the last 30 days of data in our backtest and look at the 3 months before then. With the poloniex helper function, it's easy to do that.
```python
import pandas as pd
import poloniex as px

pair = "BTC_ETH"    # Use ETH pricing data on the BTC market
period = 1800       # Use 1800 second candles
daysBack = 30       # Grab data starting 30 days ago
daysData = 90       # From there collect 90 days of data

# Request data from Poloniex
data = px.getPast(pair, period, daysBack, daysData)

# Convert to dataframe with datetime format
data = pd.DataFrame(data)
data['date'] = pd.to_datetime(data['date'], unit='s')

# Load the data into a backtesting class called Run
r = gemini.Run(data)

# Start backtesting with 100 (BTC) intital capital
# You'll need to define a logic function first (next topic)
r.Start(100, Logic)

# Show results
r.Results()

# Visualize results
r.Chart(ShowTrades=True)

```

