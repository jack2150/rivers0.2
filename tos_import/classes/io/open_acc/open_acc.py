from datetime import datetime
from django.utils.timezone import utc
from tos_import.classes.io.open_csv import OpenCSV


class OpenAcc(OpenCSV):
    """
    Open an account statement file and
    format then return all data as dict
    note: remember to use 'type' for position
    """
    def __init__(self, data):
        OpenCSV.__init__(self, data)

        self.account_summary_keys = [
            'net_liquid_value',
            'stock_buying_power',
            'option_buying_power',
            'commissions_ytd',
            'futures_commissions_ytd'
        ]

        self.forex_summary_keys = [
            'cash', 'upl', 'floating', 'equity', 'margin',
            'available_equity', 'risk_level'
        ]

        self.profit_loss_keys = [
            'symbol', 'description', 'pl_open', 'pl_pct',
            'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
        ]

        self.holding_equity_keys = [
            'symbol', 'description', 'quantity', 'trade_price', 'mark', 'mark_value'
        ]

        self.holding_option_keys = [
            'symbol', 'option_code', 'expire_date', 'strike',
            'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
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

        self.future_statement_keys = [
            'trade_date', 'execute_date', 'execute_time', 'contract',
            'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
        ]

        self.holding_future_keys = [
            'lookup', 'symbol', 'description',  # not duplicate expire date
            'spc', 'expire_date', 'quantity', 'trade_price', 'mark', 'pl_day'

        ]

        self.forex_statement_keys = [
            '', 'date', 'time', 'contract', 'ref_no',
            'description', 'commissions', 'amount',
            'amount_usd', 'balance'
        ]

        self.holding_forex_keys = [
            'symbol', 'description', 'quantity', 'trade_price', 'mark', 'fpl'
        ]

        self.cash_balance_keys = [
            'date', 'time', 'contract', 'ref_no', 'description',
            'fees', 'commissions', 'amount', 'balance'
        ]

        self.account_summary = dict()
        self.forex_summary = dict()
        self.profit_loss = list()
        self.holding_option = list()
        self.holding_equity = list()
        self.trade_history = list()
        self.order_history = list()
        self.cash_balance = list()
        self.future_statement = list()
        self.holding_future = list()
        self.forex_statement = list()
        self.holding_forex = list()

    @classmethod
    def get_summary_data(cls, items):
        """
        Get summary data from a list
        :param items: list
        :return: str
        """
        try:
            result = str(items[1])
        except IndexError:
            raise IndexError('item have not index 1: %s' % items)

        return result

    def set_account_summary(self):
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

        self.account_summary = self.make_dict(self.account_summary_keys, summary)

    def set_forex_summary(self):
        """
        Set forex summary into class property
        Last a few lines before account summary
        """
        forex_summary = list()

        lines = self.get_lines(
            start_phrase='Forex Account Summary',
            end_phrase=None
        )
        for line in lines[1:-1]:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)
            item = self.get_summary_data(items)
            item = self.format_item(item)

            forex_summary.append(item)

        self.forex_summary = self.make_dict(self.forex_summary_keys, forex_summary)

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
        result = datetime.strptime(date, '%m/%d/%y %H:%M:%S').replace(tzinfo=utc)
        #result = datetime.strptime(date, '%m/%d/%y %H:%M:%S').utcnow().replace(tzinfo=utc)
        #result = timezone(result, timezone.get_current_timezone())

        return result

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

    def set_future_statement(self):
        """
        Set future statement into class property
        """
        self.set_values(
            start_phrase='Futures Statements',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.future_statement_keys,
            prop_name='future_statement'
        )

        self.future_statement = map(self.del_empty_keys, self.future_statement)

        self.convert_specific_type(self.future_statement, 'trade_date', self.convert_date, '')
        self.convert_specific_type(self.future_statement, 'execute_date', self.convert_date, '')
        self.convert_specific_type(self.future_statement, 'execute_time', self.convert_time, '')

        self.convert_specific_type(self.future_statement, 'fee', float, 0.0)
        self.convert_specific_type(self.future_statement, 'commission', float, 0.0)
        self.convert_specific_type(self.future_statement, 'amount', float, 0.0)
        self.convert_specific_type(self.future_statement, 'balance', float, 0.0)

    def get_lines_without_phrase(self, start_with, start_without, end_phrase):
        """
        Get lines with searching start ext and end text
        :param start_with: tuple
        :param start_without: tuple
        :param end_phrase: str
        :return: list of str
        """
        start = end = 0
        for key, line in enumerate(self.lines):
            start_with_cond = sum([x in line for x in start_with]) == len(start_with)
            start_without_cond = sum([x not in line for x in start_without]) == len(start_without)

            if start == 0 and start_with_cond and start_without_cond:
                start = key

            if end == 0 and start > 0 and end_phrase in line:
                end = key

        lines = []
        if start > 0 and end > 0:
            lines = self.lines[start:end + 1]

        return lines

    def set_holding_future(self):
        """
        Set futures into class property
        """
        lines = self.get_lines_without_phrase(
            start_with=('Futures', ),
            start_without=('Statements', '/'),
            end_phrase='OVERALL TOTALS',
        )

        for line in lines[2:-1]:
            # custom format for future
            future = self.get_future_detail(line)

            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            items = map(self.format_item, items)

            # add lookup field
            items.insert(0, items[0][1:3])

            holding_future = self.make_dict(self.holding_future_keys, items)
            holding_future['session'] = future['session'].upper()
            holding_future['description'] = future['description'].upper()

            self.holding_future.append(holding_future)

    def set_forex_statement(self):
        """
        Set forex into class property
        :return: None
        """
        self.set_values(
            start_phrase='Forex Statements',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.forex_statement_keys,
            prop_name='forex_statement'
        )

        self.replace_zero(self.forex_statement)
        self.forex_statement = map(self.del_empty_keys, self.forex_statement)
        self.forex_statement = self.fillna_dict(self.forex_statement)

        self.convert_specific_type(self.forex_statement, 'commissions', float, 0.0)
        self.convert_specific_type(self.forex_statement, 'amount', float, 0.0)
        self.convert_specific_type(self.forex_statement, 'amount_usd', float, 0.0)
        self.convert_specific_type(self.forex_statement, 'balance', float, 0.0)

        self.convert_specific_type(self.forex_statement, 'date', self.convert_date, '')
        self.convert_specific_type(self.forex_statement, 'time', self.convert_time, '')

    def set_holding_forex(self):
        """
        Set forex into class property
        """
        lines = self.get_lines_without_phrase(
            start_with=('Forex', ),
            start_without=('Statements', '/'),
            end_phrase='OVERALL TOTALS',
        )

        for line in lines[2:-1]:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            items = map(self.format_item, items)

            holding_forex = self.make_dict(self.holding_forex_keys, items)
            holding_forex['description'] = holding_forex['description'].upper()
            self.holding_forex.append(holding_forex)

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
        #self.trade_history = self.fillna_dict(self.trade_history)
        self.fillna_dict_with_exists(
            self.trade_history,
            'execute_time',
            ('execute_time', 'spread', 'order_type')
        )

        self.convert_specific_type(self.trade_history, 'execute_time', self.convert_datetime, '')
        self.convert_specific_type(self.trade_history, 'quantity', int, 0)
        self.convert_specific_type(self.trade_history, 'strike', float, 0.0)
        self.convert_specific_type(self.trade_history, 'price', float, 0.0)

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
        self.fillna_dict_with_exists(
            self.order_history,
            'time_placed',
            ('time_placed', 'spread', 'order', 'tif', 'status')
        )

        self.convert_specific_type(self.order_history, 'time_placed', self.convert_datetime, '')
        self.convert_specific_type(self.order_history, 'quantity', int, 0)
        self.convert_specific_type(self.order_history, 'strike', float, 0.0)

        try:
            self.convert_specific_type(self.order_history, 'price', float, 0.0)
        except ValueError:
            self.convert_specific_type(self.order_history, 'price', str, '0.0')

    def set_holding_equity(self):
        """
        Set equity into class property
        :return: None
        """
        self.set_values(
            start_phrase='Equities',
            end_phrase='OVERALL TOTALS',
            start_with=2,
            end_until=-1,
            prop_keys=self.holding_equity_keys,
            prop_name='holding_equity'
        )

        self.convert_specific_type(self.holding_equity, 'quantity', int, 0)

    def set_holding_option(self):
        """
        Set options into class property
        :return: None
        """
        self.set_values(
            start_phrase='Options',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.holding_option_keys,
            prop_name='holding_option'
        )

        self.convert_specific_type(self.holding_option, 'quantity', int, 0)

        # drop row if symbol not exists
        self.holding_option = [option for option in self.holding_option if option['symbol']]

    def get_future_detail(self, line):
        lookup = ''
        description = ''
        expire_date = ''
        session = ''

        if line[0] == '/':
            # is future
            line = self.replace_dash_inside_quote(line, replace_with=':')
            items = self.split_lines_with_dash(line)

            lookup = items[0][1:3]

            if ':' in items[1]:
                description, expire_date, session = map(lambda x: x.upper(), items[1].split(':'))
            elif ' - ' in items[1]:
                description, session, expire_date = map(lambda x: x.upper(), items[1].split(' - '))

        return dict(
            lookup=lookup,
            description=description,
            expire_date=expire_date,
            session=session
        )

    def set_profit_loss(self):
        """
        Set profits and losses into class property
        drop empty profit loss records
        :return: None

        self.set_values(
            start_phrase='Profits and Losses',
            end_phrase='OVERALL TOTALS',
            start_with=2,
            end_until=-1,
            prop_keys=self.profit_loss_keys,
            prop_name='profit_loss'
        )
        """
        lines = self.get_lines('Profits and Losses', 'OVERALL TOTALS')

        if 'Unallocated Subtotal' in lines[-2]:
            use_lines = lines[2:-2]
        else:
            use_lines = lines[2:-1]

        for line in use_lines:
            future = self.get_future_detail(line)
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)
            items = map(self.format_item, items)

            profit_loss = self.make_dict(self.profit_loss_keys, items)

            if profit_loss['symbol'][0] == '/':
                # is future
                profit_loss['description'] = future

            self.profit_loss.append(profit_loss)

    def read(self):
        """
        Most important method in class
        read files and output all data
        :return: dict
        """
        self.set_cash_balance()
        self.set_profit_loss()

        self.set_future_statement()
        self.set_forex_statement()

        self.set_order_history()
        self.set_trade_history()

        self.set_holding_equity()
        self.set_holding_option()
        self.set_holding_future()
        self.set_holding_forex()

        self.set_forex_summary()
        self.set_account_summary()

        return dict(
            cash_balance=self.cash_balance,
            profit_loss=self.profit_loss,

            future_statement=self.future_statement,
            forex_statement=self.forex_statement,

            order_history=self.order_history,
            trade_history=self.trade_history,

            holding_equity=self.holding_equity,
            holding_option=self.holding_option,
            holding_future=self.holding_future,
            holding_forex=self.holding_forex,

            forex_summary=self.forex_summary,
            account_summary=self.account_summary
        )