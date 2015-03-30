from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage


class StageShortPutBackratio(Stage):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.buy_order = None
        self.sell_order = None
        for filled_order in filled_orders:
            if filled_order.side == 'BUY':
                self.buy_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.side == 'SELL':
                self.sell_order = filled_order
                """:type : FilledOrder"""

        self.contract_right = contract_right

        # set net price
        if self.buy_order.net_price:
            self.net_price = self.buy_order.net_price
        else:
            self.net_price = self.sell_order.net_price

        # max loss amount
        self.max_profit_price = (
            self.sell_order.strike - self.buy_order.strike + self.net_price
        )

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        if self.net_price < 0:
            result = [
                self.create_max_profit_stage2(),
                self.create_profit_stage2(),
                self.create_max_profit_stage1(),
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
            ]
        elif self.net_price > 0:
            result = [
                self.create_max_loss_stage(),
                self.create_loss_stage2(),
                self.create_profit_stage2(),
                self.create_max_profit_stage1(),
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
            ]
        else:
            result = [
                self.create_even_stage2(),
                self.create_profit_stage2(),
                self.create_max_profit_stage1(),
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
            ]

        return result

    def create_even_stage1(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        even_stage.stage_expression = self.e_price
        even_stage.price_a = self.sell_order.strike + self.max_profit_price

        return even_stage

    def create_even_stage2(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        if self.net_price == 0.0:
            even_stage.stage_expression = self.gte_price
        else:
            even_stage.stage_expression = self.e_price

        even_stage.price_a = self.sell_order.strike - self.max_profit_price

        return even_stage

    def create_max_profit_stage1(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = self.e_price

        max_profit_stage.price_a = self.sell_order.strike
        max_profit_stage.amount_a = (
            self.max_profit_price * self.buy_order.quantity * self.contract_right * -1
        )

        max_profit_stage.left_status = ''
        max_profit_stage.right_status = ''

        return max_profit_stage

    def create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.lt_price

        loss_stage.price_a = self.sell_order.strike + self.max_profit_price

        loss_stage.left_expression = self.lt_price_higher
        loss_stage.right_expression = self.lt_price_lower

        return loss_stage

    def create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.ProfitStage()

        loss_stage.stage_expression = self.price_range

        loss_stage.price_a = self.sell_order.strike + self.max_profit_price
        loss_stage.amount_a = 0.0
        loss_stage.price_b = self.sell_order.strike
        loss_stage.amount_b = (
            self.max_profit_price * self.buy_order.quantity * self.contract_right * -1
        )

        loss_stage.left_expression = self.price_range_lower
        loss_stage.right_expression = self.price_range_higher

        return loss_stage

    def create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.ProfitStage()

        if self.net_price < 0:
            loss_price = self.buy_order.strike
            loss_amount = (
                self.net_price * self.buy_order.quantity * self.contract_right * -1
            )
        else:
            loss_price = self.sell_order.strike - self.max_profit_price
            loss_amount = 0.0

        loss_stage.stage_expression = self.price_range

        loss_stage.price_a = self.sell_order.strike
        loss_stage.amount_a = (
            self.max_profit_price * self.buy_order.quantity * self.contract_right * -1
        )
        loss_stage.price_b = loss_price
        loss_stage.amount_b = loss_amount

        loss_stage.left_expression = self.price_range_higher
        loss_stage.right_expression = self.price_range_lower

        return loss_stage

    def create_max_profit_stage2(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        max_profit_stage.stage_expression = self.gte_price

        max_profit_stage.price_a = self.buy_order.strike
        max_profit_stage.amount_a = (
            self.net_price * self.contract_right * -1
        )

        max_profit_stage.left_expression = self.gte_price_lower
        max_profit_stage.right_expression = self.gte_price_higher

        return max_profit_stage

    def create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        loss_stage.stage_expression = self.price_range

        loss_stage.price_a = self.sell_order.strike - self.max_profit_price
        loss_stage.amount_a = 0.0
        loss_stage.price_b = self.buy_order.strike
        loss_stage.amount_b = (
            self.net_price * self.contract_right * -1
        )

        loss_stage.left_expression = self.price_range_lower
        loss_stage.right_expression = self.price_range_higher

        return loss_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = self.MaxLossStage()

        max_loss_stage.stage_expression = self.gte_price

        max_loss_stage.price_a = self.buy_order.strike
        max_loss_stage.amount_a = (
            self.net_price * self.contract_right * -1
        )

        max_loss_stage.left_expression = self.gte_price_lower
        max_loss_stage.right_expression = self.gte_price_higher

        return max_loss_stage
