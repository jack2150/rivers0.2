from datetime import datetime
from django.utils.timezone import utc
from lib.io.open_csv import OpenCSV


class OpenAcc(OpenCSV):
    """
    Open an account statement file and
    format then return all data as dict
    """
    def __init__(self, data):
        OpenCSV.__init__(self, data)

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
            '', 'date', 'time', 'contract', 'ref_no',
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

    @classmethod
    def convert_date(cls, date):
        """
        Convert date format into YYYY-MM-DD
        :param date: str
        :return: str
        """
        result = datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d')

        return result

    @classmethod
    def convert_time(cls, time):
        """
        Convert date format into %H:%M:%S
        :param time: str
        :return: str
        """
        result = datetime.strptime(time, '%H:%M:%S').strftime('%H:%M:%S')

        return result

    @classmethod
    def convert_datetime(cls, date):
        """
        Convert date format into YYYY-MM-DD 7/23/14 22:21:27
        :param date: str
        :return: str
        """
        result = datetime.strptime(date, '%m/%d/%y %H:%M:%S').utcnow().replace(tzinfo=utc)
        #result = timezone(result, timezone.get_current_timezone())

        return result

    @classmethod
    def convert_specific_type(cls, prop_obj, column_name, specific_type, empty_value):
        """
        Convert item for dict in list into specific type
        :param prop_obj: list
        :param column_name: str
        :param specific_type: type
        :return: None
        """
        for key, item in enumerate(prop_obj):
            if item[column_name]:
                prop_obj[key][column_name] = specific_type(item[column_name])
            else:
                prop_obj[key][column_name] = empty_value

    @classmethod
    def replace_zero(cls, prop_obj):
        """
        Convert item for dict in list into specific type
        :param prop_obj: list
        :return: None
        """
        for key, item in enumerate(prop_obj):
            for column, value in item.items():
                if value == '--':
                    prop_obj[key][column] = int(0)

    def set_cash_balance(self):
        """
        Set Cash Balance into class property
        :return: None
        """
        self.set_values(
            start_phrase='Cash Balance',
            end_phrase='TOTAL',
            start_with=2,
            end_until=-1,
            prop_keys=self.cash_balance_keys,
            prop_name='cash_balance'
        )

        self.convert_specific_type(self.cash_balance, 'date', self.convert_date, '')
        self.convert_specific_type(self.cash_balance, 'ref_no', float, 0)
        self.convert_specific_type(self.cash_balance, 'fees', float, 0.0)
        self.convert_specific_type(self.cash_balance, 'commissions', float, 0.0)
        self.convert_specific_type(self.cash_balance, 'amount', float, 0.0)
        self.convert_specific_type(self.cash_balance, 'balance', float, 0.0)

    def set_futures(self):
        """
        Set futures into class property
        :return: None
        """
        self.set_values(
            start_phrase='Futures Statements',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.futures_keys,
            prop_name='futures'
        )

        self.convert_specific_type(self.futures, 'trade_date', self.convert_date, '')
        self.convert_specific_type(self.futures, 'execute_date', self.convert_date, '')
        self.convert_specific_type(self.futures, 'execute_time', self.convert_time, '')

    def set_forex(self):
        """
        Set forex into class property
        :return: None
        """
        self.set_values(
            start_phrase='Forex Statements',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.forex_keys,
            prop_name='forex'
        )

        self.replace_zero(self.forex)
        self.forex = map(self.del_empty_keys, self.forex)
        self.forex = self.fillna_dict(self.forex)

        self.convert_specific_type(self.forex, 'commissions', float, 0.0)
        self.convert_specific_type(self.forex, 'amount', float, 0.0)
        self.convert_specific_type(self.forex, 'amount_usd', float, 0.0)
        self.convert_specific_type(self.forex, 'balance', float, 0.0)

        self.convert_specific_type(self.forex, 'date', self.convert_date, '')
        self.convert_specific_type(self.forex, 'time', self.convert_time, '')

    def set_trade_history(self):
        """
        Set trade history into class property
        :return: None
        """
        self.set_values(
            start_phrase='Account Trade History',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.trade_history_keys,
            prop_name='trade_history'
        )

        self.trade_history = map(self.del_empty_keys, self.trade_history)
        self.trade_history = self.fillna_dict(self.trade_history)

        self.convert_specific_type(self.trade_history, 'execute_time', self.convert_datetime, '')
        self.convert_specific_type(self.trade_history, 'quantity', int, 0)

    def set_order_history(self):
        """
        Set order history into class property
        :return: None
        """
        self.set_values(
            start_phrase='Account Order History',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.order_history_keys,
            prop_name='order_history'
        )

        self.order_history = map(self.del_empty_keys, self.order_history)
        self.order_history = self.fillna_dict(self.order_history)

        self.convert_specific_type(self.order_history, 'time_placed', self.convert_datetime, '')
        self.convert_specific_type(self.order_history, 'quantity', int, 0)

    def set_equities(self):
        """
        Set equity into class property
        :return: None
        """
        self.set_values(
            start_phrase='Equities',
            end_phrase='OVERALL TOTALS',
            start_with=2,
            end_until=-1,
            prop_keys=self.equity_keys,
            prop_name='equities'
        )

        self.convert_specific_type(self.equities, 'quantity', int, 0)

    def set_options(self):
        """
        Set options into class property
        :return: None
        """
        self.set_values(
            start_phrase='Options',
            end_phrase=',,,,,,',
            start_with=2,
            end_until=-1,
            prop_keys=self.options_keys,
            prop_name='options'
        )

        self.convert_specific_type(self.options, 'quantity', int, 0)

    def set_profits_losses(self):
        """
        Set profits and losses into class property
        :return: None
        """
        self.set_values(
            start_phrase='Profits and Losses',
            end_phrase='OVERALL TOTALS',
            start_with=2,
            end_until=-1,
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
        self.set_profits_losses()
        self.set_summary()

        return dict(
            cash_balance=self.cash_balance,
            futures=self.futures,
            forex=self.forex,
            order_history=self.order_history,
            trade_history=self.trade_history,
            equities=self.equities,
            options=self.options,
            profits_losses=self.profits_losses,
            summary=self.summary
        )
