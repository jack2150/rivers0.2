from long_stock import StageLongStock
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongStock(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='BUY',
            quantity=10,
            price=374.24
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_stock = StageLongStock(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_stock.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='374.24 == {price}',
            detail={
                'price_a': 374.24,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=374.24, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=375.9, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=374.24, old_price=375.9, expect='unknown'
        )

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_stock.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='374.24 < {price}',
            detail={
                'price_a': 374.24,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=376.11, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=373.9, expect=False)

        self.check_get_status(profit_stage, new_price=375.9, old_price=376.11, expect='decreasing')
        self.check_get_status(profit_stage, new_price=377.85, old_price=376.11, expect='profiting')
        self.check_get_status(profit_stage, new_price=376.11, old_price=376.11, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_stock.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price} < 374.24',
            detail={
                'price_a': 374.24,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'losing',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=366.71, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=375.9, expect=False)

        self.check_get_status(loss_stage, new_price=365.9, old_price=364.44, expect='recovering')
        self.check_get_status(loss_stage, new_price=363.11, old_price=364.44, expect='losing')
        self.check_get_status(loss_stage, new_price=373.22, old_price=373.22, expect='unknown')

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
