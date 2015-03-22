from django.db.models.query import QuerySet
from position.models import PositionStage


class StageProtectivePut(object):
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

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
            self.create_profit_stage(),
            self.create_even_stage(),
            self.create_loss_stage(),
            self.create_max_loss_stage()
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = '%.2f == {price}' % float(
            self.option_order.net_price
        )

        even_stage.price_a = self.option_order.net_price
        even_stage.amount_a = 0.0

        return even_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = PositionStage()

        max_loss_stage.stage_name = 'MAX_LOSS'
        max_loss_stage.stage_expression = '{price} <= %.2f' % self.option_order.strike

        max_loss_stage.price_a = self.option_order.strike
        max_loss_stage.amount_a = (
            (self.option_order.net_price - self.option_order.strike)
            * self.stock_order.quantity * -1
        )

        max_loss_stage.left_status = 'easing'
        max_loss_stage.left_expression = '{old_price} < {new_price} <= {price_a}'
        max_loss_stage.right_status = 'worst'
        max_loss_stage.right_expression = '{new_price} < {old_price} <= {price_a}'

        return max_loss_stage

    def create_loss_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.option_order.strike),
            float(self.option_order.net_price)
        )

        loss_stage.price_a = self.option_order.strike
        loss_stage.amount_a = (
            (self.option_order.net_price - self.option_order.strike)
            * self.stock_order.quantity * -1
        )
        loss_stage.price_b = self.option_order.net_price
        loss_stage.amount_b = 0.0

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{price_a} < {old_price} < {new_price} < {price_b}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{price_a} < {new_price} < {old_price} < {price_b}'

        return loss_stage

    def create_profit_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'PROFIT'
        loss_stage.stage_expression = '%.2f < {price}' % (
            float(self.option_order.net_price)
        )

        loss_stage.price_a = self.option_order.net_price
        loss_stage.amount_a = 0.0

        loss_stage.left_status = 'decreasing'
        loss_stage.left_expression = '{price_a} < {new_price} < {old_price}'
        loss_stage.right_status = 'profiting'
        loss_stage.right_expression = '{price_a} < {old_price} < {new_price}'

        return loss_stage
