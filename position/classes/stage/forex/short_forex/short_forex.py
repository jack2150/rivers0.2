from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage
from position.models import PositionStage


class StageShortForex(Stage):
    def __init__(self, filled_orders):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.forex_order = filled_orders[0]
        """:type : FilledOrder"""

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [
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
        even_stage.price_a = self.forex_order.price

        return even_stage

    def create_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        profit_stage.stage_expression = self.lt_price
        profit_stage.price_a = self.forex_order.price
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

        loss_stage.stage_expression = self.gt_price

        loss_stage.price_a = self.forex_order.price
        loss_stage.amount_a = 0.0

        loss_stage.left_expression = self.gt_price_lower
        loss_stage.right_expression = self.gt_price_higher

        return loss_stage