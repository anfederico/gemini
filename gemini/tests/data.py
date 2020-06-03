from gemini.gemini_core import data

import unittest

class Methods(unittest.TestCase):

    def test_ltf_errors(self):
        self.assertRaises(ValueError, data.get_ltf_candles, "UDSC_BTC", "2-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "2HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "2-H", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "4-MIN", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "7-MIN", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "2-HOUR", "2019/01/12 12:00:00", "2019/02/01 00:00:00")
        self.assertRaises(ValueError, data.get_ltf_candles, "USDC_BTC", "2-HOUR", "2019-03-12 12:00:00", "2019-02-01 00:00:00")
    
    def test_ltf(self):
        df = data.get_ltf_candles("USDC_BTC", "8-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertEqual(list(df.columns), ['date', 'low', 'high', 'open', 'close', 'volume'])
        self.assertEqual((df.date[1]-df.date[0]).total_seconds(), 28800)
        self.assertEqual(len(df), 59)

    def test_htf_errors(self):
        self.assertRaises(ValueError, data.get_htf_candles, "USDC_BTC", "Finex", "1-DAY", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "USDC_BTC", "Bitfinex", "1-DAY", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "1DAY", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "1-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "1-D", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "12-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "25-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "2-HOUR", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "2-DAY", "2019/01/12 12:00:00", "2019/02/01 00:00:00")
        self.assertRaises(ValueError, data.get_htf_candles, "BTC_USD", "Bitfinex", "2-DAY", "2019-03-12 12:00:00", "2019-02-01 00:00:00")

    def test_htf(self):
        df = data.get_htf_candles("BTC_USD", "Bitfinex", "2-DAY", "2019-01-12 12:00:00", "2019-02-01 00:00:00")
        self.assertEqual(list(df.columns), ['date', 'low', 'high', 'open', 'close', 'volume'])
        self.assertEqual((df.date[1]-df.date[0]).total_seconds(), 172800)
        self.assertEqual(len(df), 10)

if __name__ == '__main__':
    unittest.main()