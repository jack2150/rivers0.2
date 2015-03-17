from decimal import Decimal
from django.db.models.query import QuerySet
from position.models import *


class ContextLongCombo(object):
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

        self.left_context = None
        self.right_context = None
        self.position_contexts = None
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
        self.position_contexts = PositionContexts(
            left=self.create_left_context(),  # put
            right=self.create_right_context()  # call
        )
        self.position_contexts.save()

        return self.position_contexts

    def create_left_context(self):
        """
        Left position context only
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.put_order.strike,
            condition='>=',
            amount=((self.put_order.price - self.call_order.price)
                    * self.call_order.quantity * self.contract_right)
        )
        self.break_even.save()

        self.start_loss = StartLoss(
            price=self.put_order.strike,
            condition='<'
        )
        self.start_loss.save()

        self.max_loss = MaxLoss(
            price=self.put_order.strike * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=(((self.put_order.strike * Decimal(self.price_range)
                    * self.put_order.quantity * self.contract_right)
                     + self.break_even.amount))
        )
        self.max_loss.save()

        self.left_context = PositionContext(
            break_even=self.break_even,
            start_loss=self.start_loss,
            max_loss=self.max_loss
        )
        self.left_context.save()

        return self.left_context

    def create_right_context(self):
        """
        Right position context
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.call_order.strike,
            condition='<=',
            amount=((self.put_order.price - self.call_order.price)
                    * self.call_order.quantity * self.contract_right)
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.call_order.strike,
            condition='>'
        )
        self.start_profit.save()

        # assume as strike +20%
        self.max_profit = MaxProfit(
            price=self.call_order.strike * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=round(((self.call_order.strike * Decimal(self.price_range))
                          * self.call_order.quantity * self.contract_right)
                         + self.break_even.amount, 2)
        )
        self.max_profit.save()

        self.right_context = PositionContext(
            break_even=self.break_even,
            start_profit=self.start_profit,
            max_profit=self.max_profit,
        )
        self.right_context.save()

        return self.right_context


class ContextShortCombo(object):
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

        self.left_context = None
        self.right_context = None
        self.position_contexts = None
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
        self.position_contexts = PositionContexts(
            left=self.create_left_context(),  # put
            right=self.create_right_context()  # call
        )
        self.position_contexts.save()

        return self.position_contexts

    def create_left_context(self):
        """
        Left position context only
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.put_order.strike,
            condition='>=',
            amount=((self.put_order.price - self.call_order.price)
                    * self.call_order.quantity * self.contract_right)
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.put_order.strike,
            condition='<'
        )
        self.start_profit.save()

        self.max_profit = MaxProfit(
            price=self.put_order.strike * Decimal(1 - self.price_range),
            condition='<=',
            limit=True,
            amount=round(((self.put_order.strike * Decimal(self.price_range))
                          * self.put_order.quantity * self.contract_right)
                         + self.break_even.amount, 2)
        )
        self.max_profit.save()

        self.left_context = PositionContext(
            break_even=self.break_even,
            start_profit=self.start_profit,
            max_profit=self.max_profit
        )
        self.left_context.save()

        return self.left_context

    def create_right_context(self):
        """
        Right position context
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.call_order.strike,
            condition='<=',
            amount=((self.put_order.price - self.call_order.price)
                    * self.call_order.quantity * self.contract_right)
        )
        self.break_even.save()

        self.start_loss = StartLoss(
            price=self.call_order.strike,
            condition='>'
        )
        self.start_loss.save()

        self.max_loss = MaxLoss(
            price=self.call_order.strike * Decimal(1 + self.price_range),
            condition='>=',
            limit=False,
            amount=round((((self.call_order.strike * Decimal(self.price_range)
                            * self.call_order.quantity * self.contract_right)
                           + self.break_even.amount)), 2)
        )
        self.max_loss.save()

        self.right_context = PositionContext(
            break_even=self.break_even,
            start_loss=self.start_loss,
            max_loss=self.max_loss,
        )
        self.right_context.save()

        return self.right_context
