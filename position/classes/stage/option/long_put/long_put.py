from django.db.models.query import QuerySet
from position.models import PositionStage


class StageLongPut(object):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.put_order = filled_orders[0]
        """:type : FilledOrder"""

        self.contract_right = contract_right

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
        even_stage.stage_expression = '%.2f == {price}' % (
            float(self.put_order.strike - self.put_order.price)
        )

        even_stage.price_a = self.put_order.strike - self.put_order.price
        even_stage.amount_a = 0.0

        return even_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = PositionStage()

        max_loss_stage.stage_name = 'MAX_LOSS'
        max_loss_stage.stage_expression = '%.2f <= {price}' % (
            float(self.put_order.strike)
        )

        max_loss_stage.price_a = self.put_order.strike
        max_loss_stage.amount_a = (
            self.put_order.price * self.put_order.quantity * self.contract_right * -1
        )

        max_loss_stage.left_status = 'easing'
        max_loss_stage.left_expression = '{price_a} <= {new_price} < {old_price}'
        max_loss_stage.right_status = 'worst'
        max_loss_stage.right_expression = '{price_a} <= {old_price} < {new_price}'

        return max_loss_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = '{price} < %.2f' % (
            float(self.put_order.strike - self.put_order.price)
        )

        profit_stage.price_a = self.put_order.strike - self.put_order.price
        profit_stage.amount_a = 0.0

        profit_stage.left_status = 'decreasing'
        profit_stage.left_expression = '{old_price} < {new_price} < {price_a}'
        profit_stage.right_status = 'profiting'
        profit_stage.right_expression = '{new_price} < {old_price} < {price_a}'

        return profit_stage

    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.put_order.strike - self.put_order.price),
            float(self.put_order.strike)
        )

        loss_stage.price_a = self.put_order.strike - self.put_order.price
        loss_stage.amount_a = 0.0
        loss_stage.price_b = self.put_order.strike
        loss_stage.amount_b = (
            self.put_order.price * self.put_order.quantity * self.contract_right * -1
        )

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{price_a} < {new_price} < {old_price} < {price_b}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{price_a} < {old_price} < {new_price} < {price_b}'

        return loss_stage
