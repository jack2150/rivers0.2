from covered_call import StageCoveredCall
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageCoveredCall(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'BUY', 'quantity': +100,
                      'strike': 0, 'price': 85.5, 'net_price': 0.0},
            'option': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                       'strike': 85, 'price': 2.2, 'net_price': 83.3},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.covered_call = StageCoveredCall(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.covered_call.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 83.30,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=83.3, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=82.1, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=83.3, old_price=83.3, expect='UNKNOWN'
        )

    def test_create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.covered_call.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 85.0,
                'amount_a': 170.00,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'VANISHING',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'GUARANTEEING',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=86.6, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=84.3, expect=False)

        self.check_get_status(max_profit_stage, new_price=86.55, old_price=86.6, expect='VANISHING')
        self.check_get_status(max_profit_stage, new_price=87.8, old_price=86.6, expect='GUARANTEEING')
        self.check_get_status(max_profit_stage, new_price=86.6, old_price=86.6, expect='UNKNOWN')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.covered_call.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 83.30,
                'amount_a': 0.0,
                'price_b': 85.0,
                'amount_b': 170.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=83.8, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=86.7, expect=False)

        self.check_get_status(profit_stage, new_price=83.8, old_price=84.5, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=84.8, old_price=84.5, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=84.5, old_price=84.5, expect='UNKNOWN')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.covered_call.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 83.3,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'LOSING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=81.55, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=86.77, expect=False)

        self.check_get_status(loss_stage, new_price=81.74, old_price=80.55, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=80.55, old_price=81, expect='LOSING')
        self.check_get_status(loss_stage, new_price=82.56, old_price=82.56, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.covered_call.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
