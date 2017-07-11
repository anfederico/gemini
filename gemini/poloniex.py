import requests
import time

def getNow(pair):
    return requests.get('https://poloniex.com/public?command=returnTicker').json()[pair]

def getPast(pair, period, daysBack, daysData):
    now = int(time.time())
    end = now-(24*60*60*daysBack)
    start = end-(24*60*60*daysData)
    base = 'https://poloniex.com/public?command=returnChartData&currencyPair='
    response = requests.get('{0}{1}&start={2}&end={3}&period={4}'.format(base, pair, start, end, period))
    return response.json()