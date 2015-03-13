import locale
from django.db import models
from django.db.models import Q
from tos_import.models import Underlying, Future, Forex
#from position.classes.spread.spread import Spread

locale.setlocale(locale.LC_ALL, '')
decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


class BreakEven(models.Model):
    """
    A break even for a position only have price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    amount = models.DecimalField(null=True, blank=True, verbose_name='Amount', **decimal_field)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'BreakEven when price {condition} {price} (amount: {amount})'.format(
            condition=self.condition,
            price=locale.currency(self.price, grouping=True),
            amount=locale.currency(self.amount, grouping=True)
        )


class StartProfit(models.Model):
    """
    A position will be start profit after it reach it price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'StartProfit when price %s %s' % (
            self.condition, locale.currency(self.price, grouping=True)
        )


class StartLoss(models.Model):
    """
    A position will be start loss after it reach it certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'StartLoss when price %s %s' % (
            self.condition, locale.currency(self.price, grouping=True)
        )


class MaxProfit(models.Model):
    """
    A position reach max profit when it reach certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    limit = models.BooleanField(verbose_name='Limit')  # true or false
    amount = models.DecimalField(verbose_name='Amount', **decimal_field)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'MaxProfit when price %s %s (limit: %s, amount: %s)' % (
            self.condition, locale.currency(self.price, grouping=True),
            self.limit, locale.currency(self.amount, grouping=True),

        )


class MaxLoss(models.Model):
    """
    A position reach max profit when it reach certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    limit = models.BooleanField(verbose_name='Limit')  # true or false
    amount = models.DecimalField(verbose_name='Amount', **decimal_field)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'MaxLoss when price %s %s (limit: %s, amount: %s)' % (
            self.condition, locale.currency(self.price, grouping=True),
            self.limit, locale.currency(self.amount, grouping=True),

        )


class PositionContext(models.Model):
    """
    A position profit loss contain mainly 5 sub class
    """
    break_even = models.OneToOneField(
        BreakEven, verbose_name='Break Even', null=True, default=None, blank=True
    )

    start_profit = models.OneToOneField(
        StartProfit, verbose_name='Start Profit', null=True, default=None, blank=True
    )
    start_loss = models.OneToOneField(
        StartLoss, verbose_name='Start Loss', null=True, default=None, blank=True
    )

    max_profit = models.OneToOneField(
        MaxProfit, verbose_name='Max Profit', null=True, default=None, blank=True
    )
    max_loss = models.OneToOneField(
        MaxLoss, verbose_name='Max Loss', null=True, default=None, blank=True
    )

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        break_even = '{price}{condition}P'.format(
            price=locale.currency(self.break_even.price, grouping=True),
            condition=self.break_even.condition
        )
        start_profit = '{condition}{price}'.format(
            price=locale.currency(self.start_profit.price, grouping=True),
            condition=self.start_profit.condition
        )
        start_loss = '{price}{condition}'.format(
            price=locale.currency(self.start_loss.price, grouping=True),
            condition=self.start_loss.condition
        )
        max_profit = '{condition}{price}'.format(
            price=locale.currency(self.max_profit.price, grouping=True),
            condition=self.max_profit.condition
        )
        max_loss = '{price}{condition}'.format(
            price=locale.currency(self.max_loss.price, grouping=True),
            condition=self.max_loss.condition
        )

        return 'PositionContext [{max_loss}:{start_loss}:{break_even}:{start_profit}:{max_profit})'.format(
            max_loss=max_loss,
            start_loss=start_loss,
            break_even=break_even,
            start_profit=start_profit,
            max_profit=max_profit
        )


class PositionContexts(models.Model):
    """
    A position contain 1 or 2 of profit and loss

    break_even = models.ManyToManyField(BreakEven, verbose_name='Break Even A', null=True, default=None, blank=True)

    start_profit = models.ManyToManyField(
        StartProfit, verbose_name='Start Profit A', null=True, default=None, blank=True
    )
    start_loss = models.ManyToManyField(StartLoss, verbose_name='Start Loss A', null=True, default=None, blank=True)

    max_profit = models.ManyToManyField(MaxProfit, verbose_name='Max Profit A', null=True, default=None, blank=True)
    max_loss = models.ManyToManyField(MaxLoss, verbose_name='Max Loss A', null=True, default=None, blank=True)
    """
    left = models.ForeignKey(PositionContext, related_name='position_context_left')
    right = models.ForeignKey(PositionContext, related_name='position_context_right')


class PositionSet(models.Model):
    """
    A position set for equity only, contains:
    1 underlying symbol
    1 to open filled order
    1 to close filled order can be null
    many position instrument
    many profit loss

    contain set contract and spread

    contract is either ['EQUITY', 'OPTION', 'SPREAD', 'FUTURE', 'FOREX']
    spread is model that save all context
    for example, use:
    position_equity_set.spread.pl.start_profit.price
    """
    # name and spread
    name = models.CharField(max_length=100, verbose_name='Name')  # equity, option...
    spread = models.CharField(max_length=100, verbose_name='Spread')  # long stock, naked call...

    # underlying
    underlying = models.ForeignKey(Underlying, null=True, blank=True, default=None)
    future = models.ForeignKey(Future, null=True, blank=True, default=None)
    forex = models.ForeignKey(Forex, null=True, blank=True, default=None)

    # max profit, max loss and others
    context = models.OneToOneField(PositionContext, null=True, blank=True, default=None)
    contexts = models.OneToOneField(PositionContexts, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'PositionSet: < {symbol} > {name}.{spread}'.format(
            symbol=self.underlying.symbol,
            name=self.name,
            spread=self.spread
        )


class SavePositionSet(object):
    """
    Get data from filled orders and insert then into db
    """
    def __init__(self, filled_orders):
        self.filled_orders = filled_orders

    def get_underlying_symbols(self):
        """
        Get underlying symbol from filled orders
        :rtype : list
        """
        underlying_symbols = self.filled_orders.values_list(
            'underlying__symbol', flat=True).distinct()
        underlying_symbols = [str(symbol) for symbol in underlying_symbols if symbol]

        return underlying_symbols

    def get_future_symbols(self):
        """
        Get future symbol from filled orders
        :rtype : list
        """
        future_symbols = self.filled_orders.values_list(
            'future__symbol', flat=True).distinct()
        future_symbols = [str(symbol) for symbol in future_symbols if symbol]  # drop none

        return future_symbols

    def get_forex_symbols(self):
        """
        Get forex symbol from filled orders
        :rtype : list
        """
        forex_symbols = self.filled_orders.values_list(
            'forex__symbol', flat=True).distinct()
        forex_symbols = [str(symbol) for symbol in forex_symbols if symbol]

        return forex_symbols

    def save_underlying_position_set(self):
        """
        """
        underlying_symbols = self.get_underlying_symbols()

        for symbol in underlying_symbols:
            open_orders = self.filled_orders.filter(
                Q(underlying__symbol=symbol) & Q(pos_effect='TO OPEN')
            )
            if open_orders.exists():
                spread = Spread(filled_orders=open_orders)

                spread.name = spread.get_name()
                print 'Underlying: %s' % spread.get_underlying()
                print 'Name: %s' % spread.name
                print 'Spread: %s' % spread.get_spread()
                print '.' * 60

        return None

    def start(self):
        """
        Simple start
        """
        for filled_order in self.filled_orders:
            print filled_order


























