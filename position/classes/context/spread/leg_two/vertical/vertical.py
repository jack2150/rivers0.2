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

        self.start_profit = StartProfit(
            price=self.buy_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.buy_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='<'
        )

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='>=',
            limit=True,
            amount=((self.sell_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='<=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


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

        self.start_profit = StartProfit(
            price=self.buy_order.strike - (self.sell_order.price - self.buy_order.price),
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.buy_order.strike - (self.sell_order.price - self.buy_order.price),
            condition='>'
        )

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.sell_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


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

        self.start_profit = StartProfit(
            price=self.buy_order.strike - (self.buy_order.price - self.sell_order.price),
            condition='<'
        )

        self.start_loss = StartLoss(
            price=self.buy_order.strike - (self.buy_order.price - self.sell_order.price),
            condition='>'
        )

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.break_even.price - self.sell_order.strike)
                    * self.buy_order.quantity * self.contract_right)
        )

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right * -1)
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )


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

        self.start_profit = StartProfit(
            price=self.sell_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='>'
        )

        self.start_loss = StartLoss(
            price=self.sell_order.strike + (self.buy_order.price - self.sell_order.price),
            condition='<'
        )

        self.max_profit = MaxProfit(
            price=self.sell_order.strike,
            condition='<=',
            limit=True,
            amount=((self.break_even.price - self.sell_order.strike)
                    * self.buy_order.quantity * self.contract_right * -1)
        )

        self.max_loss = MaxLoss(
            price=self.buy_order.strike,
            condition='>=',
            limit=True,
            amount=((self.buy_order.strike - self.break_even.price)
                    * self.buy_order.quantity * self.contract_right)
        )

        return dict(
            break_evens=[self.break_even],
            start_profits=[self.start_profit],
            start_losses=[self.start_loss],
            max_profits=[self.max_profit],
            max_losses=[self.max_loss]
        )