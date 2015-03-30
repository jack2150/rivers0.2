from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage


class StageLongPut(Stage):
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
        even_stage = self.EvenStage()

        even_stage.stage_expression = self.e_price
        even_stage.price_a = self.put_order.strike - self.put_order.price

        return even_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = self.MaxLossStage()

        max_loss_stage.stage_expression = self.gte_price

        max_loss_stage.price_a = self.put_order.strike
        max_loss_stage.amount_a = (
            self.put_order.price * self.put_order.quantity * self.contract_right * -1
        )

        max_loss_stage.left_expression = self.gte_price_lower
        max_loss_stage.right_expression = self.gte_price_higher

        return max_loss_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        profit_stage.stage_expression = self.lt_price

        profit_stage.price_a = self.put_order.strike - self.put_order.price
        profit_stage.amount_a = 0.0

        profit_stage.left_expression = self.lt_price_higher
        profit_stage.right_expression = self.lt_price_lower

        return profit_stage

    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.price_range

        loss_stage.price_a = self.put_order.strike - self.put_order.price
        loss_stage.amount_a = 0.0
        loss_stage.price_b = self.put_order.strike
        loss_stage.amount_b = (
            self.put_order.price * self.put_order.quantity * self.contract_right * -1
        )

        loss_stage.left_expression = self.price_range_lower
        loss_stage.right_expression = self.price_range_higher

        return loss_stage
