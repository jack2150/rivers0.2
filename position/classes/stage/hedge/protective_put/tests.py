from protective_put import StageProtectivePut
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageProtectivePut(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'BUY', 'quantity': 100,
                      'strike': 0, 'price': 55.95, 'net_price': 0.0},
            'option': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1,
                       'strike': 55, 'price': 1.04, 'net_price': 56.99},
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

        self.protective_put = StageProtectivePut(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.protective_put.create_even_stage()

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
        self.assertEqual(even_stage.stage_expression, '56.99 == {price}')
        self.assertEqual(float(even_stage.price_a), 56.99)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.protective_put.create_max_loss_stage()

        print 'profit_stage: %s' % max_loss_stage
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
        self.assertEqual(max_loss_stage.stage_expression, '{price} <= 55.00')
        self.assertEqual(float(max_loss_stage.price_a), 55.0)
        self.assertEqual(float(max_loss_stage.amount_a), -199.0)
        self.assertEqual(max_loss_stage.left_status, 'easing')
        self.assertEqual(max_loss_stage.left_expression, '{old_price} < {new_price} <= {price_a}')
        self.assertEqual(max_loss_stage.right_status, 'worst')
        self.assertEqual(max_loss_stage.right_expression, '{new_price} < {old_price} <= {price_a}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.protective_put.create_loss_stage()

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
        self.assertEqual(loss_stage.stage_expression, '55.00 < {price} < 56.99')
        self.assertEqual(float(loss_stage.price_a), 55.0)
        self.assertEqual(float(loss_stage.amount_a), -199.0)
        self.assertEqual(float(loss_stage.price_b), 56.99)
        self.assertEqual(float(loss_stage.amount_b), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.protective_put.create_profit_stage()

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
        self.assertEqual(profit_stage.stage_expression, '56.99 < {price}')
        self.assertEqual(float(profit_stage.price_a), 56.99)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.protective_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=56.99, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=58.1, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.protective_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=57.2, old_price=57.2, expect='unknown'
        )

    def test_max_loss_in_stage(self):
        """
        Test max loss in stage method
        """
        max_loss_stage = self.protective_put.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_loss_stage, price=52.3, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=56.99, expect=False)

    def test_max_loss_get_status(self):
        """
        Test max loss get status method
        """
        max_loss_stage = self.protective_put.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_get_status(max_loss_stage, new_price=54.6, old_price=53.8, expect='easing')
        self.check_get_status(max_loss_stage, new_price=53.8, old_price=54.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=52.3, old_price=52.3, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test loss in stage method
        """
        loss_stage = self.protective_put.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=56.2, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=57.2, expect=False)

    def test_loss_get_status(self):
        """
        Test loss get status method
        """
        loss_stage = self.protective_put.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=56.5, old_price=56, expect='recovering')
        self.check_get_status(loss_stage, new_price=55.5, old_price=56, expect='losing')
        self.check_get_status(loss_stage, new_price=55.99, old_price=55.99, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test profit in stage method
        """
        profit_stage = self.protective_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=57.2, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=56.2, expect=False)

    def test_profit_get_status(self):
        """
        Test profit get status method
        """
        profit_stage = self.protective_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=57.22, old_price=58.3, expect='decreasing')
        self.check_get_status(profit_stage, new_price=59.3, old_price=58.3, expect='profiting')
        self.check_get_status(profit_stage, new_price=57.3, old_price=57.3, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.protective_put.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
