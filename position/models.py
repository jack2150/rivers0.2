from datetime import datetime
import locale
from django.db import models
from pandas.tseries.offsets import BDay
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
    status = models.CharField(max_length=7, verbose_name='Status', default='OPEN')  # open or closed or expired

    # dates
    start_date = models.DateField(verbose_name='Start Date')
    stop_date = models.DateField(null=True, verbose_name='Stop Date')

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
            for stage in self.manager.stages:
                getattr(self, 'positionstage_set').add(stage)

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

    def get_stage(self, price):
        """
        Get current stage for this position set
        loop all stages then determine
        :return: PositionStage
        """
        for position_stage in self.positionstage_set.all():
            if position_stage.in_stage(current_price=price):
                return position_stage

    def current_status(self, new_price, old_price):
        """
        Get current stage status for this position set
        :param new_price: float
        :param old_price: float
        :return: str
        """
        return self.get_stage(price=new_price).get_status(
            new_price=new_price, old_price=old_price
        )

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'PositionSet:{id} < {symbol} > {name}.{spread}'.format(
            id=self.id,
            symbol=self.get_symbol(),
            name=self.name,
            spread=self.spread
        )


class PositionStage(models.Model):
    """
    A stage is a condition that use for compare old and new price
    also tell what is current status that explain price movement
    -----------------------------------
    max_profit: vanishing, guaranteeing
    profit: decreasing, profiting
    breakeven...
    loss: recovering, losing
    max_loss: easing, worst
    -----------------------------------
    """
    stage_name = models.CharField(max_length=20, verbose_name='Name')
    stage_expression = models.CharField(max_length=100, verbose_name='Expression')

    price_a = models.DecimalField(verbose_name='Price_A', **decimal_field)
    amount_a = models.DecimalField(verbose_name='Amount_B', **decimal_field)
    price_b = models.DecimalField(null=True, blank=True, verbose_name='Price_B', **decimal_field)
    amount_b = models.DecimalField(null=True, blank=True, verbose_name='Amount_B', **decimal_field)

    left_expression = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name='Left Expr')
    left_status = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name='Left Status')
    right_expression = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name='Right Expr')
    right_status = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name='Right Status')

    position_set = models.ForeignKey(PositionSet, null=True, blank=True, default=None)

    def in_stage(self, current_price):
        """
        Check price in current stage
        :param current_price: float
        :return: boolean
        """
        return eval(
            self.stage_expression.format(
                current_price=current_price,
                price_a=self.price_a,
                price_b=self.price_b
            )
        )

    def get_status(self, new_price, old_price):
        """
        Use eval to determine left or right condition and return status
        :param new_price: float
        :param old_price: float
        :return: str
        """
        left_result = False
        if self.left_status:
            left_result = eval(
                self.left_expression.format(
                    price_a=self.price_a,
                    price_b=self.price_b,
                    new_price=new_price,
                    old_price=old_price,
                )
            )

        right_result = False
        if self.right_status:
            right_result = eval(
                self.right_expression.format(
                    price_a=self.price_a,
                    price_b=self.price_b,
                    new_price=new_price,
                    old_price=old_price,
                )
            )

        if left_result:
            result = self.left_status
        elif right_result:
            result = self.right_status
        else:
            result = 'UNKNOWN'

        return result

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'Stage: {status} "{expression}"'.format(
            status=self.stage_name,
            expression=self.stage_expression.format(
                current_price='price',
                price_a=self.price_a,
                price_b=self.price_b
            )
        )


class PositionOpinion(models.Model):
    """
    A model that track user opinion on whether the price will be go up or go down
    for a single position only
    """
    position_set = models.ForeignKey(PositionSet)

    date = models.DateField(
        default=datetime.today() + BDay(1),
        verbose_name='Date'
    )

    # opinion direction, up or down
    direction = models.CharField(default=None, null=True, blank=True, max_length=10, verbose_name='Direction')

    # decision to be make
    decision = models.CharField(max_length=100, verbose_name='Decision')

    # quick, simple, deep, analysis... the way to give opinion
    analysis = models.CharField(default='QUICK', max_length=10, verbose_name='Analysis')

    # result for this opinion
    direction_result = models.NullBooleanField(
        default=None, null=True, blank=True, verbose_name='Direction Result'
    )
    decision_result = models.NullBooleanField(
        default=None, null=True, blank=True, verbose_name='Decision Result'
    )

    # description about how, what and why this opinion is make
    description = models.TextField(default='', blank=True, null=True, verbose_name='Description')

    def set_direction_result(self, old_price, new_price):
        """
        Compare old price and new price then set opinion result
        :param old_price: float
        :param new_price: float
        """
        if self.direction_result is None:
            if new_price > old_price:  # bear
                if self.direction == 'BULL':
                    self.direction_result = True
                elif self.direction == 'BEAR':
                    self.direction_result = False
            elif new_price < old_price:  # bull
                if self.direction == 'BULL':
                    self.direction_result = False
                elif self.direction == 'BEAR':
                    self.direction_result = True

            # save result
            self.save()

    def set_decision_result(self, old_pl, new_pl):
        """
        Compare old price and new price then set decision result
        :param old_pl: float
        :param new_pl: float
        """
        if new_pl >= old_pl:
            if self.decision == 'HOLD':
                self.decision_result = True
            else:
                self.decision_result = False

        else:
            if self.decision == 'CLOSE':
                self.decision_result = True
            else:
                self.decision_result = False

        self.save()

    def __unicode__(self):
        """
        Explain this model
        :rtype : str
        """
        return 'Opinion: {symbol} {position_set} {date} {direction} {decision}'.format(
            symbol=self.position_set.get_symbol(),
            position_set=self.position_set.spread,
            date=self.date.strftime('%Y-%m-%d'),
            direction=self.direction,
            decision=self.decision
        )
