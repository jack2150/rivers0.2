from django.db.models.query import QuerySet
from position.models import *
# noinspection PyUnresolvedReferences
from tos_import.statement.statement_trade.models import FilledOrder


class ContextLongCall(object):
    def __init__(self, filled_orders, contract_right=100, price_multiply=10):
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

        self.contract_right = contract_right
        self.price_multiply = price_multiply

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.filled_order.strike + self.filled_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.filled_order.strike + self.filled_order.price,
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.filled_order.strike + self.filled_order.price,
            condition='<'
        )
        self.start_loss.save()

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.filled_order.strike + (self.filled_order.price * 10),
            condition='>=',
            limit=False,
            amount=(self.filled_order.price * self.filled_order.quantity
                    * self.price_multiply * self.contract_right)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.filled_order.strike,
            condition='<=',
            limit=True,
            amount=(self.filled_order.price * self.filled_order.quantity
                    * self.contract_right * -1)  # no mini
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


class ContextNakedCall(object):
    def __init__(self, filled_orders, contract_right=100, price_multiply=10):
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

        self.contract_right = contract_right
        self.price_multiply = price_multiply

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """
        self.break_even = BreakEven(
            price=self.filled_order.strike + self.filled_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.filled_order.strike + self.filled_order.price,
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.filled_order.strike + self.filled_order.price,
            condition='>'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.filled_order.strike,
            condition='<=',
            limit=True,
            amount=(self.filled_order.price * self.filled_order.quantity
                    * self.contract_right * -1)
        )
        self.max_profit.save()

        # assume as 10x
        self.max_loss = MaxLoss(
            price=self.filled_order.strike + (self.filled_order.price * self.price_multiply),
            condition='>=',
            limit=False,
            amount=(self.filled_order.price * self.filled_order.quantity
                    * self.price_multiply * self.contract_right)
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


class ContextLongPut(object):
    def __init__(self, filled_orders, contract_right=100, price_multiply=10):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.option_order = filled_orders[0]
        """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right
        self.price_multiply = price_multiply

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.option_order.strike - self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.option_order.strike - self.option_order.price,
            condition='<'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.option_order.strike - self.option_order.price,
            condition='>'
        )
        self.start_loss.save()

        self.max_profit = MaxProfit(
            price=self.option_order.strike - (self.option_order.price * self.price_multiply),
            condition='==',
            limit=True,
            amount=((self.break_even.price -
                    (self.option_order.strike - (self.option_order.price * self.price_multiply)))
                    * self.option_order.quantity * self.contract_right)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=(self.option_order.price * self.option_order.quantity * self.contract_right * -1)
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


class ContextNakedPut(object):
    def __init__(self, filled_orders, contract_right=100, price_multiply=10):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.option_order = filled_orders[0]
        """:type : FilledOrder"""

        self.position_context = None
        self.break_even = None
        self.start_profit = None
        self.start_loss = None
        self.max_profit = None
        self.max_loss = None

        self.contract_right = contract_right
        self.price_multiply = price_multiply

    def create_context(self):
        """
        Create a context model object and that save all data
        :return: PositionContext
        """

        self.break_even = BreakEven(
            price=self.option_order.strike - self.option_order.price,
            condition='=='
        )
        self.break_even.save()

        self.start_profit = StartProfit(
            price=self.option_order.strike - self.option_order.price,
            condition='>'
        )
        self.start_profit.save()

        self.start_loss = StartLoss(
            price=self.option_order.strike - self.option_order.price,
            condition='<'
        )
        self.start_loss.save()

        # assume as 10x
        self.max_profit = MaxProfit(
            price=self.option_order.strike,
            condition='>=',
            limit=True,
            amount=(self.option_order.price * self.option_order.quantity
                    * self.contract_right * -1)
        )
        self.max_profit.save()

        self.max_loss = MaxLoss(
            price=self.option_order.strike - (self.option_order.price * self.price_multiply),
            condition='<=',
            limit=True,
            amount=((self.break_even.price -
                     (self.option_order.strike - (self.option_order.price * self.price_multiply)))
                    * self.option_order.quantity * self.contract_right)
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