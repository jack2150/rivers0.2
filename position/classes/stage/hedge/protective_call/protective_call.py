from django.db.models.query import QuerySet
from position.models import PositionStage


class StageProtectiveCall(object):
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

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
            self.create_max_loss_stage(),
            self.create_loss_stage(),
            self.create_even_stage(),
            self.create_profit_stage()
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = '%.2f == {price}' % float(
            self.stock_order.price - self.option_order.price
        )

        even_stage.price_a = self.stock_order.price - self.option_order.price
        even_stage.amount_a = 0.0

        return even_stage

    def create_max_loss_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = PositionStage()

        max_profit_stage.stage_name = 'MAX_LOSS'
        max_profit_stage.stage_expression = '%.2f <= {price}' % self.option_order.strike

        max_profit_stage.price_a = self.option_order.strike
        max_profit_stage.amount_a = (
            (self.option_order.strike + self.option_order.price - self.stock_order.price)
            * self.stock_order.quantity
        )

        max_profit_stage.left_status = 'easing'
        max_profit_stage.left_expression = '{price_a} <= {new_price} < {old_price}'
        max_profit_stage.right_status = 'worst'
        max_profit_stage.right_expression = '{price_a} <= {old_price} < {new_price}'

        return max_profit_stage

    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'LOSS'
        profit_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.stock_order.price - self.option_order.price),
            float(self.option_order.strike)
        )

        profit_stage.price_a = self.stock_order.price - self.option_order.price
        profit_stage.amount_a = 0.0
        profit_stage.price_b = self.option_order.strike
        profit_stage.amount_b = (
            (self.option_order.strike + self.option_order.price - self.stock_order.price)
            * self.stock_order.quantity
        )

        profit_stage.left_status = 'recovering'
        profit_stage.left_expression = '{price_a} < {new_price} < {old_price} < {price_b}'
        profit_stage.right_status = 'losing'
        profit_stage.right_expression = '{price_a} < {old_price} < {new_price} < {price_b}'

        return profit_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'PROFIT'
        loss_stage.stage_expression = '{price} < %.2f' % (
            float(self.stock_order.price - self.option_order.price)
        )

        loss_stage.price_a = self.stock_order.price - self.option_order.price
        loss_stage.amount_a = 0.0

        loss_stage.left_status = 'decreasing'
        loss_stage.left_expression = '{old_price} < {new_price} < {price_a}'
        loss_stage.right_status = 'profiting'
        loss_stage.right_expression = '{new_price} < {old_price} < {price_a}'

        return loss_stage
