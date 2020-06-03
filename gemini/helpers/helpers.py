import math


def percent_change(d1, d2):
    """
    calculate percent change between two values
    :param d1:
    :param d2:
    :return:
    """
    return (d2 - d1) / d1


def profit(initial_capital, multiplier):
    """
    Return profit
    :param initial_capital:
    :param multiplier:
    :return:
    """
    r = initial_capital * (multiplier + 1.0) - initial_capital
    return r


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
