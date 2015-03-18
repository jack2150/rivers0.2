import locale
from django.db import models
from position.position_set.manager import PositionSetManager
from tos_import.models import Underlying, Future, Forex


locale.setlocale(locale.LC_ALL, '')
decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


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
    status = models.CharField(max_length=5, verbose_name='Status', default='OPEN')  # open or close

    # underlying
    underlying = models.ForeignKey(Underlying, null=True, blank=True, default=None)
    future = models.ForeignKey(Future, null=True, blank=True, default=None)
    forex = models.ForeignKey(Forex, null=True, blank=True, default=None)

    def __init__(self, *args, **kwargs):
        # super(PositionSet, self).__init__(self, *args, **kwargs)
        models.Model.__init__(self, *args, **kwargs)

        self.manager = PositionSetManager(self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        models.Model.save(
            self, force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )

        # run save then add foreign key items
        if self.manager.filled_orders and self.status == 'OPEN':
            self.manager.context_item_adds('break_evens', 'breakeven_set')
            self.manager.context_item_adds('start_losses', 'startloss_set')
            self.manager.context_item_adds('start_profits', 'startprofit_set')
            self.manager.context_item_adds('max_profits', 'maxprofit_set')
            self.manager.context_item_adds('max_losses', 'maxloss_set')

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

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'PositionSet Id.{id}: < {symbol} > {name}.{spread}'.format(
            id=self.id,
            symbol=self.get_symbol(),
            name=self.name,
            spread=self.spread
        )


class BreakEven(models.Model):
    """
    A break even for a position only have price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    amount = models.DecimalField(null=True, blank=True, verbose_name='Amount', **decimal_field)

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'BreakEven: P {condition} {price}, amount={amount}'.format(
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

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'StartProfit: P {condition} {price}'.format(
            condition=self.condition,
            price=locale.currency(self.price, grouping=True)
        )


class StartLoss(models.Model):
    """
    A position will be start loss after it reach it certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'StartLoss: P {condition} {price}'.format(
            condition=self.condition,
            price=locale.currency(self.price, grouping=True)
        )


class MaxProfit(models.Model):
    """
    A position reach max profit when it reach certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    limit = models.BooleanField(verbose_name='Limit')  # true or false
    amount = models.DecimalField(verbose_name='Amount', **decimal_field)

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'MaxProfit: P {condition} {price}, limit={limit}, amount={amount}'.format(
            condition=self.condition,
            price=locale.currency(self.price, grouping=True),
            limit=self.limit,
            amount=locale.currency(self.amount, grouping=True)
        )


class MaxLoss(models.Model):
    """
    A position reach max profit when it reach certain price and condition
    """
    price = models.DecimalField(verbose_name='Price', **decimal_field)
    condition = models.CharField(max_length=2, verbose_name='Condition')  # <, <=, >, >=, ==
    limit = models.BooleanField(verbose_name='Limit')  # true or false
    amount = models.DecimalField(verbose_name='Amount', **decimal_field)

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'MaxLoss: P {condition} {price}, limit={limit}, amount={amount}'.format(
            condition=self.condition,
            price=locale.currency(self.price, grouping=True),
            limit=self.limit,
            amount=locale.currency(self.amount, grouping=True)
        )










