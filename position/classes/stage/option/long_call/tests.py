from long_call import StageLongCall
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
            side='BUY',
            quantity=2,
            strike=58,
            price=0.95
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call = StageLongCall(
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
            expression='58.95 == {price}',
            detail={
                'price_a': 58.95,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=58.95, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=60.1, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=58.95, old_price=58.95, expect='unknown'
        )

    def test_create_max_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_call.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price} <= 58.00',
            detail={
                'price_a': 58.00,
                'amount_a': -190.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'worst',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=55.3, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=58.95, expect=False)

        self.check_get_status(max_loss_stage, new_price=54, old_price=53, expect='easing')
        self.check_get_status(max_loss_stage, new_price=52.5, old_price=53.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=52.2, old_price=52.2, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='58.95 < {price}',
            detail={
                'price_a': 58.95,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=62.54, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=58.95, expect=False)

        self.check_get_status(profit_stage, new_price=61.44, old_price=63.1, expect='decreasing')
        self.check_get_status(profit_stage, new_price=63.9, old_price=61, expect='profiting')
        self.check_get_status(profit_stage, new_price=62.2, old_price=62.2, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='58.00 < {price} < 58.95',
            detail={
                'price_a': 58.00,
                'amount_a': -190.00,
                'price_b': 58.95,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=58.94, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=62.3, expect=False)

        self.check_get_status(loss_stage, new_price=58.5, old_price=58.4, expect='recovering')
        self.check_get_status(loss_stage, new_price=58.5, old_price=58.6, expect='losing')
        self.check_get_status(loss_stage, new_price=58.5, old_price=58.5, expect='unknown')

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
