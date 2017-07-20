import pandas as pd
import poloniex as px
import pivots
import gemini
import helpers
from datetime import datetime

def Logic(Account, Lookback):
    try:
        # Process dataframe to collect signals
        # Lookback = process(Lookback)
        
        # Load into period class to simplify indexing
        Lookback = helpers.Period(Lookback)
        
        Today = Lookback.loc(0) # Current candle
        
        if Today['date'] >= datetime.strptime('2017-05-01', '%Y-%m-%d'):
            if Today['color'] == 'darkOrange':
                ExitPrice = Today['close']
                for Position in Account.Positions:  
                    if Position.Type == 'Long':
                        Account.ClosePosition(Position, 0.2, ExitPrice)

        if Today['color'] == 'darkBlue':
            Risk         = 0.03
            EntryPrice   = Today['close']
            AccountValue = Account.TotalValue(EntryPrice)
            EntryCapital = AccountValue*Risk
            if EntryCapital >= 0:
                try: 
                    Account.EnterPosition('Long', EntryCapital, EntryPrice)
                except ValueError: 
                    pass
    except ValueError: pass


# -----------------------------------------------

# Collect data from Poloniex

pair = "BTC_ETH"
period = 1800 # 1800 sec candles (30 min timeframe)
daysBack = 60 # Grab data starting 30 days ago
daysData = 45 # From there collect 90 days of data
data = px.getPast(pair, period, daysBack, daysData)

# Convert to dataframe with dates
data = pd.DataFrame(data)

data['date'] = pd.to_datetime(data['date'], unit='s')

data = pivots.getColors(data, 8)

r = gemini.Run(data)
r.Start(1000, Logic)
r.Results()
r.Chart()
