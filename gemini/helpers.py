def PercentChange(d1, d2):
    return (d2-d1)/d1

def Profit(InitialCapital, Multiplier):
    return InitialCapital*(Multiplier+1.0)-InitialCapital

class Period():
    def __init__(self, Data):
        self.Data = Data

    def loc(self, i):
        if i > 0: raise ValueError("Error: Cannot look forward!")
        if i <= -(len(self.Data)): raise ValueError("Error: Cannot look too far back!")     
        return self.Data.iloc[i-1]