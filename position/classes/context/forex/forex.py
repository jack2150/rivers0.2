from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *


class ContextLongForex(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.filled_order = filled_orders[0]
        """:type : FilledOrder"""

        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.price_range = price_range

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.filled_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.filled_order.price,
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.filled_order.price,
            condition='<'
        )

        profit_price = self.filled_order.price * Decimal(1 + self.price_range)
        self.max_profit = MaxProfit(
            price=profit_price,
            condition='>=',
            limit=False,
            amount=(
                ((profit_price * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / profit_price
            )
        )

        loss_price = self.filled_order.price * Decimal(1 - self.price_range)
        self.max_loss = MaxLoss(
            price=loss_price,
            condition='<=',
            limit=True,
            amount=(
                ((loss_price * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / loss_price
            )
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


class ContextShortForex(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.filled_order = filled_orders[0]
        """:type : FilledOrder"""

        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.price_range = price_range

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.filled_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.filled_order.price,
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.filled_order.price,
            condition='>'
        )

        profit_price = self.filled_order.price * Decimal(1 - self.price_range)
        self.max_profit = MaxProfit(
            price=profit_price,
            condition='<=',
            limit=True,
            amount=(
                ((profit_price * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / profit_price
            )
        )

        loss_price = self.filled_order.price * Decimal(1 + self.price_range)
        self.max_loss = MaxLoss(
            price=loss_price,
            condition='>=',
            limit=False,
            amount=(
                ((loss_price * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / loss_price
            )
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


















