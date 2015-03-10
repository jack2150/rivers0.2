from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *
# noinspection PyUnresolvedReferences
from tos_import.statement.statement_trade.models import FilledOrder


class ContextCoveredCall(object):
    def __init__(self, filled_orders):
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
            price=self.stock_order.price - self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.stock_order.price - self.option_order.price,
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.stock_order.price - self.option_order.price,
            condition='<'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=((self.option_order.strike - self.stock_order.price + self.option_order.price)
                    * self.stock_order.quantity)
        )
        self.max_profit.save()

        # assume 50%
        self.max_loss = MaxLoss(
            price=(self.stock_order.price * Decimal(0.5)),
            condition='<=',
            limit=True,
            amount=((self.stock_order.price - self.option_order.price) -
                    (self.stock_order.price * Decimal(0.5))) * -self.stock_order.quantity
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


class ContextProtectiveCall(object):
    def __init__(self, filled_orders):
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
            price=self.stock_order.price - self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.stock_order.price - self.option_order.price,
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.stock_order.price - self.option_order.price,
            condition='>'
        )
        self.start_loss.save()

        # assume 50%
        self.max_profit = MaxProfit(
            price=(self.stock_order.price * Decimal(0.5)),
            condition='<=',
            limit=True,
            amount=((self.stock_order.price - self.option_order.price) -
                    (self.stock_order.price * Decimal(0.5))) * self.stock_order.quantity
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=((self.option_order.strike - self.stock_order.price + self.option_order.price)
                    * -self.stock_order.quantity)
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


class ContextCoveredPut(object):
    def __init__(self, filled_orders):
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
            price=self.stock_order.price + self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.stock_order.price + self.option_order.price,
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.stock_order.price + self.option_order.price,
            condition='>'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.option_order.strike,
            condition='<=',
            limit=True,
            amount=((self.option_order.strike - self.stock_order.price - self.option_order.price)
                    * self.stock_order.quantity)
        )
        self.max_profit.save()

        # assume 50%
        self.max_loss = MaxLoss(
            price=self.stock_order.price * Decimal(1.5),
            condition='>=',
            limit=False,
            amount=((self.stock_order.price + self.option_order.price)
                    - (self.stock_order.price * Decimal(0.5))
                    - self.option_order.price) * self.stock_order.quantity
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


class ContextProtectivePut(object):
    def __init__(self, filled_orders):
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
            price=self.stock_order.price + self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.stock_order.price + self.option_order.price,
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.stock_order.price + self.option_order.price,
            condition='<'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.stock_order.price * Decimal(1.5),
            condition='>=',
            limit=False,
            amount=((self.stock_order.price + self.option_order.price)
                    - (self.stock_order.price * Decimal(0.5))
                    - self.option_order.price) * -self.stock_order.quantity,
        )
        self.max_profit.save()

        # assume 50%
        self.max_loss = MaxLoss(
            price=self.option_order.strike,
            condition='<=',
            limit=True,
            amount=((self.option_order.strike - self.stock_order.price - self.option_order.price)
                    * -self.stock_order.quantity)
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

