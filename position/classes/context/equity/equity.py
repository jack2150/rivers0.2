from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *


class ContextLongStock(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = filled_orders[0]
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
            price=self.stock_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price,
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price,
            condition='<'
        )

        # assume as 100%
        self.max_profit = MaxProfit(
            price=self.stock_order.price * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=(
                (self.stock_order.price * Decimal(self.price_range))
                * self.stock_order.quantity
            )
        )

        self.max_loss = MaxLoss(
            price=self.stock_order.price * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(
                (self.stock_order.price * Decimal(self.price_range))
                * self.stock_order.quantity * -1
            )
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


class ContextShortStock(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = filled_orders[0]
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
            price=self.stock_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price,
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price,
            condition='>'
        )

        self.max_profit = MaxProfit(
            price=self.stock_order.price * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(
                (self.stock_order.price * Decimal(self.price_range))
                * self.stock_order.quantity * -1
            )
        )

        self.max_loss = MaxLoss(
            price=self.stock_order.price * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=(
                (self.stock_order.price * Decimal(self.price_range))
                * self.stock_order.quantity
            )
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )
