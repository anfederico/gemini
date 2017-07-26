import pandas as pd
import poloniex as px
import helpers

pair = "BTC_ETH"    # Use ETH pricing data on the BTC market
period = 1800       # Use 1800 second candles
daysBack = 30       # Grab data starting 30 days ago
daysData = 60       # From there collect 60 days of data

# Request data from Poloniex
data = px.getPast(pair, period, daysBack, daysData)

# Convert to Pandas dataframe with datetime format
data = pd.DataFrame(data)
data['date'] = pd.to_datetime(data['date'], unit='s')

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

# Load the data into a backtesting class called Run
r = gemini.Run(data)

# Start backtesting custom logic with 1000 (BTC) intital capital
r.Start(1000, Logic)

r.Results()
r.Chart(ShowTrades=False)
