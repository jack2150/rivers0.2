# todo: pips calculation = (1/10000 / 120.87) * 10000
from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *
# noinspection PyUnresolvedReferences
from tos_import.statement.statement_trade.models import FilledOrder


class ContextLongForex(object):
    def __init__(self, filled_orders):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.filled_order = filled_orders[0]
        """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.filled_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.filled_order.price,
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.filled_order.price,
            condition='<'
        )
        self.start_loss.save()

        # assume as +50%
        self.max_profit = MaxProfit(
            price=self.filled_order.price * Decimal(1.5),
            condition='>=',
            limit=False,
            amount=(
                ((self.filled_order.price * Decimal(1.5) * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * Decimal(1.5))
            )
        )
        self.max_profit.save()

        # assume as -50%
        self.max_loss = MaxLoss(
            price=self.filled_order.price * Decimal(0.5),
            condition='<=',
            limit=True,
            amount=(
                ((self.filled_order.price * Decimal(0.5) * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * Decimal(0.5))
            )
        )
        self.max_loss.save()

        self.position_context = PositionContext(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )
        self.position_context.save()

        return self.position_context


class ContextShortForex(object):
    def __init__(self, filled_orders):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.filled_order = filled_orders[0]
        """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.filled_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.filled_order.price,
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.filled_order.price,
            condition='>'
        )
        self.start_loss.save()

        # assume as -50%
        self.max_profit = MaxProfit(
            price=self.filled_order.price * Decimal(0.5),
            condition='<=',
            limit=True,
            amount=(
                ((self.filled_order.price * Decimal(0.5) * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * Decimal(0.5))
            )
        )
        self.max_profit.save()

        # assume as +50%
        self.max_loss = MaxLoss(
            price=self.filled_order.price * Decimal(1.5),
            condition='>=',
            limit=False,
            amount=(
                ((self.filled_order.price * Decimal(1.5) * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * Decimal(1.5))
            )
        )
        self.max_loss.save()

        self.position_context = PositionContext(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )
        self.position_context.save()

        return self.position_context


















