import logging
import types
import datetime
import time
import pandas as pd
from gemini.gemini_core import exchange
from gemini.gemini_core import helpers
from gemini.gemini_core import settings
from gemini.empyrical import *
from gemini.helpers.timeframe_resampler import resample

FEES = getattr(settings, "FEES", dict())

logger = logging.getLogger(__name__)


class Gemini:
    """
    Main class of Backtester
    """
    data = None  # storage for history data
    account = None  # exchange account simulator
    indicator_data = {'date': [], 'CMO': []}
    sim_params = {
        'capital_base': 10e5,
        'data_frequency': 'D',
        'fee': FEES,  # Fees in percent of trade amount
    }
    records = []

    def __init__(self, initialize=None, logic=None, analyze=None,
                 sim_params=None):
        """
        Create backtester with own methods.

        sim_params :: Backtester's settings:
            * start_session :: not use
            * end_session :: not use
            * capital_base :: default 10k
            * data_frequency :: not use
            *

        :param initialize:
        :param logic:
        :param analyze:
        :param sim_params:
        """

        if initialize is not None:
            self.initialize = types.MethodType(initialize, self)

        if logic is not None:
            self.logic = types.MethodType(logic, self)

        if analyze is not None:
            self.analyze = types.MethodType(analyze, self)

        if sim_params is not None:
            # replace only received items
            for k, item in self.sim_params.items():
                if k in sim_params:
                    self.sim_params[k] = sim_params[k]


    def initialize(self):
        """
        First method which will be called after start algorithm
        :return:
        """
        pass

    def logic(self, data):
        """
        Central method which will be called for every tick
        in trading interval.

        :param data:
        :return:
        """
        pass

    def create_indicator_dataframe(self):
        df = pd.DataFrame(self.indicator_data)
        df = df.set_index(['date'])
        return df

    def run(self, data, **kwargs):
        """
        Main method to start backtest
        :param data :: history data with ticks or bars
        :param logic:
        :param trading_interval:
        :param lookback_period:
        :return:
        """

        self.account = exchange.Account(
            self.sim_params.get('capital_base', 10e5),
            fee=self.sim_params.get('fee', None)
        )
        self.records = []

        self.initialize()

        # TODO Add filter between start & end session from sim_params

        # resample data frame to 'D' by default
        self.data = resample(data, self.sim_params.get('data_frequency', 'D'))

        # start cycle
        for index, tick in self.data.iterrows():
            # Update account variables
            self.account.date = index
            # update total value in account
            # TODO Replace by pandas DataFrame
            self.account.equity.append(
                (index, self.account.total_value(tick['close'])))

            # Execute trading logic
            lookback_data = self.data.loc[:index]
            try:
                self.logic(lookback_data)
            except Exception as ex:
                logger.exception(ex)

            # Cleanup empty positions
            self.account.purge_positions()
        data_CMO = self.create_indicator_dataframe()
        self.results()
        self.analyze(data_CMO=data_CMO, **kwargs)

    def results(self):
        """
        Print results of backtest to console
        :return:
        """

        ts = time.time()
        results_history = open("results_history.txt", 'a')
        results_history.write(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + '\n')

        title = "{:=^50}".format(
            " Results (freq {}) ".format(self.sim_params['data_frequency']))
        print(title + "\n")
        begin_price = self.data.iloc[0]['open']
        final_price = self.data.iloc[-1]['close']

        shares = self.account.initial_capital / self.data.iloc[0]['close']
        self.data['base_equity'] = [price * shares for price in
                                    self.data['close']]
        self.data['equity'] = [e for _, e in self.account.equity]

        # STRING FORMATS
        title_fmt = "{:-^40}"
        str_fmt = "{0:<13}: {1:.2f}{2}"

        # BENCHMARK
        percent_change = helpers.percent_change(self.data['base_equity'][0],
                                                self.data['base_equity'][-1])

        benchmark = self.data['base_equity'].pct_change()
        bench = [
            ("Capital", self.account.initial_capital, ""),
            ("Final Equity", self.data['base_equity'][-1], ""),
            ("Net profit",
             helpers.profit(self.account.initial_capital, percent_change), " ({:+.2f}%)".format(percent_change * 100)),
            ("Max Drawdown",
             max_drawdown(benchmark) * 100, "%"),
        ]

        print(title_fmt.format(" Benchmark "))
        results_history.write(title_fmt.format(" Benchmark ") + '\n')
        for r in bench:
            print(str_fmt.format(*r))
            results_history.write(str_fmt.format(*r) + '\n')

        # STRATEGY
        percent_change = helpers.percent_change(self.data['equity'][0],
                                                self.data['equity'][-1])
        open_fee = sum([t.fee for t in self.account.opened_trades])
        close_fee = sum([t.fee for t in self.account.closed_trades])

        # print trades
        # for t in self.account.opened_trades: print(t)

        returns = self.data['equity'].pct_change()
        strategy = [
            ("Capital", self.account.initial_capital, ""),
            ("Final Equity", self.data['equity'][-1], ""),
            ("Net profit",
             helpers.profit(self.account.initial_capital, percent_change),
             " ({:+.2f}%)".format(percent_change * 100)),
            ("Max Drawdown",
             max_drawdown(returns)*100, "%"),
            ("Sharpe Ratio",
             sharpe_ratio(returns), ""),
            ("Sortino Ratio",
             sortino_ratio(returns), ""),
            ("Alpha",
             alpha(returns, benchmark), ""),
            ("Beta",
             beta(returns, benchmark), ""),
            ("Fees paid", open_fee + close_fee, ""),
        ]

        print(title_fmt.format(" Strategy "))
        results_history.write(title_fmt.format(" Strategy ") + '\n')
        for r in strategy:
            print(str_fmt.format(*r))
            results_history.write(str_fmt.format(*r) + '\n')

        # STATISTICS
        longs = len(
            [t for t in self.account.opened_trades if t.type_ == 'Long'])
        sells = len(
            [t for t in self.account.closed_trades if t.type_ == 'Long'])
        shorts = len(
            [t for t in self.account.opened_trades if t.type_ == 'Short'])
        covers = len(
            [t for t in self.account.closed_trades if t.type_ == 'Short'])

        stat = [
            ("Longs", longs, ""),
            ("Sells", sells, ""),
            ("Shorts", shorts, ""),
            ("Covers", covers, ""),
            ("Total Trades", longs + sells + shorts + covers, ""),
        ]
        str_fmt = "{0:<13}: {1:.0f}{2}"

        results_history.write(title_fmt.format(" Statistics ") + '\n')
        print(title_fmt.format(" Statistics "))
        for r in stat:
            print(str_fmt.format(*r))
            results_history.write(str_fmt.format(*r) + '\n')

        print("-" * len(title))
        results_history.write("-" * len(title) + '\n' * 3)
        return percent_change

    def analyze(self):
        pass
