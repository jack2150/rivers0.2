from django.db.models.query import QuerySet
from position.models import PositionStage


class StageLongCallBackratio(object):
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

        # max loss amount
        self.max_loss_price = (
            self.buy_order.strike - self.sell_order.strike + self.buy_order.net_price
        )

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        if self.buy_order.net_price < 0:
            result = [
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
                self.create_max_loss_stage1(),
                self.create_loss_stage2(),
                self.create_even_stage2(),
                self.create_profit_stage2(),
                self.create_max_profit_stage()
            ]
        elif self.buy_order.net_price > 0:
            result = [
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
                self.create_max_loss_stage1(),
                self.create_loss_stage2(),
                self.create_max_loss_stage2(),
            ]
        else:
            result = [
                self.create_profit_stage1(),
                self.create_even_stage1(),
                self.create_loss_stage1(),
                self.create_max_loss_stage1(),
                self.create_loss_stage2(),
                self.create_even_stage2()
            ]

        return result

    def create_even_stage1(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = '%.2f == {price}' % (
            float(self.buy_order.strike + self.max_loss_price)
        )

        even_stage.price_a = self.buy_order.strike + self.max_loss_price
        even_stage.amount_a = 0.0

        return even_stage

    def create_even_stage2(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        condition = '=='
        if self.buy_order.net_price == 0.0:
            condition = '<='

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = '%.2f %s {price}' % (
            float(self.buy_order.strike - self.max_loss_price),
            condition
        )

        even_stage.price_a = self.buy_order.strike - self.max_loss_price
        even_stage.amount_a = 0.0

        return even_stage

    def create_max_loss_stage1(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = PositionStage()

        max_loss_stage.stage_name = 'MAX_LOSS'
        max_loss_stage.stage_expression = '%.2f == {price}' % (
            float(self.buy_order.strike)
        )

        max_loss_stage.price_a = self.buy_order.strike
        max_loss_stage.amount_a = (
            self.max_loss_price * self.sell_order.quantity * self.contract_right
        )

        return max_loss_stage

    def create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.buy_order.strike),
            float(self.buy_order.strike + self.max_loss_price)
        )

        loss_stage.price_a = self.buy_order.strike
        loss_stage.amount_a = (
            self.max_loss_price * self.sell_order.quantity * self.contract_right
        )
        loss_stage.price_b = self.buy_order.strike + self.max_loss_price
        loss_stage.amount_b = 0.0

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{price_a} < {old_price} < {new_price} < {price_b}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{price_a} < {new_price} < {old_price} < {price_b}'

        return loss_stage

    def create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = '%.2f < {price}' % (
            float(self.buy_order.strike + self.max_loss_price),
        )

        profit_stage.price_a = self.buy_order.strike + self.max_loss_price
        profit_stage.amount_a = 0.0

        profit_stage.left_status = 'decreasing'
        profit_stage.left_expression = '{price_a} < {new_price} < {old_price}'
        profit_stage.right_status = 'profiting'
        profit_stage.right_expression = '{price_a} < {old_price} < {new_price}'

        return profit_stage

    def create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        :return: PositionStage
        """
        loss_stage = PositionStage()

        if self.buy_order.net_price < 0:
            loss_price = self.buy_order.strike - self.max_loss_price
            loss_amount = 0.0
        else:
            loss_price = self.sell_order.strike
            loss_amount = (
                self.buy_order.net_price * self.sell_order.quantity * self.contract_right
            )

        loss_stage.stage_name = 'LOSS'
        loss_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(loss_price),
            float(self.buy_order.strike),
        )

        loss_stage.price_a = loss_price
        loss_stage.amount_a = loss_amount
        loss_stage.price_b = self.buy_order.strike
        loss_stage.amount_b = (
            self.max_loss_price * self.sell_order.quantity * self.contract_right
        )

        loss_stage.left_status = 'recovering'
        loss_stage.left_expression = '{price_a} < {new_price} < {old_price} < {price_b}'
        loss_stage.right_status = 'losing'
        loss_stage.right_expression = '{price_a} < {old_price} < {new_price} < {price_b}'

        return loss_stage

    def create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        profit_stage = PositionStage()

        profit_stage.stage_name = 'PROFIT'
        profit_stage.stage_expression = '%.2f < {price} < %.2f' % (
            float(self.sell_order.strike),
            float(self.buy_order.strike - self.max_loss_price)
        )

        profit_stage.price_a = self.sell_order.strike
        profit_stage.amount_a = (
            self.buy_order.net_price * self.contract_right * -1
        )
        profit_stage.price_b = self.buy_order.strike - self.max_loss_price
        profit_stage.amount_b = 0.0

        profit_stage.left_status = 'decreasing'
        profit_stage.left_expression = '{price_a} < {old_price} < {new_price} < {price_b}'
        profit_stage.right_status = 'profiting'
        profit_stage.right_expression = '{price_a} < {new_price} < {old_price} < {price_b}'

        return profit_stage

    def create_max_profit_stage(self):
        """
        Create profit stage using filled orders data
        :return: PositionStage
        """
        max_profit_stage = PositionStage()

        max_profit_stage.stage_name = 'MAX_PROFIT'
        max_profit_stage.stage_expression = '{price} <= %.2f' % (
            float(self.sell_order.strike)
        )

        max_profit_stage.price_a = self.sell_order.strike
        max_profit_stage.amount_a = (
            self.buy_order.net_price * self.contract_right * -1
        )

        max_profit_stage.left_status = 'vanishing'
        max_profit_stage.left_expression = '{old_price} < {new_price} < {price_a}'
        max_profit_stage.right_status = 'guaranteeing'
        max_profit_stage.right_expression = '{new_price} < {old_price} < {price_a}'

        return max_profit_stage

    def create_max_loss_stage2(self):
        """
        Create max loss stage using filled orders data
        :return: PositionStage
        """
        max_loss_stage = PositionStage()

        max_loss_stage.stage_name = 'MAX_LOSS'
        max_loss_stage.stage_expression = '{price} <= %.2f' % (
            float(self.sell_order.strike)
        )

        max_loss_stage.price_a = self.sell_order.strike
        max_loss_stage.amount_a = (
            self.buy_order.net_price * self.contract_right * -1
        )

        max_loss_stage.left_status = 'easing'
        max_loss_stage.left_expression = '{old_price} < {new_price} < {price_a}'
        max_loss_stage.right_status = 'worst'
        max_loss_stage.right_expression = '{new_price} < {old_price} < {price_a}'

        return max_loss_stage