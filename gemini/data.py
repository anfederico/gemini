import time
import requests
import pandas as pd
import datetime as dt

# Local imorts
from . import ptable

tf_mapper = {'MIN':'T','HOUR':'H','DAY':'D','WEEK':'W','MONTH':'M'}

def resample_data(df, integer, htf):
    htf = str(integer)+tf_mapper[htf]
    df['low']    = df.low.resample(htf).min()
    df['high']   = df.high.resample(htf).max()
    df['open']   = df.open.resample(htf).first()
    df['close']  = df.close.resample(htf).last()
    df['volume'] = df.volume.resample(htf).sum()
    return df.dropna()

def available_units():
    return tf_mapper.keys()

def tf_to_secs(freq, unit):
    multiplier = {'MIN'  : 60,
                  'HOUR' : 3600,
                  'DAY'  : 86400,
                  'WEEK' : 604800,
                  'MONTH': 18144000}
    return freq*multiplier[unit]

def px_available_pairs(show=False):
    url = "https://poloniex.com/public?command=returnTicker"
    response = requests.get(url)
    data = response.json()
    tickers = [i for i in data]
    if show:
        print("Available Pairs")
        ptable.tableize(tickers, cols = 4).show()
    return(tickers)

def px_available_tfs():
    print("Available timeframes take the form of 'FREQ-UNIT'")
    print("Any timeframe above 5-MIN is available")
    print("E.g. 5-MIN, 12-HOUR, 3-DAY, 1-WEEK, 1-MONTH")

def px_request_data(pair, tf, start, end):
    end = (end-dt.datetime(1970,1,1)).total_seconds()
    start = (start-dt.datetime(1970,1,1)).total_seconds()

    # Grab the close tf possible given the dates
    url = "https://poloniex.com/public?command=returnChartData&currencyPair={0}&start={1}&end={2}&resolution=auto&period={3}"
    url = url.format(pair, start, end, tf)
    response = requests.get(url)
    df = pd.DataFrame(response.json())

    # Format dataframe
    df['date'] = pd.to_datetime(df.date, unit='s')
    df = df.set_index(df.date, drop=True)
    df = df[['low', 'high', 'open', 'close', 'volume']]
    return df

def cc_available_tfs():
    print("Available timeframes take the form of 'FREQ-UNIT'")
    print("Any timeframe above 1-DAY is available")
    print("E.g. 1-DAY, 3-WEEK, 1-MONTH")

def cc_available_exchanges(show=False):
    url = "https://min-api.cryptocompare.com/data/v2/all/exchanges"
    response = requests.get(url)
    data = response.json()
    exchanges = []
    if data['Response'] == "Success":
        for i in data['Data']:
            try:
                i.encode('utf-8')
                if (data['Data'][i]['is_active']):
                    exchanges.append(i)
            except UnicodeEncodeError:
                pass
    else:
        raise ValueError(data["Message"])

    # Case-insensitive sort
    exchanges = sorted(exchanges, key=lambda s: s.lower())

    if show:
        print("Available Exchanges for Daily Candles...")
        ptable.tableize(exchanges, cols = 4).show()
    else:
        return(exchanges)

def cc_available_pairs(exchange, show=False):
    url = "https://min-api.cryptocompare.com/data/v2/all/exchanges"
    response = requests.get(url)
    data = response.json()
    pairs = []
    if data['Response'] == "Success":
        for i in data['Data']:
            if i == exchange:
                exchange_pairs = data['Data'][i]['pairs']
                for ticker, bases in exchange_pairs.items():
                    pairs += ["{0}_{1}".format(ticker, b) for b in bases]
                break
    else:
        raise ValueError(data["Message"])    

    # Case-insensitive sort
    pairs = sorted(pairs, key=lambda s: s.lower())

    if show:
        print("Available Pairs for {0}...".format(exchange))
        ptable.tableize(pairs, cols = 5).show()
    else:
        return pairs

def cc_request_data(pair, exchange, start, end): 
    params = {'fsym': pair.split("_")[0],
              'tsym': pair.split("_")[1],
              'toTs': (end-dt.datetime(1970,1,1)).total_seconds(),
              'limit': 2000,
              'aggregate': 1,
              'e': exchange}
    response = requests.get('https://min-api.cryptocompare.com/data/histoday', params=params)
    data = response.json()
    
    if data['Response'] == "Success":
        df = pd.DataFrame(data['Data'])
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df['volume'] = df['volumefrom']
        df = df.set_index(df.date, drop=True)
        df = df[['low', 'high', 'open', 'close', 'volume']]
        df = df.loc[(df.index <= end) & (df.index >= start)]
        return(df)
    else:
        raise ValueError(data["Message"])

def get_ltf_candles(pair, tf, start, end):

    # Handling of pair
    if pair not in px_available_pairs(show=False):
        px_available_pairs(show=True)
        raise ValueError("{0} is an invalid pair\n".format(pair))

    # Handling of tf
    tf_s = tf.split("-")
    if len(tf_s) != 2:
        px_available_tfs()
        raise ValueError("{0} is an invalid timeframe".format(tf))
    else:
        tf_1 = int(tf_s[0])
        tf_2 = str(tf_s[1])
    if tf_2 not in available_units():
        print("Try {0}".format(", ".join(available_units())))
        raise ValueError("{0} is an invalid unit of time...".format(tf_2))

    # Find closest compatible timeframe
    tf_secs = tf_to_secs(tf_1, tf_2)
    if tf_secs < 300:
        raise ValueError("Timeframe must be >= 5-MIN") 
    if tf_secs % 300 != 0:
        raise ValueError("Timeframe must be a multiple by 5-MIN")

    # Gets the a comptaible time frame yielding the most data
    tf_secs = [i for i in [300, 900, 1800, 7200, 14400] \
               if i <= tf_secs and tf_secs % i == 0][-1]

    # Handling of dates
    start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    if start >= end:
        raise ValueError("Start date must be earlier than end date")

    # Get data
    df = px_request_data(pair, tf_secs, start, end)

    # Resample to higher time frame if necessary
    df = resample_data(df, tf_1, tf_2)

    df = df.reset_index()

    return df

def get_htf_candles(pair, exchange, tf, start, end):

    # Handling of exchange/pair
    if exchange not in cc_available_exchanges():
        cc_available_exchanges(show=True)
        raise ValueError("{0} is an invalid exchange".format(exchange))
    if pair not in cc_available_pairs(exchange):
        cc_available_pairs(exchange, show=True)
        raise ValueError("{0} is an invalid pair".format(pair))

    # Handling of tf
    tf_s = tf.split("-")
    if len(tf_s) != 2:
        cc_available_tfs()
        raise ValueError("{0} is an invalid timeframe".format(tf))
    else:
        tf_1 = int(tf_s[0])
        tf_2 = str(tf_s[1])

    if tf_2 not in available_units():
        print("Try {0}".format(", ".join(available_units())))
        raise ValueError("{0} is an invalid unit of time...".format(tf_2))

    # Find closest compatible timeframe
    tf_secs = tf_to_secs(tf_1, tf_2)
    if tf_secs < 86400:
        raise ValueError("Timeframe must be >= 1-DAY")
    if tf_secs % 86400 != 0:
        raise ValueError("Timeframe must be a multiple by 1-DAY")

    # Handling of dates
    start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end   = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    if start >= end:
        raise ValueError("Start date must be earlier than end date")

    # Get data
    df = cc_request_data(pair, exchange, start, end)

    # Resample to higher time frame if necessary
    df = resample_data(df, tf_1, tf_2)

    df = df.reset_index()

    return(df)