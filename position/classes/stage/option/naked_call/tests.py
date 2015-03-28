from naked_call import StageNakedCall
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCall(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=66,
            price=2.95
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call = StageNakedCall(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='68.95 == {price}',
            detail={
                'price_a': 68.95,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=68.95, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=69.99, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=68.95, old_price=68.95, expect='unknown'
        )

    def test_create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.long_call.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price} <= 66.00',
            detail={
                'price_a': 66.00,
                'amount_a': 295.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'guaranteeing',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=63.88, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=66.88, expect=False)

        self.check_get_status(max_profit_stage, new_price=65, old_price=64, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=64, old_price=65, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=65, old_price=65, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='66.00 < {price} < 68.95',
            detail={
                'price_a': 66.0,
                'amount_a': 295.0,
                'price_b': 68.95,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=67.2, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=69.2, expect=False)

        self.check_get_status(profit_stage, new_price=67.99, old_price=66.3, expect='decreasing')
        self.check_get_status(profit_stage, new_price=66.3, old_price=67.2, expect='profiting')
        self.check_get_status(profit_stage, new_price=67.2, old_price=67.2, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='68.95 < {price}',
            detail={
                'price_a': 68.95,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=69, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=65, expect=False)

        self.check_get_status(loss_stage, new_price=69, old_price=70, expect='recovering')
        self.check_get_status(loss_stage, new_price=69.32, old_price=69, expect='losing')
        self.check_get_status(loss_stage, new_price=69, old_price=69, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_call.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
