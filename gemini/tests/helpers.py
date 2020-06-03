from gemini.gemini_core import helpers

import unittest

class Methods(unittest.TestCase):

    def test_helpers(self):
        self.assertEqual(helpers.percent_change(50, 238), 3.76)
        self.assertEqual(helpers.profit(50, 2.4), 120)

if __name__ == '__main__':
    unittest.main()