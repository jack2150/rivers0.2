from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage
from position.models import PositionStage


class StageShortStrangle(Stage):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.contract == 'CALL':
                self.call_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.put_order = filled_order
                """:type : FilledOrder"""

        # set net price
        if self.call_order.net_price:
            self.net_price = self.call_order.net_price
        else:
            self.net_price = self.put_order.net_price

        # mid price
        self.center_price = round(self.put_order.strike + (
            (self.call_order.strike - self.put_order.strike) / 2
        ), 2)

        self.contract_right = contract_right

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
            self.create_loss_stage1(),
            self.create_even_stage1(),
            self.create_profit_stage1(),
            self.create_max_profit_stage1(),
            self.create_max_profit_stage2(),
            self.create_profit_stage2(),
            self.create_even_stage2(),
            self.create_loss_stage2()
        ]

    def create_even_stage1(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'

        even_stage.stage_expression = self.e_price

        even_stage.price_a = self.call_order.strike + self.net_price

        return even_stage

    def create_even_stage2(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        even_stage.stage_expression = self.e_price

        even_stage.price_a = self.put_order.strike - self.net_price

        return even_stage

    def create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.gt_price

        loss_stage.price_a = self.call_order.strike + self.net_price
        loss_stage.amount_a = 0.0

        loss_stage.left_expression = self.gt_price_lower
        loss_stage.right_expression = self.gt_price_higher

        return loss_stage

    def create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.lt_price

        loss_stage.price_a = self.put_order.strike - self.net_price
        loss_stage.amount_a = 0.0

        loss_stage.left_expression = self.lt_price_higher
        loss_stage.right_expression = self.lt_price_lower

        return loss_stage

    def create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        profit_stage.stage_expression = self.price_range

        profit_stage.price_a = self.call_order.strike
        profit_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        profit_stage.price_b = self.call_order.strike + self.net_price
        profit_stage.amount_b = 0.0

        profit_stage.left_expression = self.price_range_higher
        profit_stage.right_expression = self.price_range_lower

        return profit_stage

    def create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = self.price_range

        profit_stage.price_a = self.put_order.strike - self.net_price
        profit_stage.amount_a = 0.0
        profit_stage.price_b = self.put_order.strike
        profit_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        profit_stage.left_expression = self.price_range_lower
        profit_stage.right_expression = self.price_range_higher

        return profit_stage

    def create_max_profit_stage1(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = '{price_a} <= {current_price} <= {price_b}'

        max_profit_stage.price_a = self.center_price
        max_profit_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        max_profit_stage.price_b = self.call_order.strike
        max_profit_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        max_profit_stage.left_expression = '{price_a} <= {old_price} < {new_price} <= {price_b}'
        max_profit_stage.right_expression = '{price_a} <= {new_price} < {old_price} <= {price_b}'

        return max_profit_stage

    def create_max_profit_stage2(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = '{price_a} <= {current_price} <= {price_b}'

        max_profit_stage.price_a = self.put_order.strike
        max_profit_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        max_profit_stage.price_b = self.center_price
        max_profit_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        max_profit_stage.left_expression = '{price_a} <= {new_price} < {old_price} <= {price_b}'
        max_profit_stage.right_expression = '{price_a} <= {old_price} < {new_price} <= {price_b}'

        return max_profit_stage
