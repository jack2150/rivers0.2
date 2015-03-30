from position.classes.stage.tests import TestUnitSetUpStage
from long_strangle import StageLongStrangle
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCallVertical(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 85, 'price': 1.18, 'net_price': 2.55},
            'buy_put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                        'strike': 80, 'price': 1.37, 'net_price': 0.0},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.long_call_vertical = StageLongStrangle(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_vertical.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 87.55,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=87.55, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=87, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=87.55, old_price=87.55, expect='unknown'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_vertical.create_even_stage2()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 77.45,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=77.45, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=77.5, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=77.45, old_price=77.45, expect='unknown'
        )