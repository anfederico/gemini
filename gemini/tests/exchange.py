from context import gemini

import unittest

class Methods(unittest.TestCase):
    
    def test_errors(self):
        a = gemini.exchange.account(1000)
        self.assertRaises(ValueError, a.enter_position, 'long',  2000, 10)
        self.assertRaises(ValueError, a.enter_position, 'long',  -500, 10)       
        self.assertRaises(ValueError, a.enter_position, 'long', 500, -10)
        # Enter valid position
        a.enter_position('long', 250, 10)
        a.enter_position('short', 250, 10)
        long  = a.positions[0]
        short = a.positions[1]
        self.assertRaises(ValueError, a.close_position, long, 0.5, -20)
        self.assertRaises(ValueError, a.close_position, long, 1.01, 20)
        self.assertRaises(ValueError, a.close_position, long, -0.5, 20)
        self.assertRaises(ValueError, a.close_position, short, 1.01, 20)
        self.assertRaises(ValueError, a.close_position, short, -0.5, 20)

    def test_long(self):
        a = gemini.exchange.account(1000)
        # Win on a long
        a.enter_position('long', 500, 10)
        a.enter_position('long', 500, 10)
        self.assertEqual(a.buying_power, 0)
        self.assertEqual(a.total_value(10), 1000)
        L0 = a.positions[0]
        L1 = a.positions[1]
        a.close_position(L0, 0.5, 20)
        a.close_position(L1, 0.5, 20)
        self.assertEqual(a.buying_power, 1000)
        self.assertEqual(a.total_value(20), 2000)
        a.close_position(L0, 0.5, 40)
        a.close_position(L1, 0.5, 40)
        self.assertEqual(a.buying_power, 2000)
        self.assertEqual(a.total_value(40), 3000)
        # Lose on a long
        a.enter_position('long', 1000, 50)
        L2 = a.positions[2]
        a.close_position(L2, 0.5, 25)
        self.assertEqual(a.buying_power, 1250)
        self.assertEqual(a.total_value(25), 2125)


    def test_short(self):
        a = gemini.exchange.account(1000)
        # Win on a short        
        a.enter_position('short', 500, 10)
        a.enter_position('short', 500, 10)
        self.assertEqual(a.buying_power, 0)
        self.assertEqual(a.total_value(10), 1000)
        S0 = a.positions[0]
        S1 = a.positions[1]
        a.close_position(S0, 0.5, 5)
        a.close_position(S1, 0.5, 5)
        self.assertEqual(a.buying_power, 750)
        self.assertEqual(a.total_value(5), 1500)
        a.close_position(S0, 0.5, 2.5)
        a.close_position(S1, 0.5, 2.5)
        self.assertEqual(a.buying_power, 1187.5)
        self.assertEqual(a.total_value(2.5), 1625)
        # Lose on a short   
        a.enter_position('short', 1000, 2)
        S2 = a.positions[2]
        a.close_position(S2, 0.5, 4)
        self.assertEqual(a.buying_power, 187.5)
        self.assertEqual(a.total_value(4), 587.5)
    
    def test_both(self):
        a = gemini.exchange.account(1000)
        a.enter_position('long',  200, 20)
        a.enter_position('short', 250, 25)
        self.assertEqual(a.buying_power, 550)
        self.assertEqual(a.total_value(25), 1050)
        long  = a.positions[0]
        short = a.positions[1]
        a.close_position(long,  0.5, 40)
        a.close_position(short, 0.5, 12.5)
        self.assertEqual(a.buying_power, 937.5)
        self.assertEqual(a.total_value(12.5), 1187.5)
        a.close_position(long,  1.0, 50)
        a.close_position(short, 1.0, 50)
        self.assertEqual(a.buying_power, 1187.5)
        self.assertEqual(a.total_value(100), 1187.5)
    
    def test_decimals(self):
        # long with decimals
        a = gemini.exchange.account(2)
        a.enter_position('long', 1, 0.00000001)
        self.assertEqual(a.total_value(0.00000002), 3)
        a.close_position(a.positions[0], 1, 0.00000002)
        self.assertEqual(a.buying_power, 3)
        # short with decimals 
        a = gemini.exchange.account(2)
        a.enter_position('short', 1, 0.00000002)
        self.assertEqual(a.total_value(0.00000001), 2.5)
        a.close_position(a.positions[0], 1, 0.00000001)
        self.assertEqual(a.buying_power, 2.5)
    
    def test_commision(self):
        # ten percent commission
        a = gemini.exchange.account(1000)
        a.enter_position('long',  220, 20, commission=0.1)
        a.enter_position('short', 330, 30, commission=0.1) 
        self.assertEqual(a.buying_power, 450)
        self.assertEqual(a.total_value(25), 1050)
        long  = a.positions[0]
        short = a.positions[1]
        a.close_position(long,  0.5, 30, commission=0.1)
        a.close_position(short, 0.5, 30, commission=0.1)
        self.assertEqual(a.buying_power, 720) 
        self.assertEqual(a.total_value(25), 1020)
        a.close_position(long,  1.0, 50, commission=0.1)
        a.close_position(short, 1.0, 30, commission=0.1)
        self.assertEqual(a.buying_power, 1080)
        self.assertEqual(a.total_value(100), 1080)
    
if __name__ == '__main__':
    unittest.main()