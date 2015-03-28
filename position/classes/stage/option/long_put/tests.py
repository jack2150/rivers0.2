from long_put import StageLongPut
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongPut(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='BUY',
            quantity=1,
            strike=125,
            price=3.93
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put = StageLongPut(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='121.07 == {price}',
            detail={
                'price_a': 121.07,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=121.07, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=123, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=121.07, old_price=121.07, expect='unknown'
        )

    def test_create_max_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_put.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='125.00 <= {price}',
            detail={
                'price_a': 125.00,
                'amount_a': -393.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'worst',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=126, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=124.6, expect=False)

        self.check_get_status(max_loss_stage, new_price=126, old_price=127, expect='easing')
        self.check_get_status(max_loss_stage, new_price=128, old_price=127, expect='worst')
        self.check_get_status(max_loss_stage, new_price=126, old_price=126, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price} < 121.07',
            detail={
                'price_a': 121.07,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=120.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=123.5, expect=False)

        self.check_get_status(profit_stage, new_price=119.5, old_price=118.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=115, old_price=118, expect='profiting')
        self.check_get_status(profit_stage, new_price=119.5, old_price=119.5, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='121.07 < {price} < 125.00',
            detail={
                'price_a': 121.07,
                'amount_a': 0.0,
                'price_b': 125.0,
                'amount_b': -393.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=124.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=126.7, expect=False)

        self.check_get_status(loss_stage, new_price=122.5, old_price=123, expect='recovering')
        self.check_get_status(loss_stage, new_price=123.5, old_price=123, expect='losing')
        self.check_get_status(loss_stage, new_price=123, old_price=123, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_put.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
