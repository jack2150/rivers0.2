from django.db.models.query import QuerySet
from position.models import *


class ContextLongCallVertical(object):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.side == 'BUY':
                self.buy_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.side == 'SELL':
                self.sell_order = filled_order
                """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.buy_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.buy_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.buy_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='<'
        )
        self.start_loss.save()

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='>=',
            limit=True,
            amount=((self.sell_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='<=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
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


class ContextShortCallVertical(object):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.side == 'BUY':
                self.buy_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.side == 'SELL':
                self.sell_order = filled_order
                """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.buy_order.strike - (self.sell_order.price - self.buy_order.price),
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.buy_order.strike - (self.sell_order.price - self.buy_order.price),
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.buy_order.strike - (self.sell_order.price - self.buy_order.price),
            condition='>'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.sell_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
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


class ContextLongPutVertical(object):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.side == 'BUY':
                self.buy_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.side == 'SELL':
                self.sell_order = filled_order
                """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.buy_order.strike - (self.buy_order.price - self.sell_order.price),
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.buy_order.strike - (self.buy_order.price - self.sell_order.price),
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.buy_order.strike - (self.buy_order.price - self.sell_order.price),
            condition='>'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.break_even.price - self.sell_order.strike)
                    * self.buy_order.quantity * self.contract_right)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right * -1)
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


class ContextShortPutVertical(object):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.side == 'BUY':
                self.buy_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.side == 'SELL':
                self.sell_order = filled_order
                """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.sell_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.sell_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.sell_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='<'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.break_even.price - self.sell_order.strike)
                    * self.buy_order.quantity * self.contract_right * -1)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
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