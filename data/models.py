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
    volume = models.BigIntegerField(verbose_name='Volume')
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
    contract = models.CharField(max_length=4, verbose_name='Contract')
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
        self.contract = x['contract']
        self.option_code = x['option_code']
        self.others = x['others']

    data = property(fset=set_dict_data)

    def __unicode__(self):
        """
        Output explain this model
        """
        return '{right} {special} {ex_month} {ex_year} {strike} {contract}{others}'.format(
            right=self.right,
            special=self.special,
            ex_month=self.ex_month,
            ex_year=self.ex_year,
            strike=self.strike,
            contract=self.contract,
            others=' (%s)' % self.others if self.others else ''
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
        return '{date} {option_contract}'.format(
            date=self.date,
            option_contract=self.option_contract
        )


def get_price(symbol, date, source='tos_thinkback'):
    """
    Universal method that use for get price for one symbol and one date
    :param symbol: str 'AAPL'
    :param date: str '2015-04-02'
    :param source: str ('tos_thinkback', 'google', 'yahoo')
    :return: Stock
    """
    stocks = Stock.objects.filter(Q(symbol=symbol) & Q(date=date) & Q(source=source))

    stock = None
    if stocks.exists():
        stock = stocks.first()
    else:
        stocks = Stock.objects.filter(Q(symbol=symbol) & Q(date=date))

        if stocks.filter(source='tos_thinkback').exists():
            stock = stocks.get(source='tos_thinkback')
        elif stocks.filter(source='google').exists():
            stock = stocks.get(source='google')
        elif stocks.filter(source='yahoo').exists():
            stock = stocks.get(source='yahoo')

    return stock


def get_option(date, option_code='', symbol='', expire_date='', strike=0.0, contract=''):
    """
    Get option data using option_code or symbol + expire date + strike
    :param date: str
    :param symbol: str
    :param expire_date: str
    :param strike: float
    :param option_code: str
    :param contract: str ('CALL', 'PUT')
    :return: Option
    """
    if option_code:
        # using option code
        option_contract = OptionContract.objects.get(option_code=option_code)
        option = option_contract.option_set.get(date=date)
    else:
        # using symbol, expire_date, strike
        ex_month, ex_year = expire_date.split(' ')
        option_contract = OptionContract.objects.get(
            Q(symbol=symbol) &
            Q(ex_month=ex_month) &
            Q(ex_year=ex_year) &
            Q(strike=strike) &
            Q(contract=contract)
        )
        option = option_contract.option_set.get(date=date)

    return option


# todo: earning, dividend, split, ipo...