from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *


class ContextCoveredCall(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = None
        self.option_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'STOCK':
                self.stock_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'CALL':
                self.option_order = filled_order
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
            price=self.stock_order.price - self.option_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price - self.option_order.price,
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price - self.option_order.price,
            condition='<'
        )

        self.max_profit = MaxProfit(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=(
                (self.option_order.strike - self.stock_order.price + self.option_order.price)
                * self.stock_order.quantity
            )
        )

        self.max_loss = MaxLoss(
            price=(self.stock_order.price * Decimal(1 - self.price_range)),
            condition='<=',
            limit=True,
            amount=(
                (self.break_even.price - (self.stock_order.price * Decimal(1 - self.price_range)))
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


class ContextProtectiveCall(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = None
        self.option_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'STOCK':
                self.stock_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'CALL':
                self.option_order = filled_order
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
            price=self.stock_order.price - self.option_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price - self.option_order.price,
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price - self.option_order.price,
            condition='>'
        )

        # assume 50%
        self.max_profit = MaxProfit(
            price=(self.stock_order.price * Decimal(1 - self.price_range)),
            condition='<=',
            limit=True,
            amount=(
                (self.break_even.price - (self.stock_order.price * Decimal(1 - self.price_range)))
                * self.stock_order.quantity
            )
        )

        self.max_loss = MaxLoss(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=(
                (self.option_order.strike - self.stock_order.price + self.option_order.price)
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


class ContextCoveredPut(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = None
        self.option_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'STOCK':
                self.stock_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.option_order = filled_order
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
            price=self.stock_order.price + self.option_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price + self.option_order.price,
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price + self.option_order.price,
            condition='>'
        )

        self.max_profit = MaxProfit(
            price=self.option_order.strike,
            condition='<=',
            limit=True,
            amount=(
                (self.option_order.strike - self.stock_order.price - self.option_order.price)
                * self.stock_order.quantity
            )
        )

        self.max_loss = MaxLoss(
            price=self.stock_order.price * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=(
                (self.break_even.price -
                 (self.stock_order.price * Decimal(1 + self.price_range)))
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


class ContextProtectivePut(object):
    def __init__(self, filled_orders, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = None
        self.option_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'STOCK':
                self.stock_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.option_order = filled_order
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
            price=self.stock_order.price + self.option_order.price,
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.stock_order.price + self.option_order.price,
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.stock_order.price + self.option_order.price,
            condition='<'
        )

        self.max_profit = MaxProfit(
            price=self.stock_order.price * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(
                ((self.stock_order.price * Decimal(1 - self.price_range)) -
                 self.break_even.price)
                * self.stock_order.quantity
            )
        )

        self.max_loss = MaxLoss(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=(
                (self.option_order.strike - self.stock_order.price - self.option_order.price)
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
