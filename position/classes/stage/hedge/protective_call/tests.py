from protective_call import StageProtectiveCall
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageProtectiveCall(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'SELL', 'quantity': -100,
                      'strike': 0, 'price': 52.92, 'net_price': 0.0},
            'option': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                       'strike': 55, 'price': 1.31, 'net_price': 51.61},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.protective_call = StageProtectiveCall(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.protective_call.create_even_stage()

        print 'current_stage: %s' % even_stage
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
        self.assertEqual(even_stage.stage_expression, '51.61 == {price}')
        self.assertEqual(float(even_stage.price_a), 51.61)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_loss_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_loss_stage = self.protective_call.create_max_loss_stage()

        print 'current_stage: %s' % max_loss_stage
        print 'stage_name: %s' % max_loss_stage.stage_name
        print 'stage_expression: %s' % max_loss_stage.stage_expression
        print 'price_a: %s' % max_loss_stage.price_a
        print 'amount_a: %s' % max_loss_stage.amount_a
        print 'left_status: %s' % max_loss_stage.left_status
        print 'left_expression: %s' % max_loss_stage.left_expression
        print 'right_status: %s' % max_loss_stage.right_status
        print 'right_expression: %s' % max_loss_stage.right_expression

        self.assertEqual(type(max_loss_stage), PositionStage)
        self.assertFalse(max_loss_stage.id)
        self.assertEqual(max_loss_stage.stage_name, 'MAX_LOSS')
        self.assertEqual(max_loss_stage.stage_expression, '55.00 <= {price}')
        self.assertEqual(float(max_loss_stage.price_a), 55.0)
        self.assertEqual(float(max_loss_stage.amount_a), -339.0)
        self.assertEqual(max_loss_stage.left_status, 'easing')
        self.assertEqual(max_loss_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(max_loss_stage.right_status, 'worst')
        self.assertEqual(max_loss_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.protective_call.create_loss_stage()

        print 'current_stage: %s' % profit_stage
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
        self.assertEqual(profit_stage.stage_name, 'LOSS')
        self.assertEqual(profit_stage.stage_expression, '51.61 < {price} < 55.00')
        self.assertEqual(float(profit_stage.price_a), 51.61)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(float(profit_stage.price_b), 55.00)
        self.assertEqual(float(profit_stage.amount_b), -339.0)
        self.assertEqual(profit_stage.left_status, 'recovering')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(profit_stage.right_status, 'losing')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {old_price} < {new_price} < {price_b}')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.protective_call.create_profit_stage()

        print 'current_stage: %s' % profit_stage
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
        self.assertEqual(profit_stage.stage_expression, '{price} < 51.61')
        self.assertEqual(float(profit_stage.price_a), 51.61)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{new_price} < {old_price} < {price_a}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.protective_call.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=51.61, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=52, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.protective_call.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=51.61, old_price=51.61, expect='unknown'
        )

    def test_max_loss_in_stage(self):
        """
        Test max profit in stage method
        """
        max_loss_stage = self.protective_call.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_loss_stage, price=56.5, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=51.61, expect=False)

    def test_max_loss_get_status(self):
        """
        Test max loss get status method
        """
        max_loss_stage = self.protective_call.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_get_status(max_loss_stage, new_price=55.5, old_price=56.5, expect='easing')
        self.check_get_status(max_loss_stage, new_price=57.5, old_price=56.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=56.5, old_price=56.5, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test profit in stage method
        """
        profit_stage = self.protective_call.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=50.1, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=54.5, expect=False)

    def test_profit_get_status(self):
        """
        Test profit get status method
        """
        profit_stage = self.protective_call.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=47.5, old_price=44.33, expect='decreasing')
        self.check_get_status(profit_stage, new_price=44.33, old_price=47.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=48.5, old_price=48.5, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test loss in stage method
        """
        loss_stage = self.protective_call.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=52.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=49.9, expect=False)

    def test_loss_get_status(self):
        """
        Test loss get status method
        """
        loss_stage = self.protective_call.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=52.65, old_price=53.88, expect='recovering')
        self.check_get_status(loss_stage, new_price=54.96, old_price=53.88, expect='losing')
        self.check_get_status(loss_stage, new_price=53.88, old_price=53.88, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.protective_call.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
