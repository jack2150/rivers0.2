from long_stock import StageLongStock
from position.classes.stage import TestUnitSetUpStage
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

        print 'current_stage: %s' % even_stage
        print 'stage_name: %s' % even_stage.stage_name
        print 'stage_expression: %s' % even_stage.stage_expression
        print 'price_a: %.2f' % even_stage.price_a
        print 'amount_a: %.2f' % even_stage.amount_a
        print 'left_status: %s' % even_stage.left_status
        print 'left_expression: %s' % even_stage.left_expression
        print 'right_status: %s' % even_stage.right_status
        print 'right_expression: %s' % even_stage.right_expression

        self.assertEqual(type(even_stage), PositionStage)
        self.assertFalse(even_stage.id)
        self.assertEqual(even_stage.stage_name, 'EVEN')
        self.assertEqual(even_stage.stage_expression, '374.24 == {price}')
        self.assertEqual(float(even_stage.price_a), 374.24)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_stock.create_profit_stage()

        print 'current_stage: %s' % profit_stage
        print 'stage_name: %s' % profit_stage.stage_name
        print 'stage_expression: %s' % profit_stage.stage_expression
        print 'price_a: %.2f' % profit_stage.price_a
        print 'amount_a: %.2f' % profit_stage.amount_a
        print 'left_status: %s' % profit_stage.left_status
        print 'left_expression: %s' % profit_stage.left_expression
        print 'right_status: %s' % profit_stage.right_status
        print 'right_expression: %s' % profit_stage.right_expression

        self.assertEqual(type(profit_stage), PositionStage)
        self.assertFalse(profit_stage.id)
        self.assertEqual(profit_stage.stage_name, 'PROFIT')
        self.assertEqual(profit_stage.stage_expression, '374.24 < {price}')
        self.assertEqual(float(profit_stage.price_a), 374.24)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_stock.create_loss_stage()

        print 'current_stage: %s' % loss_stage
        print 'stage_name: %s' % loss_stage.stage_name
        print 'stage_expression: %s' % loss_stage.stage_expression
        print 'price_a: %.2f' % loss_stage.price_a
        print 'amount_a: %.2f' % loss_stage.amount_a
        print 'left_status: %s' % loss_stage.left_status
        print 'left_expression: %s' % loss_stage.left_expression
        print 'right_status: %s' % loss_stage.right_status
        print 'right_expression: %s' % loss_stage.right_expression

        self.assertEqual(type(loss_stage), PositionStage)
        self.assertFalse(loss_stage.id)
        self.assertEqual(loss_stage.stage_name, 'LOSS')
        self.assertEqual(loss_stage.stage_expression, '{price} < 374.24')
        self.assertEqual(float(loss_stage.price_a), 374.24)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{new_price} < {old_price} < {price_a}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_stock.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=374.24, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=375.9, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_stock.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=374.24, old_price=375.9, expect='unknown'
        )

    def test_profit_in_stage(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_stock.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=376.11, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=373.9, expect=False)

    def test_profit_get_status(self):
        """
        Test even get status method
        """
        profit_stage = self.long_stock.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=375.9, old_price=376.11, expect='decreasing')
        self.check_get_status(profit_stage, new_price=377.85, old_price=376.11, expect='profiting')
        self.check_get_status(profit_stage, new_price=376.11, old_price=376.11, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_stock.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=366.71, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=375.9, expect=False)

    def test_loss_get_status(self):
        """
        Test even get status method
        """
        loss_stage = self.long_stock.create_loss_stage()

        print loss_stage
        print '.' * 60
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
