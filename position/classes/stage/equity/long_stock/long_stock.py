from django.db.models.query import QuerySet
from position.models import PositionStage


class StageLongStock(object):
    def __init__(self, filled_orders):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.stock_order = filled_orders[0]
        """:type : FilledOrder"""

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
            self.create_profit_stage(),
            self.create_even_stage(),
            self.create_loss_stage()
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = '%.2f == {price}' % self.stock_order.price

        even_stage.price_a = self.stock_order.price
        even_stage.amount_a = 0.0

        return even_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = '%.2f < {price}' % self.stock_order.price

        profit_stage.price_a = self.stock_order.price
        profit_stage.amount_a = 0.0

        profit_stage.left_status = 'decreasing'
        profit_stage.left_expression = '{price_a} < {new_price} < {old_price}'
        profit_stage.right_status = 'profiting'
        profit_stage.right_expression = '{price_a} < {old_price} < {new_price}'

        return profit_stage

    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '{price} < %.2f' % self.stock_order.price

        loss_stage.price_a = self.stock_order.price
        loss_stage.amount_a = 0.0

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{old_price} < {new_price} < {price_a}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{new_price} < {old_price} < {price_a}'

        return loss_stage
