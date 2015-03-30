from short_stock import StageShortStock
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageShortStock(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='SELL',
            quantity=-10,
            price=126.03
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_stock = StageShortStock(filled_orders=filled_orders)

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
                'price_a': 126.03,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=126.03, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=120, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=133.33, old_price=133.33, expect='unknown'
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
                'price_a': 126.03,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=124.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=127.84, expect=False)

        self.check_get_status(profit_stage, new_price=124.21, old_price=122.76, expect='decreasing')
        self.check_get_status(profit_stage, new_price=121.63, old_price=122.76, expect='profiting')
        self.check_get_status(profit_stage, new_price=120.8, old_price=120.8, expect='unknown')

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
                'price_a': 126.03,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=131.9, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=120.8, expect=False)

        self.check_get_status(loss_stage, new_price=131.7, old_price=133.85, expect='recovering')
        self.check_get_status(loss_stage, new_price=140, old_price=133.85, expect='losing')
        self.check_get_status(loss_stage, new_price=132.4, old_price=132.4, expect='unknown')

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
