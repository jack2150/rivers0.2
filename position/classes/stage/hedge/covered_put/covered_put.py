from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage
from position.models import PositionStage


class StageCoveredPut(Stage):
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
            self.create_loss_stage(),
            self.create_even_stage(),
            self.create_profit_stage(),
            self.create_max_profit_stage()
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        even_stage.stage_expression = self.e_price
        even_stage.price_a = self.option_order.net_price

        return even_stage

    def create_max_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = self.lte_price

        max_profit_stage.price_a = self.option_order.strike
        max_profit_stage.amount_a = (
            (self.option_order.net_price - self.option_order.strike)
            * self.stock_order.quantity * -1
        )

        max_profit_stage.left_expression = self.lte_price_higher
        max_profit_stage.right_expression = self.lte_price_lower

        return max_profit_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        profit_stage.stage_expression = self.price_range

        profit_stage.price_a = self.option_order.strike
        profit_stage.amount_a = (
            (self.option_order.net_price - self.option_order.strike)
            * self.stock_order.quantity * -1
        )
        profit_stage.price_b = self.option_order.net_price
        profit_stage.amount_b = 0.0

        profit_stage.left_expression = self.price_range_higher
        profit_stage.right_expression = self.price_range_lower

        return profit_stage

    def create_loss_stage(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.gt_price

        loss_stage.price_a = self.option_order.net_price
        loss_stage.amount_a = 0.0

        loss_stage.left_expression = self.gt_price_lower
        loss_stage.right_expression = self.gt_price_higher

        return loss_stage
