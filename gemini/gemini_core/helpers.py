import math

def percent_change(d1, d2):
    """Calculate percent change between two numbers.

    :param d1: Starting number
    :type d1: float
    :param d2: Ending number
    :type d2: float

    :return: Percent change
    :rtype: float
    """
    return (d2 - d1) / d1

def profit(initial_capital, multiplier):
    """Calculate the profit based on multiplier factor.

    :param initial_capital: Initial amount of capital
    :type initial_capital: float
    :param multiplier: Multiplying factor
    :type multiplier: float

    :return: Profit
    :rtype: float
    """
    return initial_capital * (multiplier + 1.0) - initial_capital

def rnd(value, prec=8):
    """
    Return good float value
    :param value:
    :param prec: precession
    :return:
    """
    round_prec = 10 ** prec
    rounded = math.ceil(value * round_prec)
    return rounded / round_prec

class period():
    """An object representing a period of time."""
    def __init__(self, data):
        self.data = data

    def loc(self, i):
        """Look back to previous indices.

        :param i: Number of indices to look book
        :type i: int

        :return: A lookback period
        :rtype: period
        """
        if i > 0:
            raise ValueError("Error: Cannot look forward!")
        if i <= -(len(self.data)):
            raise ValueError("Error: Cannot look too far back!")
        return self.data.iloc[i-1]
