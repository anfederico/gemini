# Load gemini
from context import gemini
from gemini  import data, engine, helpers

# Global Imports
import pandas as pd
import numpy as np

# Build mean reversion strategy
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
        lookback = helpers.Period(lookback)
        today = lookback.loc(0)
        
        # Selling
        if today.touch_upper:
            ExitPrice = today.upper
            for Position in account.Positions:  
                if Position.Type == 'Long':
                    account.ClosePosition(Position, 1, ExitPrice)

        if today.crossing_up:
            ExitPrice = today.close
            for Position in account.Positions:  
                if Position.Type == 'Long':
                    account.ClosePosition(Position, 1, ExitPrice)
                    
        # Buying
        if today.touch_lower | today.crossing_dn:
            Risk         = 1
            EntryPrice   = today.lower
            EntryCapital = account.BuyingPower*Risk
            if EntryCapital > 0:
                account.EnterPosition('Long', EntryCapital, EntryPrice)
     
        if today.crossing_dn:
            Risk         = 1
            EntryPrice   = today.close
            EntryCapital = account.BuyingPower*Risk
            if EntryCapital > 0:
                account.EnterPosition('Long', EntryCapital, EntryPrice)    
    
    except Exception as e:
        print(e)
        pass # Handles lookback errors in beginning of dataset

# Apply strategy to example
df = pd.read_csv("data/BTC_USD.csv", header=0, index_col=0)
df = bands(df)
df = touches(df)

# Backtest
r = engine.Run(df)
r.Start(1000, logic)
r.Results()