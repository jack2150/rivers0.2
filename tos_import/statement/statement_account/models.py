import locale
from django.db import models
from tos_import.classes.io.open_acc import OpenAcc
from tos_import.models import Underlying, Future, Forex, Statement, SaveAppModel

locale.setlocale(locale.LC_ALL, '')


# noinspection PyUnresolvedReferences
class AccountModel(object):
    def set_dict(self, items):
        """
        using raw dict, set related column into property only
        :type items: dict
        """
        properties = vars(self)
        for key, item in items.items():
            if key in properties.keys():
                setattr(self, key, item)

    def get_symbol(self):
        """
        Get either one symbol from model
        underlying or future or forex
        :return: str
        """
        if self.future:
            if self.future.symbol:
                symbol = self.future.symbol
            else:
                symbol = '/%s' % self.future.lookup
        elif self.forex:
            symbol = self.forex.symbol
        else:
            symbol = self.underlying.symbol

        return symbol

    def get_description(self):
        """
        Get either one symbol from model
        underlying or future or forex
        :return: str
        """
        if self.future:
            description = self.future.description
        elif self.forex:
            description = self.forex.description
        else:
            description = self.underlying.company

        return description


class AccountSummary(models.Model):
    statement = models.ForeignKey(Statement)
    date = models.DateField(unique=True)

    net_liquid_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Net Liquid Value'
    )
    stock_buying_power = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Stock Buying Power'
    )
    option_buying_power = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Option Buying Power'
    )
    commissions_ytd = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Commissions YTD'
    )
    futures_commissions_ytd = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Future Commissions YTD'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"net_liquid_value": %.2f, ' % self.net_liquid_value
        output += '"stock_buying_power": %.2f, ' % self.stock_buying_power
        output += '"option_buying_power": %.2f, ' % self.option_buying_power
        output += '"commissions_ytd": %.2f, ' % self.commissions_ytd
        output += '"futures_commissions_ytd": %.2f' % self.futures_commissions_ytd
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        account_statement = 'AccountStatement {date} {net_liquid_value}'

        return account_statement.format(
            date='%s' % self.date,
            net_liquid_value=locale.currency(self.net_liquid_value, grouping=True),
        )


class ForexSummary(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    cash = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Cash'
    )
    upl = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Unrealized P/L'
    )
    floating = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Floating'
    )
    equity = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Equity'
    )
    margin = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Margin'
    )
    available_equity = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Available Equity'
    )
    risk_level = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Risk Level'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"cash": %.2f, ' % self.cash
        output += '"upl": %.2f, ' % self.upl
        output += '"floating": %.2f, ' % self.floating
        output += '"equity": %.2f, ' % self.equity
        output += '"margin": %.2f, ' % self.margin
        output += '"available_equity": %.2f, ' % self.available_equity
        output += '"risk_level": %.2f' % self.risk_level
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'ForexSummary {date} {cash}'

        return output.format(
            date=self.account_summary.date,
            cash=locale.currency(self.cash, grouping=True)
        )


class CashBalance(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    time = models.TimeField(verbose_name='Time')
    contract = models.CharField(max_length=10, verbose_name='Contract')
    ref_no = models.IntegerField(verbose_name='Ref No')
    description = models.CharField(max_length=255, verbose_name='Description')
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Fees')
    commissions = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Commissions'
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Amount')
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Balance')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"time": "%s", ' % self.time
        output += '"contract": "%s", ' % self.contract
        output += '"ref_no": "%s", ' % self.ref_no
        output += '"description": "%s", ' % self.description
        output += '"fees": %.2f, ' % self.fees
        output += '"commissions": %.2f, ' % self.commissions
        output += '"amount": %.2f, ' % self.amount
        output += '"balance": %.2f' % self.balance
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'CashBalance {date} {balance}'

        return output.format(
            date=self.account_summary.date,
            balance=locale.currency(self.balance, grouping=True)
        )


class OrderHistory(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    underlying = models.ForeignKey(Underlying, null=True, blank=True)
    future = models.ForeignKey(Future, null=True, blank=True)
    forex = models.ForeignKey(Forex, null=True, blank=True)

    status = models.CharField(max_length=100, verbose_name='Status')
    pos_effect = models.CharField(max_length=100, verbose_name='Pos Effect')
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Price', null=True, blank=True
    )
    contract = models.CharField(max_length=20, verbose_name='Contract')
    side = models.CharField(max_length=20, verbose_name='Side')
    time_placed = models.DateTimeField(verbose_name='Time Placed')
    spread = models.CharField(max_length=100, verbose_name='Spread')
    expire_date = models.CharField(
        max_length=20, verbose_name='Expire Date', null=True, blank=True
    )
    strike = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike', null=True, blank=True
    )
    tif = models.CharField(max_length=20, verbose_name='TIF')
    order = models.CharField(max_length=20, verbose_name='Order')
    quantity = models.IntegerField(verbose_name='Quantity')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"status": "%s", ' % self.status
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"price": %.2f, ' % self.price
        output += '"contract": "%s", ' % self.contract
        output += '"side": "%s", ' % self.side
        output += '"symbol": "%s", ' % self.get_symbol()
        output += '"time_placed": "%s", ' % self.time_placed.strftime('%Y-%m-%d %H:%M')
        output += '"spread": "%s", ' % self.spread
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"tif": "%s", ' % self.tif
        output += '"order": "%s", ' % self.order
        output += '"quantity": %d' % self.quantity
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'OrderHistory {date} < {symbol} >'

        return output.format(
            symbol=self.get_symbol(),
            date=self.account_summary.date
        )


class TradeHistory(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    underlying = models.ForeignKey(Underlying, null=True, blank=True)
    future = models.ForeignKey(Future, null=True, blank=True)
    forex = models.ForeignKey(Forex, null=True, blank=True)

    execute_time = models.DateTimeField(verbose_name='Execute Time')
    spread = models.CharField(max_length=100, verbose_name='Spread')
    side = models.CharField(max_length=20, verbose_name='Side')
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    pos_effect = models.CharField(max_length=100, verbose_name='Pos Effect')
    expire_date = models.CharField(
        max_length=100, verbose_name='Expire Date', null=True, blank=True
    )
    strike = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike', null=True, blank=True
    )
    contract = models.CharField(max_length=20, verbose_name='Contract')
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Price', null=True, blank=True
    )
    net_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Net Price', null=True, blank=True
    )
    order_type = models.CharField(max_length=100, verbose_name='Order Type')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"execute_time": "%s", ' % self.execute_time.strftime('%Y-%m-%d %H:%M')
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.get_symbol()
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"price": %.2f, ' % self.price
        output += '"net_price": %.2f, ' % self.net_price
        output += '"order_type": "%s"' % self.order_type
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'Trade History {date} < {symbol} >'

        return output.format(
            symbol=self.get_symbol(),
            date=self.account_summary.date
        )


class ProfitLoss(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    # either one but not both
    underlying = models.ForeignKey(Underlying, null=True, blank=True)
    future = models.ForeignKey(Future, null=True, blank=True)

    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Open')
    pl_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Pct')
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Day')
    pl_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL YTD')
    margin_req = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Margin Req')
    mark_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Mark Value',
        null=True, blank=True
    )

    # for position set
    position_set = models.ForeignKey('position.PositionSet', null=True, blank=True, default=None)

    def get_symbol(self):
        """
        Get either one symbol from model
        underlying or future or forex
        :return: str
        """
        if self.future:
            if self.future.symbol:
                symbol = self.future.symbol
            else:
                symbol = '/%s' % self.future.lookup
        else:
            symbol = self.underlying.symbol

        return symbol

    def get_description(self):
        """
        Get either one symbol from model
        underlying or future or forex
        :return: str
        """
        if self.future:
            description = self.future.description
        else:
            description = self.underlying.company

        return description

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"symbol": "%s", ' % self.underlying if self.underlying else self.future
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_pct": %.2f, ' % self.pl_pct
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"pl_ytd": %.2f, ' % self.pl_ytd
        output += '"margin_req": %.2f, ' % self.margin_req
        output += '"mark_value": %.2f' % self.mark_value
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'ProfitLoss {date} < {symbol} >'

        return output.format(
            symbol=self.underlying if self.underlying else self.future,
            date=self.account_summary.date
        )


class HoldingEquity(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)
    underlying = models.ForeignKey(Underlying)

    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Trade Price'
    )
    mark = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Mark',
        null=True, blank=True
    )
    mark_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Mark Value',
        null=True, blank=True
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"description": "%s", ' % self.underlying.company
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_value": %.2f' % self.mark_value
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'HoldingEquity {date} < {symbol} >'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_summary.date
        )


class HoldingOption(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)
    underlying = models.ForeignKey(Underlying)

    option_code = models.CharField(max_length=200, verbose_name='Option Code')
    expire_date = models.CharField(max_length=100, verbose_name='Expire Date')
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Trade Price'
    )
    mark = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Mark',
        null=True, blank=True
    )
    mark_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Mark Value',
        null=True, blank=True
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"option_code": "%s", ' % self.option_code
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_value": %.2f' % self.mark_value
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'Options {date} < {symbol} >'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_summary.date
        )


class FutureStatement(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    execute_date = models.DateField(verbose_name='Execute Date')
    execute_time = models.TimeField(verbose_name='Execute Time')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    ref_no = models.CharField(max_length=100, verbose_name='Reference No')
    description = models.CharField(max_length=255, verbose_name='Description')

    fee = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Fee'
    )
    commission = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Commission'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Amount'
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Balance'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"execute_date": "%s", ' % self.execute_date
        output += '"execute_time": "%s", ' % self.execute_time
        output += '"contract": "%s", ' % self.contract
        output += '"ref_no": "%s", ' % self.ref_no
        output += '"description": "%s", ' % self.description
        output += '"fee": %d, ' % self.fee
        output += '"commission": %.2f, ' % self.commission
        output += '"amount": %.2f, ' % self.amount
        output += '"balance": %.2f' % self.balance
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'FutureStatement {date} < {description} >'

        return output.format(
            date=self.account_summary.date,
            description=self.description
        )


class HoldingFuture(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)
    future = models.ForeignKey(Future)

    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Trade Price'
    )
    mark = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Mark'
    )
    pl_day = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='P/L Day'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"future": "%s", ' % self.future
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"pl_day": %.2f' % self.pl_day
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'HoldingFuture {date} < {future} >'

        return output.format(
            date=self.account_summary.date,
            future=self.future
        )


class ForexStatement(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)

    time = models.TimeField(verbose_name='Time')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    ref_no = models.CharField(max_length=200, verbose_name='Ref No')
    description = models.CharField(max_length=200, verbose_name='Description')
    commissions = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Commissions'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Amount'
    )
    amount_usd = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Amount USD'
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Balance'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"time": "%s", ' % self.time
        output += '"contract": "%s", ' % self.contract
        output += '"ref_no": "%s", ' % self.ref_no
        output += '"description": "%s", ' % self.description
        output += '"commissions": %.2f, ' % self.commissions
        output += '"amount": %.2f, ' % self.amount
        output += '"amount_usd": %.2f, ' % self.amount_usd
        output += '"balance": %.2f' % self.balance
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'ForexStatement {date} {balance}'

        return output.format(
            date=self.account_summary.date,
            balance=locale.currency(self.balance, grouping=True)
        )


class HoldingForex(models.Model, AccountModel):
    account_summary = models.ForeignKey(AccountSummary)
    forex = models.ForeignKey(Forex)

    fpl = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Floating P/L'
    )
    mark = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Mark'
    )
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=12, decimal_places=6, default=0.0, verbose_name='Trade Price'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement_account": "%s", ' % self.account_summary.__unicode__()
        output += '"forex": "%s", ' % self.forex
        output += '"fpl": %.2f, ' % self.fpl
        output += '"mark": %.2f, ' % self.mark
        output += '"quantity": %.2f, ' % self.quantity
        output += '"trade_price": %.2f' % self.trade_price
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = 'HoldingForex {date} < {forex} >'

        return output.format(
            date=self.account_summary.date,
            forex=self.forex
        )


class SaveAccountStatement(SaveAppModel):
    def __init__(self, date, statement, file_data):
        """
        :param date: str
        :param statement: Statement
        :param file_data: str, raw file read
        """
        SaveAppModel.__init__(self, date, statement, file_data)

        acc_data = OpenAcc(data=self.file_data).read()

        self.cash_balance = acc_data['cash_balance']
        self.profit_loss = acc_data['profit_loss']

        self.order_history = acc_data['order_history']
        self.trade_history = acc_data['trade_history']

        self.holding_equity = acc_data['holding_equity']
        self.holding_option = acc_data['holding_option']
        self.holding_future = acc_data['holding_future']
        self.holding_forex = acc_data['holding_forex']

        self.future_statement = acc_data['future_statement']
        self.forex_statement = acc_data['forex_statement']

        self.forex_summary = acc_data['forex_summary']
        self.account_summary = acc_data['account_summary']

        self.account_statement = None

    def save_account_summary(self):
        """
        Save account statement into class property and db
        """
        self.account_statement = AccountSummary(
            statement=self.statement,
            date=self.date,
            **self.account_summary
        )

        self.account_statement.save()

    def save_single_with_underlying(self, save_cls, save_data):
        """
        Save single model into db
        :param save_cls: model class
        :param save_data: list of dict
        """
        for data in save_data:
            if len(data.keys()):
                if 'symbol' in data.keys():
                    if 'description' in data.keys():
                        underlying = self.get_underlying(
                            symbol=data['symbol'],
                            company=data['description'],
                        )
                    else:
                        underlying = self.get_underlying(
                            symbol=data['symbol']
                        )

                    cls_obj = save_cls(
                        account_summary=self.account_statement,
                        underlying=underlying
                    )

                    cls_obj.set_dict(data)
                    cls_obj.save()
                else:
                    cls_obj = save_cls(
                        account_summary=self.account_statement
                    )

                    cls_obj.set_dict(data)
                    cls_obj.save()

    def save_profit_loss(self, save_data):
        """
        Custom save for profit loss table
        including either underlying or future
        :param save_data: list of dict

        pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Open')
        pl_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Pct')
        pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Day')
        pl_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL YTD')
        margin_req = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Margin Req')
        mark_value
        """
        for data in save_data:
            if sum([True for d in data.values() if d == 0.0]) != 6:
                future = None
                underlying = None

                if '/' in data['symbol']:
                    future = self.get_future(
                        symbol=data['symbol'],
                        lookup=data['description']['lookup'],
                        description=data['description']['description'],
                        expire_date=data['description']['expire_date'],
                        session=data['description']['session']
                    )
                else:
                    underlying = self.get_underlying(
                        symbol=data['symbol'],
                        company=data['description']
                    )

                profit_loss = ProfitLoss(
                    account_summary=self.account_statement,
                    underlying=underlying,
                    future=future
                )
                profit_loss.set_dict(data)

                profit_loss.save()

    def save_holding_future(self, save_data):
        """
        For saving future data only
        """
        for data in save_data:
            future = self.get_future(
                lookup=data['lookup'],
                symbol=data['symbol'],
                description=data['description'],
                expire_date=data['expire_date'],
                session=data['session'],
                spc=data['spc']
            )

            holding_future = HoldingFuture(
                account_summary=self.account_statement,
                future=future
            )
            holding_future.set_dict(data)
            holding_future.save()

    def save_holding_forex(self, save_data):
        """
        For saving future data only
        """
        for data in save_data:
            forex = self.get_forex(
                symbol=data['symbol'],
                description=data['description'],
            )

            holding_future = HoldingForex(
                account_summary=self.account_statement,
                forex=forex
            )
            holding_future.set_dict(data)
            holding_future.save()

    def save_history(self, save_cls, save_data):
        """
        Save order history into table with using
        underlying, future or forex foreign key
        """
        for data in save_data:
            underlying = None
            future = None
            forex = None

            if data['contract'] == 'FUTURE':
                future = self.get_future(
                    symbol=data['symbol']
                )
            elif data['contract'] == 'FOREX':
                forex = self.get_forex(
                    symbol=data['symbol']
                )
            else:
                underlying = self.get_underlying(
                    symbol=data['symbol']
                )

            cls_obj = save_cls(
                account_summary=self.account_statement,
                underlying=underlying,
                future=future,
                forex=forex
            )
            cls_obj.set_dict(data)
            cls_obj.save()

    def save_all(self):
        """
        Save all data into position models
        :rtype : int
        """
        self.save_account_summary()

        self.save_holding_future(save_data=self.holding_future)
        self.save_holding_forex(save_data=self.holding_forex)

        self.save_profit_loss(save_data=self.profit_loss)

        self.save_single_with_underlying(save_cls=ForexSummary, save_data=[self.forex_summary])
        self.save_single_with_underlying(save_cls=CashBalance, save_data=self.cash_balance)
        self.save_single_with_underlying(save_cls=ForexStatement, save_data=self.forex_statement)
        self.save_single_with_underlying(save_cls=FutureStatement, save_data=self.future_statement)

        self.save_single_with_underlying(save_cls=HoldingEquity, save_data=self.holding_equity)
        self.save_single_with_underlying(save_cls=HoldingOption, save_data=self.holding_option)

        self.save_history(save_cls=OrderHistory, save_data=self.order_history)
        self.save_history(save_cls=TradeHistory, save_data=self.trade_history)

        return self.account_statement.id
