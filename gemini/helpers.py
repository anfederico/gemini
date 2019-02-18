def percent_change(d1, d2):
    return (d2 - d1) / d1

def profit(initial_capital, multiplier):
    return initial_capital * (multiplier + 1.0) - initial_capital

class period():
    def __init__(self, data):
        self.data = data

    def loc(self, i):
        if i > 0:
            raise ValueError("Error: Cannot look forward!")
        if i <= -(len(self.data)):
            raise ValueError("Error: Cannot look too far back!")
        return self.data.iloc[i-1]