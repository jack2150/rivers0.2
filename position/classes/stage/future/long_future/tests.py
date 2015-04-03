from long_future import StageLongFuture
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongFuture(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='BUY',
            quantity=1,
            price=480.00,
            net_price=480.00
        )

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.long_future = StageLongFuture(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_future.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 480.00,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=480.0, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=490.0, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=433.0, old_price=433.0, expect='UNKNOWN'
        )

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_future.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 480.00,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=499.9, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=466.6, expect=False)

        self.check_get_status(profit_stage, new_price=505, old_price=510, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=520, old_price=510, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=510, old_price=510, expect='UNKNOWN')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_future.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 480.00,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'LOSING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=477.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=493.7, expect=False)

        self.check_get_status(loss_stage, new_price=472.5, old_price=466.6, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=453.8, old_price=466.6, expect='LOSING')
        self.check_get_status(loss_stage, new_price=466.6, old_price=466.6, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_future.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
