from django.db.models.query import QuerySet
from position.models import PositionStage


class StageShortPutVertical(object):
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

        self.contract_right = contract_right

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
            self.create_max_profit_stage(),
            self.create_profit_stage(),
            self.create_even_stage(),
            self.create_loss_stage(),
            self.create_max_loss_stage(),
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.price_a = self.sell_order.strike + self.buy_order.price - self.sell_order.price
        even_stage.stage_expression = '%.2f == {price}' % (float(even_stage.price_a))
        even_stage.amount_a = 0.0

        return even_stage

    def create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = PositionStage()

        max_profit_stage.stage_name = 'MAX_PROFIT'
        max_profit_stage.stage_expression = '%.2f <= {price}' % self.sell_order.strike

        max_profit_stage.price_a = self.sell_order.strike
        max_profit_stage.amount_a = (
            (self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
        )

        max_profit_stage.left_status = 'vanishing'
        max_profit_stage.left_expression = '{price_a} <= {new_price} < {old_price}'
        max_profit_stage.right_status = 'guaranteeing'
        max_profit_stage.right_expression = '{price_a} <= {old_price} < {new_price}'

        return max_profit_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = PositionStage()

        max_loss_stage.stage_name = 'MAX_LOSS'
        max_loss_stage.stage_expression = '{price} <= %.2f' % self.buy_order.strike

        max_loss_stage.price_a = self.buy_order.strike
        max_loss_stage.amount_a = (
            (self.sell_order.strike - self.buy_order.strike
             + self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
        )

        max_loss_stage.left_status = 'easing'
        max_loss_stage.left_expression = '{old_price} < {new_price} <= {price_a}'
        max_loss_stage.right_status = 'worst'
        max_loss_stage.right_expression = '{new_price} < {old_price} <= {price_a}'

        return max_loss_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.sell_order.strike + self.buy_order.price - self.sell_order.price),
            float(self.sell_order.strike)
        )

        profit_stage.price_a = self.sell_order.strike + self.buy_order.price - self.sell_order.price
        profit_stage.amount_a = 0.0
        profit_stage.price_b = self.sell_order.strike
        profit_stage.amount_b = (
            (self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
        )

        profit_stage.left_status = 'decreasing'
        profit_stage.left_expression = '{price_a} < {new_price} < {old_price} < {price_b}'
        profit_stage.right_status = 'profiting'
        profit_stage.right_expression = '{price_a} < {old_price} < {new_price} < {price_b}'

        return profit_stage

    # todo: until here
    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.buy_order.strike),
            float(self.sell_order.strike + self.buy_order.price - self.sell_order.price),
        )

        loss_stage.price_a = self.buy_order.strike
        loss_stage.amount_a = (
            (self.sell_order.strike - self.buy_order.strike
             + self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
        )
        loss_stage.price_b = self.sell_order.strike + self.buy_order.price - self.sell_order.price
        loss_stage.amount_b = 0.0

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{price_a} < {old_price} < {new_price} < {price_b}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{price_a} < {new_price} < {old_price} < {price_b}'

        return loss_stage
