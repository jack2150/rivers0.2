from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *


class ContextLongStraddle(object):
    def __init__(self, filled_orders, contract_right=100, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.call_order = None
        self.put_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'CALL':
                self.call_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.put_order = filled_order
                """:type : FilledOrder"""

        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        # maintain later using position right
        self.contract_right = contract_right

        # range for max profit
        self.price_range = price_range

    def create_context(self):
        """
        Create a context model object and that save all data
        2 max profit, 1 max loss, 2 break even, 2 start profit, 2 start loss,
        :return: PositionContexts
        """
        left_context = self.create_left_context()
        right_context = self.create_right_context()

        return dict(
            break_evens=[left_context['break_even'], right_context['break_even']],
            start_profits=[left_context['start_profit'], right_context['start_profit']],
            start_losses=[left_context['start_loss'], right_context['start_loss']],
            max_profits=[left_context['max_profit'], right_context['max_profit']],
            max_losses=[left_context['max_loss'], right_context['max_loss']]
        )

    def create_left_context(self):
        """
        Left position context only
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='>'
        )

        # assume as breakeven -20%
        self.max_profit = MaxProfit(
            price=self.break_even.price * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(((self.break_even.price * Decimal(1 - self.price_range))
                     - self.break_even.price) * Decimal(self.contract_right) * -1)
        )

        self.max_loss = MaxLoss(
            price=self.put_order.strike,
            condition='==',
            limit=True,
            amount=((self.call_order.price + self.put_order.price)
                    * self.put_order.quantity * Decimal(-self.contract_right))
        )

        return dict(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )

    def create_right_context(self):
        """
        Right position context
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='<'
        )

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.break_even.price * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=(((self.break_even.price * Decimal(1 + self.price_range))
                     - self.break_even.price) * Decimal(self.contract_right))
        )

        self.max_loss = MaxLoss(
            price=self.call_order.strike,
            condition='==',
            limit=True,
            amount=((self.call_order.price + self.put_order.price)
                    * self.put_order.quantity * Decimal(self.contract_right) * -1)
        )

        return dict(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )


class ContextShortStraddle(object):
    def __init__(self, filled_orders, contract_right=100, price_range=0.2):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.call_order = None
        self.put_order = None
        for filled_order in filled_orders:
            if filled_order.contract == 'CALL':
                self.call_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.put_order = filled_order
                """:type : FilledOrder"""

        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        # maintain later using position right
        self.contract_right = contract_right

        # range for max profit
        self.price_range = price_range

    def create_context(self):
        """
        Create a context model object and that save all data
        2 max profit, 1 max loss, 2 break even, 2 start profit, 2 start loss,
        :return: PositionContexts
        """
        left_context = self.create_left_context()
        right_context = self.create_right_context()

        return dict(
            break_evens=[left_context['break_even'], right_context['break_even']],
            start_profits=[left_context['start_profit'], right_context['start_profit']],
            start_losses=[left_context['start_loss'], right_context['start_loss']],
            max_profits=[left_context['max_profit'], right_context['max_profit']],
            max_losses=[left_context['max_loss'], right_context['max_loss']]
        )

    def create_left_context(self):
        """
        Left position context only
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.put_order.strike - (self.call_order.price + self.put_order.price),
            condition='<'
        )

        # assume as breakeven -20%
        self.max_profit = MaxProfit(
            price=self.put_order.strike,
            condition='==',
            limit=True,
            amount=((self.call_order.price + self.put_order.price) * self.put_order.quantity
                    * Decimal(self.contract_right) * -1)

        )

        self.max_loss = MaxLoss(
            price=self.break_even.price * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(((self.break_even.price * Decimal(1 - self.price_range))
                     - self.break_even.price) * Decimal(self.contract_right))
        )

        return dict(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )

    def create_right_context(self):
        """
        Right position context
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='=='
        )

        self.start_profit = StartProfit(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.call_order.strike + (self.call_order.price + self.put_order.price),
            condition='>'
        )

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.call_order.strike,
            condition='==',
            limit=True,
            amount=((self.call_order.price + self.put_order.price) * self.put_order.quantity
                    * Decimal(self.contract_right) * -1)
        )

        self.max_loss = MaxLoss(
            price=self.break_even.price * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=(((self.break_even.price * Decimal(1 + self.price_range))
                     - self.break_even.price) * Decimal(self.contract_right) * -1)
        )

        return dict(
            break_even=self.break_even,
            start_profit=self.start_profit,
            start_loss=self.start_loss,
            max_profit=self.max_profit,
            max_loss=self.max_loss
        )

