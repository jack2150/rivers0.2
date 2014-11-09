from django.db import models
from lib.io.open_ta import OpenTA
from pms_app.models import Underlying, Statement


class TaModel(object):
    def set_dict(self, items):
        """
        using raw dict, set related column into property only
        :type items: dict
        """
        properties = vars(self)

        for key, item in items.items():
            if key in properties.keys():
                setattr(self, key, item)


class TradeActivity(models.Model):
    statement = models.ForeignKey(Statement)
    date = models.DateField(unique=True, verbose_name="Date")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"statement": "%s", ' % self.statement
        output += '"date": "%s", ' % self.date
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<Trade Activity> {date}'

        return output.format(
            date=self.date
        )

    class Meta:
        verbose_name_plural = " Trade Activity"


class WorkingOrder(models.Model, TaModel):
    trade_activity = models.ForeignKey(TradeActivity)
    underlying = models.ForeignKey(Underlying)

    time_placed = models.DateTimeField(verbose_name="Time Placed")
    spread = models.CharField(max_length=20, verbose_name="Spread")
    side = models.CharField(max_length=20, verbose_name="Side")
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    pos_effect = models.CharField(max_length=200, verbose_name="Pos Effect")
    expire_date = models.CharField(max_length=20, verbose_name="Expire Date", null=True, blank=True)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Strike")
    contract = models.CharField(max_length=20, verbose_name="Contract")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Price")
    order = models.CharField(max_length=20, verbose_name="Order")
    tif = models.CharField(max_length=20, verbose_name="TIF")
    mark = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark")
    status = models.CharField(max_length=20, verbose_name="Status")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.trade_activity.date
        output += '"time_placed": "%s", ' % self.time_placed
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"price": %.2f, ' % self.price
        output += '"order": "%s", ' % self.order
        output += '"tif": "%s", ' % self.tif
        output += '"mark": %.2f, ' % self.mark
        output += '"status": "%s"' % self.status
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<WorkingOrder:{date}> {symbol}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.trade_activity.date
        )


class FilledOrder(models.Model, TaModel):
    trade_activity = models.ForeignKey(TradeActivity)
    underlying = models.ForeignKey(Underlying)

    exec_time = models.DateTimeField(verbose_name="Execute Time")
    spread = models.CharField(max_length=20, verbose_name="Spread")
    side = models.CharField(max_length=20, verbose_name="Side")
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    pos_effect = models.CharField(max_length=200, verbose_name="Pos Effect")
    expire_date = models.CharField(max_length=20, verbose_name="Expire Date", null=True, blank=True)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Strike")
    contract = models.CharField(max_length=20, verbose_name="Contract")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Price")
    net_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Net Price")
    order = models.CharField(max_length=20, verbose_name="Order")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.trade_activity.date
        output += '"exec_time": "%s", ' % self.exec_time
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
        output += '"order": "%s"' % self.order
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<FilledOrder:{date}> {symbol}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.trade_activity.date
        )


class CancelledOrder(models.Model, TaModel):
    trade_activity = models.ForeignKey(TradeActivity)
    underlying = models.ForeignKey(Underlying)

    time_cancelled = models.DateTimeField(verbose_name="Time Cancelled")
    spread = models.CharField(max_length=20, verbose_name="Spread")
    side = models.CharField(max_length=20, verbose_name="Side")
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    pos_effect = models.CharField(max_length=200, verbose_name="Pos Effect")
    expire_date = models.CharField(max_length=20, verbose_name="Expire Date", null=True, blank=True)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Strike")
    contract = models.CharField(max_length=20, verbose_name="Contract")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Price")
    order = models.CharField(max_length=20, verbose_name="Order")
    tif = models.CharField(max_length=20, verbose_name="TIF")
    status = models.CharField(max_length=20, verbose_name="Status")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.trade_activity.date
        output += '"time_cancelled": "%s", ' % self.time_cancelled
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"price": %.2f, ' % self.price
        output += '"order": "%s",' % self.order
        output += '"tif": "%s",' % self.tif
        output += '"status": "%s"' % self.status
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        output = '<CancelledOrder:{date}> {symbol}'

        return output.format(
            symbol=self.underlying.symbol,
            date=self.trade_activity.date
        )


class RollingStrategy(models.Model, TaModel):
    trade_activity = models.ForeignKey(TradeActivity)
    underlying = models.ForeignKey(Underlying)

    # option contract name
    # no special for rolling strategy because all will auto use month to month contract
    strategy = models.CharField(default='Covered Call', max_length=20, verbose_name="Strategy")
    side = models.IntegerField(default=0, verbose_name="Side")
    right = models.IntegerField(default=100, verbose_name="Right")
    ex_month = models.CharField(max_length=10, verbose_name="Expire Month")
    ex_year = models.IntegerField(verbose_name="Expire Year")
    strike_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Strike Price")
    contract = models.CharField(max_length=10, verbose_name="Contract")

    # position details
    new_expire_date = models.CharField(max_length=200, verbose_name="New Expire Date")
    call_by = models.CharField(max_length=50, verbose_name="Call By")
    days_begin = models.IntegerField(default=0, verbose_name="Days Begin")
    order_price = models.CharField(max_length=50, verbose_name="Order Price")
    active_time_start = models.TimeField(verbose_name="Active Time Start")
    active_time_end = models.TimeField(verbose_name="Active Time End")
    move_to_market_time_start = models.TimeField(verbose_name="Move Market Time Start")
    move_to_market_time_end = models.TimeField(verbose_name="Move Market Time End")
    status = models.CharField(max_length=20, verbose_name="Status")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.trade_activity.date
        output += '"strategy": "%s", ' % self.strategy
        output += '"side": %d, ' % self.side
        output += '"symbol": "%s", ' % self.underlying.symbol
        output += '"right": %d, ' % self.right
        output += '"ex_month": "%s", ' % self.ex_month
        output += '"ex_year": %d, ' % self.ex_year
        output += '"strike_price": %.2f, ' % self.strike_price
        output += '"contract": "%s", ' % self.contract
        output += '"new_expire_date": "%s", ' % self.new_expire_date
        output += '"call_by": "%s", ' % self.call_by
        output += '"days_begin": "%s", ' % self.days_begin
        output += '"order_price": "%s", ' % self.order_price
        output += '"active_time_start": "%s", ' % self.active_time_start
        output += '"active_time_end": "%s", ' % self.active_time_end
        output += '"move_to_market_time_start": "%s", ' % self.move_to_market_time_start
        output += '"move_to_market_time_end": "%s", ' % self.move_to_market_time_end
        output += '"status": "%s"' % self.status
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        option = '{symbol} {right} {ex_month} {ex_year} {strike_price} {contract}'
        output = '<RollingStrategy:{date}> {option}'

        return output.format(
            option=option.format(
                symbol=self.underlying.symbol,
                right=self.right,
                ex_month=self.ex_month,
                ex_year=self.ex_year,
                strike_price=self.strike_price,
                contract=self.contract
            ),
            date=self.trade_activity.date
        )


class SaveTradeActivity(object):
    def __init__(self, date, statement, file_data):
        """
        :param date: str
        :param statement: Statement
        :param file_data: str, raw file read
        """
        self.date = date
        self.statement = statement

        ta_data = OpenTA(data=file_data).read()

        self.working_order = ta_data['working_order']
        self.filled_order = ta_data['filled_order']
        self.cancelled_order = ta_data['cancelled_order']
        self.rolling_strategy = ta_data['rolling_strategy']

        self.trade_activity = None

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
                    trade_activity=self.trade_activity,
                    underlying=underlying
                )

                cls_obj.set_dict(data)
                cls_obj.save()
            else:
                cls_obj = save_cls(
                    trade_activity=self.trade_activity
                )

                cls_obj.set_dict(data)
                cls_obj.save()

    def save_all(self):
        """
        Save all data into position models
        """
        self.trade_activity = TradeActivity(
            statement=self.statement,
            date=self.date
        )
        self.trade_activity.save()

        self.save_single(save_cls=WorkingOrder, save_data=self.working_order)
        self.save_single(save_cls=FilledOrder, save_data=self.filled_order)
        self.save_single(save_cls=CancelledOrder, save_data=self.cancelled_order)
        self.save_single(save_cls=RollingStrategy, save_data=self.rolling_strategy)
