from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage


class StageLongPutVertical(Stage):
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
            self.create_max_loss_stage(),
            self.create_loss_stage(),
            self.create_even_stage(),
            self.create_profit_stage(),
            self.create_max_profit_stage(),
        ]

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        even_stage.price_a = self.buy_order.strike - self.buy_order.price + self.sell_order.price
        even_stage.stage_expression = self.e_price

        return even_stage

    def create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = self.lte_price

        max_profit_stage.price_a = self.sell_order.strike
        max_profit_stage.amount_a = (
            (self.buy_order.strike - self.sell_order.strike
             - self.buy_order.price + self.sell_order.price)
            * self.contract_right * self.buy_order.quantity
        )

        max_profit_stage.left_expression = self.lte_price_higher
        max_profit_stage.right_expression = self.lte_price_lower

        return max_profit_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = self.MaxLossStage()

        max_loss_stage.stage_expression = self.gte_price

        max_loss_stage.price_a = self.buy_order.strike
        max_loss_stage.amount_a = (
            (self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
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

        profit_stage.stage_expression = self.price_range

        profit_stage.price_a = self.sell_order.strike
        profit_stage.amount_a = (
            (self.buy_order.strike - self.sell_order.strike
             - self.buy_order.price + self.sell_order.price)
            * self.contract_right * self.buy_order.quantity
        )
        profit_stage.price_b = self.buy_order.strike - self.buy_order.price + self.sell_order.price
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

        loss_stage.stage_expression = self.price_range

        loss_stage.price_a = self.buy_order.strike - self.buy_order.price + self.sell_order.price
        loss_stage.amount_a = 0.0
        loss_stage.price_b = self.buy_order.strike
        loss_stage.amount_b = (
            (self.buy_order.price - self.sell_order.price)
            * self.contract_right * self.sell_order.quantity
        )

        loss_stage.left_expression = self.price_range_lower
        loss_stage.right_expression = self.price_range_higher

        return loss_stage
