import copy

class opened_trade():
    
    def __init__(self, type, date):
        self.type = type
        self.date = date

    def __str__(self):
        return "{0}\n{1}".format(self.type, self.date)

class closed_trade(opened_trade):
    
    def __init__(self, type, date, shares, entry, exit):
        super().__init__(type, date)
        self.shares = float(shares)
        self.entry  = float(entry)
        self.exit   = float(exit)
    
    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}".format(self.type, 
                                                self.date, 
                                                self.shares, 
                                                self.entry, 
                                                self.exit)

class position:
    
    def __init__(self, no, entry_price, shares, exit_price=0, stop_loss=0):
        self.no          = no
        self.type        = "None"
        self.entry_price = float(entry_price)
        self.shares      = float(shares)
        self.exit_price  = float(exit_price)
        self.stop_loss   = float(stop_loss)   
    
    def show(self):
        print("No.     {0}".format(self.no))
        print("Type:   {0}".format(self.type))
        print("Entry:  {0}".format(self.entry_price))
        print("Shares: {0}".format(self.shares))
        print("Exit:   {0}".format(self.exit_price))
        print("Stop:   {0}\n".format(self.stop_loss))

class long_position(position):
    
    def __init__(self, no, entry_price, shares, exit_price=0, stop_loss=0):
        super().__init__(no, entry_price, shares, exit_price, stop_loss)
        self.type = 'long'

    def close(self, percent, current_price):
        shares = self.shares
        self.shares *= 1.0 - percent
        return shares * percent * current_price

class short_position(position):
    
    def __init__(self, no, entry_price, shares, exit_price=0, stop_loss=0):
        super().__init__(no, entry_price, shares, exit_price, stop_loss)
        self.type = 'short' 

    def close(self, percent, current_price):
        entry = self.shares * percent * self.entry_price
        exit = self.shares * percent * current_price
        self.shares *= 1.0 - percent
        if entry - exit + entry <= 0: 
            return 0
        else: 
            return entry - exit + entry

class account():
    
    def __init__(self, initial_capital):
        self.initial_capital = float(initial_capital)
        self.buying_power    = float(initial_capital)
        self.no              = 0
        self.date            = None
        self.equity          = []
        self.positions       = []
        self.opened_trades   = []
        self.closed_trades   = []

    def enter_position(self, type, entry_capital, entry_price, exit_price=0, stop_loss=0):
        entry_capital = float(entry_capital)
        if entry_capital < 0: 
            raise ValueError("Error: Entry capital must be positive")          
        elif entry_price < 0: 
            raise ValueError("Error: Entry price cannot be negative.")
        elif self.buying_power < entry_capital: 
            raise ValueError("Error: Not enough buying power to enter position")          
        else: 
            self.buying_power -= entry_capital
            shares = entry_capital / entry_price 
            if type == 'long': 
                self.positions.append(long_position(self.no, 
                                                    entry_price, 
                                                    shares, 
                                                    exit_price, 
                                                    stop_loss))
            elif type == 'short': 
                self.positions.append(short_position(self.no, 
                                                     entry_price, 
                                                     shares, 
                                                     exit_price, 
                                                     stop_loss))    
            else: 
                raise TypeError("Error: Invalid position type.")

            self.opened_trades.append(opened_trade(type, self.date))
            self.no += 1    

    def close_position(self, position, percent, current_price):
        if percent > 1 or percent < 0: 
            raise ValueError("Error: Percent must range between 0-1.")
        elif current_price < 0:
            raise ValueError("Error: Current price cannot be negative.")                
        else: 
            self.closed_trades.append(closed_trade(position.type, 
                                                   self.date, 
                                                   position.shares * percent, 
                                                   position.entry_price, 
                                                   current_price))
            
            self.buying_power += position.close(percent, current_price)

    def purge_positions(self):
        self.positions = [p for p in self.positions if p.shares > 0]        
            
    def show_positions(self):
        for p in self.positions: p.show()

    def total_value(self, current_price):
        temporary = copy.deepcopy(self)
        for position in temporary.positions:
            temporary.close_position(position, 1.0, current_price)
        return temporary.buying_power
