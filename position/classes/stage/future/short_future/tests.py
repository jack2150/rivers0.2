from short_future import StageShortFuture
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageShortFuture(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='SELL',
            quantity=-1,
            price=484.25,
            net_price=484.25
        )

        filled_orders = FilledOrder.objects.filter(future=self.future)

        self.long_stock = StageShortFuture(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_stock.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 484.25,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=484.25, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=499, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=422.2, old_price=422.2, expect='unknown'
        )

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_stock.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 484.25,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=460, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=490, expect=False)

        self.check_get_status(profit_stage, new_price=465.5, old_price=450.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=442.5, old_price=450.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=450.5, old_price=450.5, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_stock.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 484.25,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=510.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=460.3, expect=False)

        self.check_get_status(loss_stage, new_price=499.5, old_price=510.5, expect='recovering')
        self.check_get_status(loss_stage, new_price=520.2, old_price=510.5, expect='losing')
        self.check_get_status(loss_stage, new_price=520.2, old_price=520.2, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_stock.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
