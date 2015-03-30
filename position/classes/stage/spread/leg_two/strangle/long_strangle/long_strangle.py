from django.db.models.query import QuerySet
from position.classes.stage.expression import Expression
from position.models import PositionStage


class StageLongStrangle(Expression):
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

        self.contract_right = contract_right

    def create_stages(self):
        """
        Create stage using filled_orders
        :return: list of PositionStage
        """
        return [

        ]

    def create_even_stage1(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = self.equal_as_price

        even_stage.price_a = self.call_order.strike + self.net_price

        return even_stage

    def create_even_stage2(self):
        """
        Create even stage using filled orders data
        :return: PositionStage
        """
        even_stage = PositionStage()

        even_stage.stage_name = 'EVEN'
        even_stage.stage_expression = self.equal_as_price

        even_stage.price_a = self.put_order.strike - self.net_price

        return even_stage