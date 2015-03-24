from long_put import StageLongPut
from position.classes.stage import TestUnitSetUpStage
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
        self.assertEqual(even_stage.stage_expression, '121.07 == {price}')
        self.assertEqual(float(even_stage.price_a), 121.07)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        max_loss = self.long_put.create_max_loss_stage()

        print 'current_stage: %s' % max_loss
        print 'stage_name: %s' % max_loss.stage_name
        print 'stage_expression: %s' % max_loss.stage_expression
        print 'price_a: %.2f' % max_loss.price_a
        print 'amount_a: %.2f' % max_loss.amount_a
        print 'left_status: %s' % max_loss.left_status
        print 'left_expression: %s' % max_loss.left_expression
        print 'right_status: %s' % max_loss.right_status
        print 'right_expression: %s' % max_loss.right_expression

        self.assertEqual(type(max_loss), PositionStage)
        self.assertFalse(max_loss.id)
        self.assertEqual(max_loss.stage_name, 'MAX_LOSS')
        self.assertEqual(max_loss.stage_expression, '125.00 <= {price}')
        self.assertEqual(float(max_loss.price_a), 125.00)
        self.assertEqual(float(max_loss.amount_a), -393.0)
        self.assertEqual(max_loss.left_status, 'easing')
        self.assertEqual(max_loss.left_expression, '{price_a} <= {new_price} < {old_price}')
        self.assertEqual(max_loss.right_status, 'worst')
        self.assertEqual(max_loss.right_expression, '{price_a} <= {old_price} < {new_price}')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put.create_profit_stage()

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
        self.assertEqual(profit_stage.stage_expression, '{price} < 121.07')
        self.assertEqual(float(profit_stage.price_a), 121.07)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{new_price} < {old_price} < {price_a}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put.create_loss_stage()

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
        self.assertEqual(loss_stage.stage_expression, '121.07 < {price} < 125.00')
        self.assertEqual(float(loss_stage.price_a), 121.07)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(float(loss_stage.price_b), 125.0)
        self.assertEqual(float(loss_stage.amount_b), -393.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {old_price} < {new_price} < {price_b}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=121.07, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=123, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=121.07, old_price=121.07, expect='unknown'
        )

    def test_max_loss_in_stage(self):
        """
        Test max loss in stage method
        """
        max_loss_stage = self.long_put.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_loss_stage, price=126, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=124.6, expect=False)

    def test_max_loss_get_status(self):
        """
        Test even get status method
        """
        max_loss_stage = self.long_put.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_get_status(max_loss_stage, new_price=126, old_price=127, expect='easing')
        self.check_get_status(max_loss_stage, new_price=128, old_price=127, expect='worst')
        self.check_get_status(max_loss_stage, new_price=126, old_price=126, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=120.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=123.5, expect=False)

    def test_profit_get_status(self):
        """
        Test even get status method
        """
        profit_stage = self.long_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=119.5, old_price=118.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=115, old_price=118, expect='profiting')
        self.check_get_status(profit_stage, new_price=119.5, old_price=119.5, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_put.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=124.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=126.7, expect=False)

    def test_loss_get_status(self):
        """
        Test even get status method
        """
        loss_stage = self.long_put.create_loss_stage()

        print loss_stage
        print '.' * 60
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
