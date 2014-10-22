from django.db import models


class SampleModel(object):
    def set_dict(self, items):
        """
        using raw dict, set related column into property only
        :type items: dict
        """
        properties = vars(self)

        for key, item in items.items():
            if key in properties.keys():
                setattr(self, key, item)


class CashBalance(models.Model, SampleModel):
    date = models.DateField()
    time = models.TimeField()
    contract = models.CharField(max_length=10)
    ref_no = models.IntegerField()
    description = models.CharField(max_length=255)
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    commissions = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
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


class ProfitsLosses(models.Model, SampleModel):
    date = models.DateField()
    symbol = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    margin_req = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"symbol": "%s", ' % self.symbol
        output += '"description": "%s", ' % self.description
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_pct": %.2f, ' % self.pl_pct
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"pl_ytd": %.2f, ' % self.pl_ytd
        output += '"margin_req": %.2f' % self.margin_req
        output += '}'

        return output


class AccountSummary(models.Model, SampleModel):
    date = models.DateField()
    net_liquid_value = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    stock_buying_power = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    option_buying_power = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    commissions_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    futures_commissions_ytd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
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


class OrderHistory(models.Model, SampleModel):
    date = models.DateField()
    status = models.CharField(max_length=50)
    pos_effect = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    side = models.CharField(max_length=20)
    symbol = models.CharField(max_length=50)
    time_placed = models.DateTimeField()
    spread = models.CharField(max_length=50)
    expire_date = models.CharField(max_length=20)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    tif = models.CharField(max_length=20)
    order = models.CharField(max_length=20)
    quantity = models.IntegerField()

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"status": "%s", ' % self.status
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"price": %.2f, ' % self.price
        output += '"contract": "%s", ' % self.contract
        output += '"side": "%s", ' % self.side
        output += '"symbol": "%s", ' % self.symbol
        output += '"time_placed": "%s", ' % self.time_placed.strftime('%Y-%m-%d %H:%M')
        output += '"spread": "%s", ' % self.spread
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"tif": "%s", ' % self.tif
        output += '"order": "%s", ' % self.order
        output += '"quantity": %d' % self.quantity
        output += '}'

        return output


class TradeHistory(models.Model, SampleModel):
    date = models.DateField()
    execute_time = models.DateTimeField()
    spread = models.CharField(max_length=50)
    side = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    pos_effect = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)
    expire_date = models.CharField(max_length=50)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    net_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    order_type = models.CharField(max_length=50)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"execute_time": "%s", ' % self.execute_time.strftime('%Y-%m-%d %H:%M')
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.symbol
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"price": %.2f, ' % self.price
        output += '"net_price": %.2f, ' % self.net_price
        output += '"order_type": "%s"' % self.order_type
        output += '}'

        return output


class Equities(models.Model, SampleModel):
    date = models.DateField()
    symbol = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    trade_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"symbol": "%s", ' % self.symbol
        output += '"description": "%s", ' % self.description
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f' % self.trade_price
        output += '}'

        return output


class Options(models.Model, SampleModel):
    date = models.DateField()
    symbol = models.CharField(max_length=50)
    option_code = models.CharField(max_length=200)
    expire_date = models.CharField(max_length=50)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    trade_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"symbol": "%s", ' % self.symbol
        output += '"option_code": "%s", ' % self.option_code
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"quantity": %d, ' % self.quantity
        output += '"trade_price": %.2f' % self.trade_price
        output += '}'

        return output


class Futures(models.Model, SampleModel):
    date = models.DateField()
    trade_date = models.DateField()
    execute_date = models.DateField()
    execute_time = models.TimeField()
    contract = models.CharField(max_length=20)
    ref_no = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    commissions = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
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


class Forex(models.Model, SampleModel):
    date = models.DateField()
    time = models.TimeField()
    contract = models.CharField(max_length=20)
    ref_no = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    commissions = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    amount_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
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












































