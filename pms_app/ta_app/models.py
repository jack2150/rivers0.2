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


class WorkingOrder(models.Model, SampleModel):
    date = models.DateField()
    time_placed = models.DateTimeField()
    spread = models.CharField(max_length=20)
    side = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    pos_effect = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200)
    expire_date = models.CharField(max_length=20)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    order = models.CharField(max_length=20)
    tif = models.CharField(max_length=20)
    mark = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"time_placed": "%s", ' % self.time_placed
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.symbol
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


class FilledOrder(models.Model, SampleModel):
    date = models.DateField()
    exec_time = models.DateTimeField()
    spread = models.CharField(max_length=20)
    side = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    pos_effect = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200)
    expire_date = models.CharField(max_length=20)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    net_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    order = models.CharField(max_length=20)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"exec_time": "%s", ' % self.exec_time
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
        output += '"order": "%s"' % self.order
        output += '}'

        return output


class CancelledOrder(models.Model, SampleModel):
    date = models.DateField()
    time_cancelled = models.DateTimeField()
    spread = models.CharField(max_length=20)
    side = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    pos_effect = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200)
    expire_date = models.CharField(max_length=20)
    strike = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    contract = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    order = models.CharField(max_length=20)
    tif = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"time_cancelled": "%s", ' % self.time_cancelled
        output += '"spread": "%s", ' % self.spread
        output += '"side": "%s", ' % self.side
        output += '"quantity": %d, ' % self.quantity
        output += '"pos_effect": "%s", ' % self.pos_effect
        output += '"symbol": "%s", ' % self.symbol
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"strike": %.2f, ' % self.strike
        output += '"contract": "%s", ' % self.contract
        output += '"price": %.2f, ' % self.price
        output += '"order": "%s",' % self.order
        output += '"tif": "%s",' % self.tif
        output += '"status": "%s"' % self.status
        output += '}'

        return output


class RollingStrategy(models.Model, SampleModel):
    date = models.DateField()

    # option contract name
    strategy = models.CharField(default='Covered Call', max_length=20)
    side = models.CharField(max_length=20)
    symbol = models.CharField(max_length=200)
    right = models.IntegerField(default=100)
    ex_month = models.CharField(max_length=10)
    ex_year = models.IntegerField()
    strike_price = models.DecimalField(max_digits=8, decimal_places=2)
    contract = models.CharField(max_length=10)

    # position details
    new_expire_date = models.CharField(max_length=200)
    call_by = models.CharField(max_length=50)
    days_begin = models.IntegerField(default=0)
    order_price = models.CharField(max_length=50)
    active_time_start = models.TimeField()
    active_time_end = models.TimeField()
    move_to_market_time_start = models.TimeField()
    move_to_market_time_end = models.TimeField()
    status = models.CharField(max_length=20)

    def __unicode__(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"strategy": "%s", ' % self.strategy
        output += '"side": %d, ' % self.side
        output += '"symbol": "%s", ' % self.symbol
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

    # todo: until here... next format ta dict then use for testing