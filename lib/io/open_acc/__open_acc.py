import numpy
from lib.io.open_csv import OpenCSV
from pandas import DataFrame


class OpenAcc(OpenCSV):
    """
    Open an account statement file and
    format then return all data as dict
    """
    def __init__(self, fname):
        OpenCSV.__init__(self, fname)

        self.summary_keys = [
            'net_liquid_value',
            'stock_buying_power',
            'option_buying_power',
            'commissions_ytd',
            'futures_commissions_ytd'
        ]

        self.profits_losses_keys = [
            'symbol', 'description', 'pl_open', 'pl_pct',
            'pl_day', 'pl_ytd', 'margin_req'
        ]

        self.equity_keys = [
            'symbol', 'description', 'quantity', 'trade_price'
        ]

        self.options_keys = [
            'symbol', 'option_code', 'expire_date', 'strike',
            'contract', 'quantity', 'trade_price'
        ]

        self.trade_history_keys = [
            '', 'execute_time', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike',
            'contract', 'price', 'net_price', 'order_type'
        ]

        self.order_history_keys = [
            '', '', 'time_placed', 'spread', 'side',
            'quantity', 'pos_effect', 'symbol', 'expire_date',
            'strike', 'contract', 'price', 'order', 'tif',
            'status'
        ]

        self.forex_keys = [
            'date', 'time', 'contract', 'ref_no',
            'description', 'commissions', 'amount',
            'amount_usd', 'balance'
        ]

        self.futures_keys = [
            'trade_date', 'execute_date',
            'execute_time', 'contract',
            'ref_no', 'description',
            'fees', 'commissions',
            'amount', 'balance'
        ]

        self.cash_balance_keys = [
            'date', 'time', 'contract', 'ref_no', 'description',
            'fees', 'commissions', 'amount', 'balance'
        ]

        self.summary = dict()
        self.profits_losses = list()
        self.options = list()
        self.equities = list()
        self.trade_history = list()
        self.order_history = list()
        self.cash_balance = list()
        self.futures = list()
        self.forex = list()

    @classmethod
    def get_summary_data(cls, items):
        """
        Get summary data from a list
        :param items: list
        :return: str
        """
        return str(items[1])

    def set_summary(self):
        """
        Get summary data from lines
        then make dict using column names
        and save it into class property
        :return: dict
        """
        summary = list()
        lines = self.last_five_lines(self.lines)

        for line in lines:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)
            item = self.get_summary_data(items)

            item = self.format_item(item)

            summary.append(item)

        self.summary = self.make_dict(self.summary_keys, summary)

    def set_values(self, start_phrase, end_phrase, start_add, end_reduce, prop_keys, prop_name):
        """
        Make a dict from file lines for single section
        then save it into class property
        :param start_phrase: str
        :param end_phrase: str
        :param start_add: int
        :param end_reduce: int
        :param prop_keys: list
        :param prop_name: str
        :return: None
        """
        prop_list = list()

        lines = self.get_lines(start_phrase, end_phrase)

        for line in lines[start_add:end_reduce]:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            items = map(self.format_item, items)

            prop_list.append(self.make_dict(prop_keys, items))

        setattr(self, prop_name, prop_list)

    def set_cash_balance(self):
        """
        Set Cash Balance into class property
        :return: None
        """
        self.set_values(
            start_phrase='Cash Balance',
            end_phrase='TOTAL',
            start_add=2,
            end_reduce=-1,
            prop_keys=self.cash_balance_keys,
            prop_name='cash_balance'
        )

    def set_futures(self):
        """
        Set futures into class property
        :return: None
        """
        self.set_values(
            start_phrase='Futures Statements',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.futures_keys,
            prop_name='futures'
        )

    def set_forex(self):
        """
        Set forex into class property
        :return: None
        """
        self.set_values(
            start_phrase='Forex Statements',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.forex_keys,
            prop_name='forex'
        )

    @classmethod
    def fillna_history_sections(cls, prop):
        """
        Use trade history then fill empty with value row above
        """
        df = DataFrame(prop)
        df = df.replace(['', 'DEBIT', 'CREDIT'], numpy.nan)
        df = df.fillna(method='ffill')

        return [r.to_dict() for k, r in df.iterrows()]

    def set_trade_history(self):
        """
        Set trade history into class property
        :return: None
        """
        self.set_values(
            start_phrase='Account Trade History',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.trade_history_keys,
            prop_name='trade_history'
        )

        self.trade_history = map(self.del_empty_keys, self.trade_history)
        self.trade_history = self.fillna_history_sections(self.trade_history)

    def set_order_history(self):
        """
        Set order history into class property
        :return: None
        """
        self.set_values(
            start_phrase='Account Order History',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.order_history_keys,
            prop_name='order_history'
        )

        self.order_history = map(self.del_empty_keys, self.order_history)
        self.order_history = self.fillna_history_sections(self.order_history)

    def set_equities(self):
        """
        Set equity into class property
        :return: None
        """
        self.set_values(
            start_phrase='Equities',
            end_phrase='OVERALL TOTALS',
            start_add=2,
            end_reduce=-1,
            prop_keys=self.equity_keys,
            prop_name='equities'
        )

    def set_options(self):
        """
        Set options into class property
        :return: None
        """
        self.set_values(
            start_phrase='Options',
            end_phrase=',,,,,,',
            start_add=2,
            end_reduce=-1,
            prop_keys=self.options_keys,
            prop_name='options'
        )

    def set_profits_losses(self):
        """
        Set profits and losses into class property
        :return: None
        """
        self.set_values(
            start_phrase='Profits and Losses',
            end_phrase='OVERALL TOTALS',
            start_add=2,
            end_reduce=-1,
            prop_keys=self.profits_losses_keys,
            prop_name='profits_losses'
        )

    def read(self):
        """
        Most important method in class
        read files and output all data
        :return: dict
        """
        self.set_cash_balance()
        self.set_futures()
        self.set_forex()
        self.set_order_history()
        self.set_trade_history()
        self.set_equities()
        self.set_options()
        self.set_summary()

        return dict(
            cash_balance=self.cash_balance,
            futures=self.futures,
            forex=self.forex,
            order_history=self.order_history,
            trade_history=self.trade_history,
            equities=self.equities,
            options=self.options,
            summary=self.summary
        )



















































