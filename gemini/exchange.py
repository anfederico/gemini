import copy
import math

class opened_trade():
    """An object representing an open trade."""

    def __init__(self, type, date):
        """Initate the trade.

        :param type: Type of trade
        :type type: float
        :param date: When the trade was opened
        :type date: datetime

        :return: A trade
        :rtype: trade
        """  
        self.type = type
        self.date = date

    def __str__(self):
        return "{0}\n{1}".format(self.type, self.date)

class closed_trade(opened_trade):
    """An object representing a closed trade."""

    def __init__(self, type, date, shares, entry, exit):
        """Initate the trade.

        :param type: Type of trade
        :type type: float
        :param date: When the trade was closed
        :type date: datetime
        :param shares: Number of shares
        :type shares: float
        :param entry: Entry price
        :type entry: float
        :param exit: Exit price
        :type exit: float

        :return: A trade
        :rtype: trade
        """  
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
    """A parent object representing a position."""

    def __init__(self, no, entry_price, shares, exit_price, stop_loss):
        """Open the position.

        :param no: A unique position id number
        :type no: float
        :param entry_price: Entry price at which shares are longed/shorted
        :type entry_price: float
        :param shares: Number of shares to long/short
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float

        :return: A position
        :rtype: position
        """    
        self.no            = no
        self.type          = "None"
        self.entry_price   = float(entry_price)
        self.shares        = float(shares)
        self.exit_price    = float(exit_price)
        self.stop_loss     = float(stop_loss)
    
    def show(self):
        print("No.     {0}".format(self.no))
        print("Type:   {0}".format(self.type))
        print("Entry:  {0}".format(self.entry_price))
        print("Shares: {0}".format(self.shares))
        print("Exit:   {0}".format(self.exit_price))
        print("Stop:   {0}\n".format(self.stop_loss))

class long_position(position):
    """A child object representing a long position."""

    def __init__(self, no, entry_price, shares, exit_price=math.inf, stop_loss=0):
        """Open the position.

        :param no: A unique position id number
        :type no: float
        :param entry_price: Entry price at which shares are longed
        :type entry_price: float
        :param shares: Number of shares to long
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float

        :return: A long position
        :rtype: long_position
        """

        if exit_price is False: exit_price = math.inf
        if stop_loss is False: stop_loss = 0
        super().__init__(no, entry_price, shares, exit_price, stop_loss)
        self.type = 'long'

    def close(self, percent, current_price):
        """Close the position.

        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Closing price
        :type current_price: float

        :return: Amount of capital gained from closing position
        :rtype: float
        """
        shares = self.shares
        self.shares *= 1.0 - percent
        return shares * percent * current_price

    def stop_hit(self, current_price):
        if current_price <= self.stop_loss:
            return(True)

class short_position(position):
    """A child object representing a short position."""

    def __init__(self, no, entry_price, shares, exit_price=0, stop_loss=math.inf):
        """Open the position.

        :param no: A unique position id number
        :type no: int
        :param entry_price: Entry price at which shares are shorted
        :type entry_price: float
        :param shares: Number of shares to short
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float

        :return: A short position
        :rtype: short_position
        """       
        if exit_price is False: exit_price = 0
        if stop_loss is False: stop_loss = math.inf
        super().__init__(no, entry_price, shares, exit_price, stop_loss)
        self.type = 'short'

    def close(self, percent, current_price):
        """Close the position.

        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Closing price
        :type current_price: float

        :return: Amount of capital gained from closing position
        :rtype: float
        """
        entry = self.shares * percent * self.entry_price
        exit = self.shares * percent * current_price
        self.shares *= 1.0 - percent
        if entry - exit + entry <= 0: 
            return 0
        else: 
            return entry - exit + entry

    def stop_hit(self, current_price):
        if current_price >= self.stop_loss:
            return(True)

class account():
    """An object representing an exchange account."""

    def __init__(self, initial_capital):
        """Initiate an account.

        :param initial_capital: Starting capital to fund account
        :type initial_capital: float

        :return: An account object
        :rtype: account
        """ 
        self.initial_capital = float(initial_capital)
        self.buying_power    = float(initial_capital)
        self.no              = 0
        self.date            = None
        self.equity          = []
        self.positions       = []
        self.opened_trades   = []
        self.closed_trades   = []

    def enter_position(self, type, entry_capital, entry_price, exit_price=False, stop_loss=False, commission=0):
        """Open a position.

        :param type: Type of position e.g. ("long, short")
        :type type: float
        :param entry_price: Amount of capital invested into position
        :type entry_price: float
        :param entry_price: Entry price at which shares are longed/shorted
        :type entry_price: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float
        :param commision: Percent commission subtracted from position size
        :type commision: float
        """ 
        entry_capital = float(entry_capital)
        
        if entry_capital < 0: 
            raise ValueError("Error: Entry capital must be positive")          
        elif entry_price < 0: 
            raise ValueError("Error: Entry price cannot be negative.")
        elif self.buying_power < entry_capital: 
            raise ValueError("Error: Not enough buying power to enter position")          
        else: 
            self.buying_power -= entry_capital
            if commission > 0:
                shares = entry_capital / (entry_price + commission * entry_price)
            else:
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

    def close_position(self, position, percent, current_price, commission=0):
        """Close a position.

        :param position: Position id number
        :type position: int
        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Price at which position is closed
        :type current_price: float
        :param commision: Percent commission subtracted from capital returned
        :type commision: float
        """ 
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
            
            if commission > 0:
                closing_position_price = position.close(percent, current_price)
                self.buying_power += (closing_position_price - closing_position_price * commission)
            else:
                self.buying_power += position.close(percent, current_price)

    def purge_positions(self):
        """Delete all empty positions.""" 
        self.positions = [p for p in self.positions if p.shares > 0]        

    def show_positions(self):
        """Show all account positions.""" 
        for p in self.positions: p.show()

    def total_value(self, current_price):
        """Calculate total value of account

        :param current_price: Price used to value open position sizes
        :type current_price: float

        :return: Total value of acocunt
        :rtype: float
        """ 
        temporary = copy.deepcopy(self)
        for position in temporary.positions:
            temporary.close_position(position, 1.0, current_price)
        return temporary.buying_power
