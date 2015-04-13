from django.db import models
from django.db.models import Q

decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


class Stock(models.Model):
    """
    Tos stock price only
    multi db not support cross db foreign key
    """
    symbol = models.CharField(max_length=20, verbose_name='Symbol')

    date = models.DateField(verbose_name='Date')
    volume = models.IntegerField(verbose_name='Volume')
    open = models.DecimalField(verbose_name='Open', **decimal_field)
    high = models.DecimalField(verbose_name='High', **decimal_field)
    low = models.DecimalField(verbose_name='Low', **decimal_field)
    close = models.DecimalField(verbose_name='Close', **decimal_field)

    source = models.CharField(max_length=20, default='tos_thinkback', verbose_name='Source')

    def set_dict_data(self, x):
        """
        Set stock dict into model field
        :param x: dict
        """
        self.date = x['date']
        self.volume = x['volume']
        self.open = x['open']
        self.high = x['high']
        self.low = x['low']
        self.close = x['last']

    data = property(fset=set_dict_data)

    def get_data(self, symbol, source='tos_thinkback'):
        """
        """
        pass

    def __unicode__(self):
        """
        Output explain this model
        """
        return 'StockPrice: < {symbol} > {date} from {source}'.format(
            symbol=self.symbol,
            date=self.date,
            source=self.source.upper()
        )


class OptionContract(models.Model):
    """
    Tos option contract only
    """
    symbol = models.CharField(max_length=20, verbose_name='Symbol')

    ex_month = models.CharField(max_length=4, verbose_name='Ex Month')
    ex_year = models.IntegerField(max_length=2, verbose_name='Ex Year')
    right = models.CharField(max_length=20, verbose_name='Right')
    special = models.CharField(max_length=10, verbose_name='Special')
    strike = models.DecimalField(max_length=4, verbose_name='Strike', **decimal_field)
    side = models.CharField(max_length=4, verbose_name='Side')
    option_code = models.CharField(max_length=200, verbose_name='Option Code', unique=True)
    others = models.CharField(max_length=200, default='', blank='', verbose_name='Others')

    source = models.CharField(max_length=20, default='tos_thinkback', verbose_name='Source')

    def set_dict_data(self, x):
        """
        Set stock dict into model field
        :param x: dict
        """
        self.ex_month = x['ex_month']
        self.ex_year = x['ex_year']
        self.right = x['right']
        self.special = x['special']
        self.strike = x['strike']
        self.side = x['side']
        self.option_code = x['option_code']
        self.others = x['others']

    data = property(fset=set_dict_data)

    def __unicode__(self):
        """
        Output explain this model
        """
        return '{right} {special} {ex_month} {ex_year} {strike} {side} {others}'.format(
            right=self.right,
            special=self.special,
            ex_month=self.ex_month,
            ex_year=self.ex_year,
            strike=self.strike,
            side=self.side,
            others=self.others
        )


class Option(models.Model):
    """
    Tos option contract price only
    """
    option_contract = models.ForeignKey(OptionContract)

    date = models.DateField(verbose_name='Date')
    dte = models.IntegerField(max_length=5, verbose_name='DTE')

    bid = models.DecimalField(verbose_name='Bid', **decimal_field)
    ask = models.DecimalField(verbose_name='Ask', **decimal_field)
    last = models.DecimalField(verbose_name='Last', **decimal_field)
    mark = models.DecimalField(verbose_name='Mark', **decimal_field)

    delta = models.DecimalField(verbose_name='Delta', **decimal_field)
    gamma = models.DecimalField(verbose_name='Gamma', **decimal_field)
    theta = models.DecimalField(verbose_name='Theta', **decimal_field)
    vega = models.DecimalField(verbose_name='Vega', **decimal_field)

    theo_price = models.DecimalField(verbose_name='Theo Price', **decimal_field)
    impl_vol = models.DecimalField(verbose_name='Impl Vol', **decimal_field)

    prob_itm = models.DecimalField(verbose_name='Prob ITM', **decimal_field)
    prob_otm = models.DecimalField(verbose_name='Prob OTM', **decimal_field)
    prob_touch = models.DecimalField(verbose_name='Prob Touch', **decimal_field)

    volume = models.IntegerField(verbose_name='DTE')
    open_int = models.IntegerField(verbose_name='Open Interest')

    intrinsic = models.DecimalField(verbose_name='Intrinsic', **decimal_field)
    extrinsic = models.DecimalField(verbose_name='Extrinsic', **decimal_field)

    def set_dict_data(self, x):
        """
        Set stock dict into model field
        :param x: dict
        """
        self.date = x['date']
        self.dte = x['dte']
        self.bid = x['bid']
        self.ask = x['ask']
        self.mark = x['mark']
        self.last = x['last']
        self.delta = x['delta']
        self.gamma = x['gamma']
        self.theta = x['theta']
        self.theo_price = x['theo_price']
        self.impl_vol = x['impl_vol']
        self.prob_itm = x['prob_itm']
        self.prob_otm = x['prob_otm']
        self.prob_touch = x['prob_touch']
        self.volume = x['volume']
        self.open_int = x['open_int']
        self.intrinsic = x['intrinsic']
        self.extrinsic = x['extrinsic']

    data = property(fset=set_dict_data)

    def __unicode__(self):
        """
        Output explain this model
        """
        return '{option_contract} {date}'.format(
            option_contract=self.option_contract,
            date=self.date
        )

# todo: earning, dividend, split, ipo...