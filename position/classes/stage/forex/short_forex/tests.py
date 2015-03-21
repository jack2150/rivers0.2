from short_forex import StageShortForex
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageShortForex(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.forex_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='SELL',
            quantity=-10000,
            price=120.1295
        )

        filled_orders = FilledOrder.objects.filter(forex=self.forex)

        self.long_stock = StageShortForex(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_stock.create_even_stage()

        print 'profit_stage: %s' % even_stage
        print 'stage_name: %s' % even_stage.stage_name
        print 'stage_expression: %s' % even_stage.stage_expression
        print 'price_a: %s' % even_stage.price_a
        print 'amount_a: %s' % even_stage.amount_a
        print 'left_status: %s' % even_stage.left_status
        print 'left_expression: %s' % even_stage.left_expression
        print 'right_status: %s' % even_stage.right_status
        print 'right_expression: %s' % even_stage.right_expression

        self.assertEqual(type(even_stage), PositionStage)
        self.assertFalse(even_stage.id)
        self.assertEqual(even_stage.stage_name, 'EVEN')
        self.assertEqual(even_stage.stage_expression, '120.1295 == {price}')
        self.assertEqual(float(even_stage.price_a), 120.1295)
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

        print 'profit_stage: %s' % profit_stage
        print 'stage_name: %s' % profit_stage.stage_name
        print 'stage_expression: %s' % profit_stage.stage_expression
        print 'price_a: %s' % profit_stage.price_a
        print 'amount_a: %s' % profit_stage.amount_a
        print 'left_status: %s' % profit_stage.left_status
        print 'left_expression: %s' % profit_stage.left_expression
        print 'right_status: %s' % profit_stage.right_status
        print 'right_expression: %s' % profit_stage.right_expression

        self.assertEqual(type(profit_stage), PositionStage)
        self.assertFalse(profit_stage.id)
        self.assertEqual(profit_stage.stage_name, 'PROFIT')
        self.assertEqual(profit_stage.stage_expression, '{price} < 120.1295')
        self.assertEqual(float(profit_stage.price_a), 120.1295)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{new_price} < {old_price} < {price_a}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_stock.create_loss_stage()

        print 'profit_stage: %s' % loss_stage
        print 'stage_name: %s' % loss_stage.stage_name
        print 'stage_expression: %s' % loss_stage.stage_expression
        print 'price_a: %s' % loss_stage.price_a
        print 'amount_a: %s' % loss_stage.amount_a
        print 'left_status: %s' % loss_stage.left_status
        print 'left_expression: %s' % loss_stage.left_expression
        print 'right_status: %s' % loss_stage.right_status
        print 'right_expression: %s' % loss_stage.right_expression

        self.assertEqual(type(loss_stage), PositionStage)
        self.assertFalse(loss_stage.id)
        self.assertEqual(loss_stage.stage_name, 'LOSS')
        self.assertEqual(loss_stage.stage_expression, '120.1295 < {price}')
        self.assertEqual(float(loss_stage.price_a), 120.1295)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_stock.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=120.1295, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=121.1295, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_stock.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=120.1295, old_price=120.1295, expect='unknown'
        )

    def test_profit_in_stage(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_stock.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=116.1295, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=122.1295, expect=False)

    def test_profit_get_status(self):
        """
        Test even get status method
        """
        profit_stage = self.long_stock.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=118.1295, old_price=116.1295, expect='decreasing')
        self.check_get_status(profit_stage, new_price=116.1295, old_price=118.1295, expect='profiting')
        self.check_get_status(profit_stage, new_price=116.1295, old_price=116.1295, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_stock.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=122.1295, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=116.1295, expect=False)

    def test_loss_get_status(self):
        """
        Test even get status method
        """
        loss_stage = self.long_stock.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=122.1295, old_price=123.1295, expect='recovering')
        self.check_get_status(loss_stage, new_price=124.1295, old_price=123.1295, expect='losing')
        self.check_get_status(loss_stage, new_price=123.1295, old_price=123.1295, expect='unknown')

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
