from django.db import models

decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


class DateStat(models.Model):
    """
    Keep daily statistic
    """
    date = models.DateField()

    pl_total = models.DecimalField(verbose_name='Today P/L', **decimal_field)
    pl_ratio = models.FloatField(verbose_name='P/L Ratio', default=0.0)

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return '<DateStat:{date}>'.format(
            date=self.date
        )


class Trade(models.Model):
    """
    keep trade detail for every day
    """
    date_stat = models.ForeignKey(DateStat)

    number = models.IntegerField(default=0, verbose_name='Number of Trades')
    working = models.IntegerField(default=0, verbose_name='Working Trades')
    cancelled = models.IntegerField(default=0, verbose_name='Cancelled Trades')
    filled = models.IntegerField(default=0, verbose_name='Filled Trades')


class Profit(models.Model):
    """
    keep profit position detail for every day
    """
    date_stat = models.ForeignKey(DateStat)

    stock_number = models.IntegerField(default=0, verbose_name='Stock Profit Trade Number')
    stock_total = models.DecimalField(verbose_name='Stock Profit Total', **decimal_field)

    option_number = models.IntegerField(default=0, verbose_name='Option Profit Trade Number')
    option_total = models.DecimalField(verbose_name='Option Profit Total', **decimal_field)

    spread_number = models.IntegerField(default=0, verbose_name='Spread Profit Trade Number')
    spread_total = models.DecimalField(verbose_name='Spread Profit Total', **decimal_field)

    future_number = models.IntegerField(default=0, verbose_name='Future Profit Trade Number')
    future_total = models.DecimalField(verbose_name='Future Profit Total', **decimal_field)

    forex_number = models.IntegerField(default=0, verbose_name='Forex Profit Trade Number')
    forex_total = models.DecimalField(verbose_name='Forex Profit Total', **decimal_field)


class Loss(models.Model):
    """
    keep loss position detail for every day
    """
    date_stat = models.ForeignKey(DateStat)

    stock_number = models.IntegerField(default=0, verbose_name='Stock Loss Trade Number')
    stock_total = models.DecimalField(verbose_name='Stock Loss Total', **decimal_field)

    option_number = models.IntegerField(default=0, verbose_name='Option Loss Trade Number')
    option_total = models.DecimalField(verbose_name='Option Loss Total', **decimal_field)

    spread_number = models.IntegerField(default=0, verbose_name='Spread Loss Trade Number')
    spread_total = models.DecimalField(verbose_name='Spread Loss Total', **decimal_field)

    future_number = models.IntegerField(default=0, verbose_name='Future Loss Trade Number')
    future_total = models.DecimalField(verbose_name='Future Loss Total', **decimal_field)

    forex_number = models.IntegerField(default=0, verbose_name='Forex Loss Trade Number')
    forex_total = models.DecimalField(verbose_name='Forex Loss Total', **decimal_field)


class Holding(models.Model):
    """
    keep today holding position
    """
    date_stat = models.ForeignKey(DateStat)

    stock = models.IntegerField(default=0, verbose_name='Holding Stock')
    option = models.IntegerField(default=0, verbose_name='Holding Option')
    spread = models.IntegerField(default=0, verbose_name='Holding Spread')
    future = models.IntegerField(default=0, verbose_name='Holding Future')
    forex = models.IntegerField(default=0, verbose_name='Holding Forex')
