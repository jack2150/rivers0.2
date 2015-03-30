from django.db.models.query import QuerySet
from position.classes.stage.stage import Stage


class StageLongCombo(Stage):
    def __init__(self, filled_orders, contract_right=100):
        """
        :param filled_orders: QuerySet
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.call_order = None
        self.put_order = None
        # All order are call because of call vertical
        for filled_order in filled_orders:
            if filled_order.contract == 'CALL':
                self.call_order = filled_order
                """:type : FilledOrder"""
            elif filled_order.contract == 'PUT':
                self.put_order = filled_order
                """:type : FilledOrder"""

        self.contract_right = contract_right

        # set net price
        if self.call_order.net_price:
            self.net_price = self.call_order.net_price
        else:
            self.net_price = self.put_order.net_price

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        if self.net_price < 0:
            result = [
                self.create_profit_stage1(),
                self.create_max_profit_stage(),
                self.create_profit_stage2(),
                self.create_even_stage(),
                self.create_loss_stage2()
            ]
        elif self.net_price > 0:
            result = [
                self.create_profit_stage1(),
                self.create_loss_stage1(),
                self.create_even_stage(),
                self.create_max_loss_stage(),
                self.create_loss_stage2()
            ]
        else:
            result = [
                self.create_profit_stage1(),
                self.create_even_stage(),
                self.create_loss_stage2()
            ]

        return result

    def create_even_stage(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = self.EvenStage()

        if self.net_price < 0:
            even_stage.stage_expression = self.e_price
            even_stage.price_a = self.put_order.strike + self.net_price
        elif self.net_price > 0:
            even_stage.stage_expression = self.e_price
            even_stage.price_a = self.call_order.strike + self.net_price
        else:
            even_stage.stage_expression = self.e_price_range
            even_stage.price_a = self.put_order.strike
            even_stage.price_b = self.call_order.strike

            even_stage.left_status = 'losing'
            even_stage.left_expression = self.e_price_range_lower
            even_stage.right_status = 'profiting'
            even_stage.right_expression = self.e_price_range_higher

        return even_stage

    def create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = self.MaxProfitStage()

        # only when net price < 0
        max_profit_stage.stage_expression = self.e_price_range
        max_profit_stage.price_a = self.put_order.strike
        max_profit_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        max_profit_stage.price_b = self.call_order.strike
        max_profit_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        max_profit_stage.left_expression = self.e_price_range_lower
        max_profit_stage.right_expression = self.e_price_range_higher

        return max_profit_stage

    def create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = self.MaxLossStage()

        # only when net price > 0
        max_loss_stage.stage_expression = self.e_price_range
        max_loss_stage.price_a = self.put_order.strike
        max_loss_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        max_loss_stage.price_b = self.call_order.strike
        max_loss_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        max_loss_stage.left_expression = self.e_price_range_higher
        max_loss_stage.right_expression = self.e_price_range_lower

        return max_loss_stage

    def create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        if self.net_price <= 0:
            profit_stage.stage_expression = self.gt_price
            profit_stage.price_a = self.call_order.strike
            profit_stage.amount_a = (
                self.net_price * self.call_order.quantity * self.contract_right * -1
            )
        else:
            profit_stage.stage_expression = self.gt_price
            profit_stage.price_a = self.call_order.strike + self.net_price
            profit_stage.amount_a = 0.0

        profit_stage.left_expression = self.gt_price_lower
        profit_stage.right_expression = self.gt_price_higher

        return profit_stage

    def create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = self.ProfitStage()

        # only for net price < 0
        profit_stage.stage_expression = self.price_range
        profit_stage.price_a = self.put_order.strike + self.net_price
        profit_stage.amount_a = 0.0
        profit_stage.price_b = self.put_order.strike
        profit_stage.amount_b = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )

        profit_stage.left_expression = self.price_range_lower
        profit_stage.right_expression = self.price_range_higher

        return profit_stage

    def create_loss_stage1(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        # for net price > 0 only
        loss_stage.stage_expression = self.price_range
        loss_stage.price_a = self.call_order.strike
        loss_stage.amount_a = (
            self.net_price * self.call_order.quantity * self.contract_right * -1
        )
        loss_stage.price_b = self.call_order.strike + self.net_price
        loss_stage.amount_b = 0.0

        loss_stage.left_expression = self.price_range_higher
        loss_stage.right_expression = self.price_range_lower

        return loss_stage

    def create_loss_stage2(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        loss_stage = self.LossStage()

        # for net price <= 0 only
        if self.net_price < 0:
            loss_stage.stage_expression = self.lt_price

            loss_stage.price_a = self.put_order.strike + self.net_price
            loss_stage.amount_a = 0.0

            loss_stage.left_expression = self.lt_price_higher
            loss_stage.right_expression = self.lt_price_lower
        elif self.net_price >= 0:
            loss_stage.stage_expression = self.lt_price

            loss_stage.price_a = self.put_order.strike
            loss_stage.amount_a = (
                self.net_price * self.call_order.quantity * self.contract_right * -1
            )

            loss_stage.left_expression = self.lt_price_higher
            loss_stage.right_expression = self.lt_price_lower

        return loss_stage