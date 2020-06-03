import gemini.gemini_core.settings as settings
from gemini.gemini_core.helpers import rnd

PRECISION = getattr(settings, "PRECISION", 8)
FEES = getattr(settings, "FEES", dict())


class OpenedTrade:
    """
    Open trades main class
    """

    def __init__(self, type_, date, price=None, size=None, fee=None):
        self.type_ = type_
        self.date = date
        self.price = price
        self.size = size
        self.fee = fee

    def __str__(self):
        return "OpenedTrade: {0} {1} {2:.8f} x {3:.8f} Fee: {4:.8f}".format(
            self.date, self.type_, self.price, self.size, self.fee)


class ClosedTrade(OpenedTrade):
    """
    Closed trade class
    """

    def __init__(self, type_, date, shares, entry, exit, fee):
        super().__init__(type_, date)
        self.shares = float(shares)
        self.entry = float(entry)  # enter price
        self.exit = float(exit)  # exit price
        self.fee = fee  # deal fee

    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}".format(self.type_, self.date,
                                                self.shares, self.entry,
                                                self.exit)


class Position:
    """
    Position main class
    """

    def __init__(self, number, entry_price, shares, exit_price=0, stop_loss=0):
        self.number = number
        self.type_ = "None"
        self.entry_price = float(entry_price)
        self.shares = float(shares)
        self.exit_price = float(exit_price)
        self.stop_loss = float(stop_loss)

    def show(self):
        """
        Print position info
        :return:
        """
        print("No. {0}".format(self.number))
        print("Type:   {0}".format(self.type_))
        print("Entry:  {0}".format(self.entry_price))
        print("Shares: {0}".format(self.shares))
        print("Exit:   {0}".format(self.exit_price))
        print("Stop:   {0}\n".format(self.stop_loss))

    def __str__(self):
        return "{} {}x{}".format(self.type_, self.shares, self.entry_price)


class LongPosition(Position):
    """
    Long position class
    """

    def __init__(self, number, entry_price, shares, fee, exit_price=0,
                 stop_loss=0):
        super().__init__(number, entry_price, shares, exit_price, stop_loss)
        self.type_ = 'Long'
        self.fee = fee

    def close(self, percent, current_price):
        """
        Decrease shares count by percent and return value of closed shares.

        :param percent:
        :param current_price:
        :return:
        """
        shares = self.shares
        self.shares *= 1.0 - percent
        return shares * percent * current_price


class ShortPosition(Position):
    """
    Short position class
    """

    def __init__(self, number, entry_price, shares, fee, exit_price=0,
                 stop_loss=0):
        super().__init__(number, entry_price, shares, exit_price, stop_loss)
        self.type_ = 'Short'
        self.fee = fee

    def close(self, percent, current_price):
        """
        Decrease shares count by percent and return value of closed shares.

        :param percent:
        :param current_price:
        :return:
        """

        entry = self.shares * percent * self.entry_price
        exit_ = self.shares * percent * current_price
        self.shares *= 1.0 - percent
        if entry - exit_ + entry <= 0:
            return 0
        else:
            return entry - exit_ + entry


class Account:
    """
    Main account class
    Store settings and trades data
    """
    fee = FEES

    def __init__(self, initial_capital, fee=None):
        self.initial_capital = initial_capital
        self.buying_power = initial_capital
        self.number = 0
        self.date = None
        self.equity = []
        self.positions = []
        self.opened_trades = []
        self.closed_trades = []
        if isinstance(fee, dict):
            self.fee = fee

    def enter_position(self, type_, entry_capital, entry_price, exit_price=0,
                       stop_loss=0):
        """
        Open position
        :param type_:
        :param entry_capital:
        :param entry_price:
        :param exit_price:
        :param stop_loss:
        :return:
        """

        if entry_capital < 0:
            raise ValueError("Error: Entry capital must be positive")
        elif entry_price < 0:
            raise ValueError("Error: Entry price cannot be negative.")
        elif self.buying_power < entry_capital:
            raise ValueError("Error: Not enough buying power to enter position")
        else:
            # apply fee to price
            price_with_fee = self.apply_fee(entry_price, type_, 'Open')

            # round shares and calculate position capital
            size = rnd(entry_capital / price_with_fee)
            pos_amount = rnd(entry_price * size)

            # calculate trading fee for position
            trade_fee = rnd(pos_amount * self.fee.get(type_, 0))
            # calc buying power
            self.buying_power -= pos_amount + trade_fee

            if type_ == 'Long':
                position = LongPosition(
                    self.number, entry_price, size, trade_fee, exit_price,
                    stop_loss)

            elif type_ == 'Short':
                position = ShortPosition(
                    self.number, entry_price, size, trade_fee, exit_price,
                    stop_loss)

            else:
                raise TypeError("Invalid position type.")

            self.positions.append(position)
            self.opened_trades.append(
                OpenedTrade(type_, self.date, entry_price, size, trade_fee))
            self.number += 1

    def close_position(self, position, percent, price):
        """
        close position
        :param position:
        :param percent:
        :param price:
        :return:
        """

        # TODO Change order logic to:
        # order_percent(asset, percent > 0)
        # if >0: check and buy/close if necessary
        # if 0: check and close if position exists

        if percent > 1 or percent < 0:
            raise ValueError(
                "Error: Percent must range between 0-1.")
        elif price < 0:
            raise ValueError("Error: Current price cannot be negative.")
        else:
            # get trade fee
            # FIXME Use type by direction: buy-Long, sell-Short
            trade_fee = rnd(
                price * position.shares * self.fee.get(position.type_, 0))

            self.closed_trades.append(
                ClosedTrade(position.type_, self.date,
                            position.shares * percent,
                            position.entry_price, price, trade_fee))
            self.buying_power += position.close(percent, price) - trade_fee

    def apply_fee(self, price, type_, direction):
        """
        Apply fee to price by position type & transaction direction

        Position types:
        * Long
        * Short

        Directions:
        * Open : Add fee to Long price, subtract fee from Short price
        * Close : Subtract fee from Long price, add fee to Short price

        :param price:
        :param type_:
        :param direction:
        :return:
        """
        sign = 1 if direction == 'Open' else -1

        # change price with fee
        fee = self.fee.get(type_, 0)
        if type_ == 'Long':
            price *= 1 + sign * fee
        elif type_ == 'Short':
            price *= 1 - sign * fee

        # round price
        return rnd(price)

    def purge_positions(self):
        """
        Delete positions without shares?
        :return:
        """

        # FIXME Fix to remove positions on close

        self.positions = [p for p in self.positions if p.shares > 0]

    def show_positions(self):
        """
        Show open position info
        :return:
        """
        for p in self.positions:
            p.show()

    def total_value(self, current_price):
        """
        Return total balance with open positions

        :param current_price:
        :return:
        """
        # print(self.buying_power)
        # for p in self.positions: print(p)  # positions
        # for ot in self.opened_trades: print(ot)  # open trades
        in_pos = sum(
            [p.shares * current_price for p in self.positions
             if p.type_ == 'Long']) + sum(
            [p.shares * (p.entry_price - current_price + p.entry_price)
             for p in self.positions
             if p.type_ == 'Short'])
        return self.buying_power + in_pos
