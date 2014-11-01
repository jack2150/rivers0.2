from django.db import models
from lib.io.open_acc import OpenAcc
from pms_app.models import Underlying, Statement


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


class AccountStatement(models.Model):
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
        account_statement = '<Account Statement> {date}, Net Liquid: {net_liquid_value}'

        return account_statement.format(
            date='%s' % self.date,
            net_liquid_value='%.2f' % self.net_liquid_value,
        )


class OrderHistory(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)
    underlying = models.ForeignKey(Underlying)

    status = models.CharField(max_length=50, verbose_name='Status')
    pos_effect = models.CharField(max_length=50, verbose_name='Pos Effect')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Price')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    side = models.CharField(max_length=20, verbose_name='Side')
    time_placed = models.DateTimeField(verbose_name='Time Placed')
    spread = models.CharField(max_length=50, verbose_name='Spread')
    expire_date = models.CharField(max_length=20, verbose_name='Expire Date')
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike')
    tif = models.CharField(max_length=20, verbose_name='TIF')
    order = models.CharField(max_length=20, verbose_name='Order')
    quantity = models.IntegerField(verbose_name='Quantity')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"status": "%s", ' % self.status
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"price": %.2f, ' % self.price
        output += '"contract": "%s", ' % self.contract
        output += '"side": "%s", ' % self.side
        output += '"symbol": "%s", ' % self.underlying.symbol
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
        output = '<Order History> {symbol} {date}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_statement.date
        )


class TradeHistory(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)
    underlying = models.ForeignKey(Underlying)

    execute_time = models.DateTimeField(verbose_name='Execute Time')
    spread = models.CharField(max_length=50, verbose_name='Spread')
    side = models.CharField(max_length=20, verbose_name='Side')
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    pos_effect = models.CharField(max_length=50, verbose_name='Pos Effect')
    expire_date = models.CharField(max_length=50, verbose_name='Expire Date')
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Price')
    net_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Net Price')
    order_type = models.CharField(max_length=50, verbose_name='Order Type')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"execute_time": "%s", ' % self.execute_time.strftime('%Y-%m-%d %H:%M')
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.underlying.symbol
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
        output = '<Trade History> {symbol} {date}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_statement.date
        )


class CashBalance(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)

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
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
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
        output = '<Cash Balance> {date} {time}'

        return output.format(
            date=self.account_statement.date,
            time=self.time
        )


class ProfitsLosses(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)
    underlying = models.ForeignKey(Underlying)

    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Open')
    pl_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Pct')
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL Day')
    pl_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='PL YTD')
    margin_req = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Margin Req')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"description": "%s", ' % self.underlying.company
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_pct": %.2f, ' % self.pl_pct
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"pl_ytd": %.2f, ' % self.pl_ytd
        output += '"margin_req": %.2f' % self.margin_req
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<Profits Losses> {symbol} {date}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_statement.date
        )


class Equities(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)
    underlying = models.ForeignKey(Underlying)

    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Trade Price'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"description": "%s", ' % self.underlying.company
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f' % self.trade_price
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<Equities> {symbol} {date}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_statement.date
        )


class Options(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)
    underlying = models.ForeignKey(Underlying)

    option_code = models.CharField(max_length=200, verbose_name='Option Code')
    expire_date = models.CharField(max_length=50, verbose_name='Expire Date')
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name='Strike')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Trade Price'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"option_code": "%s", ' % self.option_code
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f' % self.trade_price
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<Options> {symbol} {date}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.account_statement.date
        )


class Futures(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)

    trade_date = models.DateField(verbose_name='Trade Date')
    execute_date = models.DateField(verbose_name='Execute Date')
    execute_time = models.TimeField(verbose_name='Execute Time')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    ref_no = models.CharField(max_length=200, verbose_name='Ref No')
    description = models.CharField(max_length=200, verbose_name='Description')
    fees = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Fees'
    )
    commissions = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Commissions'
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Amount'
    )
    balance = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Balance'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
        output += '"trade_date": "%s", ' % self.trade_date
        output += '"execute_date": "%s", ' % self.execute_date
        output += '"execute_time": "%s", ' % self.execute_time
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
        output = '<Futures> {contract} {date}'

        return output.format(
            contract=self.contract,
            date=self.account_statement.date
        )


class Forex(models.Model, AccountModel):
    account_statement = models.ForeignKey(AccountStatement)

    time = models.TimeField(verbose_name='Time')
    contract = models.CharField(max_length=20, verbose_name='Contract')
    ref_no = models.CharField(max_length=200, verbose_name='Ref No')
    description = models.CharField(max_length=200, verbose_name='Description')
    commissions = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Commissions'
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Amount'
    )
    amount_usd = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Amount USD'
    )
    balance = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name='Balance'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"account_statement": "%s", ' % self.account_statement.__unicode__()
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
        output = '<Forex> {date}'

        return output.format(
            date=self.account_statement.date
        )


class SaveAccountStatement(object):
    def __init__(self, date, statement, file_data):
        """
        :param date: str
        :param statement: Statement
        :param file_data: str, raw file read
        """
        self.date = date
        self.statement = statement

        acc_data = OpenAcc(data=file_data).read()

        self.cash_balance = acc_data['cash_balance']
        self.order_history = acc_data['order_history']
        self.trade_history = acc_data['trade_history']
        self.equities = acc_data['equities']
        self.options = acc_data['options']
        self.futures = acc_data['futures']
        self.forex = acc_data['forex']
        self.profits_losses = acc_data['profits_losses']
        self.summary = acc_data['summary']

        self.account_statement = None

        # get all underlying, fast query speed
        self.underlying = Underlying.objects.all()

    def get_underlying(self, symbol, company=''):
        """
        Return saved underlying object from db
        if not exists, save new underlying then return
        :param symbol: str
        :param company: str
        """
        if self.underlying.filter(symbol=symbol).count():
            underlying = self.underlying.get(symbol=symbol)
        else:
            underlying = Underlying(
                symbol=symbol,
                company=company
            )
            underlying.save()

        return underlying

    def save_single(self, save_cls, save_data):
        """
        Save single model into db
        :param save_cls: model class
        :param save_data: list of dict
        """
        for data in save_data:
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
                    account_statement=self.account_statement,
                    underlying=underlying
                )

                cls_obj.set_dict(data)
                cls_obj.save()
            else:
                cls_obj = save_cls(
                    account_statement=self.account_statement
                )

                cls_obj.set_dict(data)
                cls_obj.save()

    def save_all(self):
        """
        Save all data into position models
        """
        self.account_statement = AccountStatement(
            statement=self.statement,
            date=self.date,
            **self.summary
        )
        self.account_statement.save()

        self.save_single(save_cls=ProfitsLosses, save_data=self.profits_losses)
        self.save_single(save_cls=TradeHistory, save_data=self.trade_history)
        self.save_single(save_cls=OrderHistory, save_data=self.order_history)
        self.save_single(save_cls=Equities, save_data=self.equities)
        self.save_single(save_cls=Options, save_data=self.options)
        self.save_single(save_cls=CashBalance, save_data=self.cash_balance)
        self.save_single(save_cls=Futures, save_data=self.futures)
        self.save_single(save_cls=Forex, save_data=self.forex)
