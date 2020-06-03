from gemini.gemini_core import engine, helpers

import unittest

# Global Imports
import os
import pandas as pd

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

class Methods(unittest.TestCase):

    def test_engine(self):

        path = os.path.dirname( __file__ ).rstrip("/tests")
        data_path = os.path.join(path, 'examples/data/BTC_USD.csv')

        df = pd.read_csv(data_path, header=0, index_col=0)
        df = bands(df)
        df = touches(df)

        backtest = engine.backtest(df)
        results = backtest.start(1000, logic)

        self.assertEqual(results.tail(1).values.tolist()[0], [9659.09950232, 6865.28571855189, -0.025089364796339712, 0.0])

if __name__ == '__main__':
    unittest.main()
