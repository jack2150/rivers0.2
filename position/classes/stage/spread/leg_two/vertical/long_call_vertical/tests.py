from position.classes.stage import TestUnitSetUpStage
from position.classes.stage.spread.leg_two.vertical.long_call_vertical.long_call_vertical \
    import StageLongCallVertical
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCallVertical(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 80, 'price': 3.15, 'net_price': 0.0},
            'sell_call': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                          'strike': 85, 'price': 1.51, 'net_price': 4.66},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.long_call_vertical = StageLongCallVertical(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_vertical.create_even_stage()

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
        self.assertEqual(even_stage.stage_expression, '81.64 == {price}')
        self.assertEqual(float(even_stage.price_a), 81.64)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        max_profit_stage = self.long_call_vertical.create_max_profit_stage()

        print 'profit_stage: %s' % max_profit_stage
        print 'stage_name: %s' % max_profit_stage.stage_name
        print 'stage_expression: %s' % max_profit_stage.stage_expression
        print 'price_a: %s' % max_profit_stage.price_a
        print 'amount_a: %s' % max_profit_stage.amount_a
        print 'left_status: %s' % max_profit_stage.left_status
        print 'left_expression: %s' % max_profit_stage.left_expression
        print 'right_status: %s' % max_profit_stage.right_status
        print 'right_expression: %s' % max_profit_stage.right_expression

        self.assertEqual(type(max_profit_stage), PositionStage)
        self.assertFalse(max_profit_stage.id)
        self.assertEqual(max_profit_stage.stage_name, 'MAX_PROFIT')
        self.assertEqual(max_profit_stage.stage_expression, '85.00 <= {price}')
        self.assertEqual(float(max_profit_stage.price_a), 85.0)
        self.assertEqual(float(max_profit_stage.amount_a), 336.0)
        self.assertEqual(max_profit_stage.left_status, 'vanishing')
        self.assertEqual(max_profit_stage.left_expression, '{price_a} <= {new_price} < {old_price}')
        self.assertEqual(max_profit_stage.right_status, 'guaranteeing')
        self.assertEqual(max_profit_stage.right_expression, '{price_a} <= {old_price} < {new_price}')

    def test_create_max_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        max_loss_stage = self.long_call_vertical.create_max_loss_stage()

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
        self.assertEqual(max_loss_stage.stage_expression, '{price} <= 80.00')
        self.assertEqual(float(max_loss_stage.price_a), 80.0)
        self.assertEqual(float(max_loss_stage.amount_a), 164.0)
        self.assertEqual(max_loss_stage.left_status, 'easing')
        self.assertEqual(max_loss_stage.left_expression, '{old_price} < {new_price} <= {price_a}')
        self.assertEqual(max_loss_stage.right_status, 'worst')
        self.assertEqual(max_loss_stage.right_expression, '{new_price} < {old_price} <= {price_a}')

    def test_create_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        profit_stage = self.long_call_vertical.create_profit_stage()

        print 'profit_stage: %s' % profit_stage
        print 'stage_name: %s' % profit_stage.stage_name
        print 'stage_expression: %s' % profit_stage.stage_expression
        print 'price_a: %s' % profit_stage.price_a
        print 'amount_a: %s' % profit_stage.amount_a
        print 'price_b: %s' % profit_stage.price_b
        print 'amount_b: %s' % profit_stage.amount_b
        print 'left_status: %s' % profit_stage.left_status
        print 'left_expression: %s' % profit_stage.left_expression
        print 'right_status: %s' % profit_stage.right_status
        print 'right_expression: %s' % profit_stage.right_expression

        self.assertEqual(type(profit_stage), PositionStage)
        self.assertFalse(profit_stage.id)
        self.assertEqual(profit_stage.stage_name, 'PROFIT')
        self.assertEqual(profit_stage.stage_expression, '81.64 < {price} < 85.00')
        self.assertEqual(float(profit_stage.price_a), 81.64)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(float(profit_stage.price_b), 85.0)
        self.assertEqual(float(profit_stage.amount_b), 336.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression,
                         '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression,
                         '{price_a} < {old_price} < {new_price} < {price_b}')

    def test_create_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        loss_stage = self.long_call_vertical.create_loss_stage()

        print 'profit_stage: %s' % loss_stage
        print 'stage_name: %s' % loss_stage.stage_name
        print 'stage_expression: %s' % loss_stage.stage_expression
        print 'price_a: %s' % loss_stage.price_a
        print 'amount_a: %s' % loss_stage.amount_a
        print 'price_b: %s' % loss_stage.price_b
        print 'amount_b: %s' % loss_stage.amount_b
        print 'left_status: %s' % loss_stage.left_status
        print 'left_expression: %s' % loss_stage.left_expression
        print 'right_status: %s' % loss_stage.right_status
        print 'right_expression: %s' % loss_stage.right_expression

        self.assertEqual(type(loss_stage), PositionStage)
        self.assertFalse(loss_stage.id)
        self.assertEqual(loss_stage.stage_name, 'LOSS')
        self.assertEqual(loss_stage.stage_expression, '80.00 < {price} < 81.64')
        self.assertEqual(float(loss_stage.price_a), 80.0)
        self.assertEqual(float(loss_stage.amount_a), -164.0)
        self.assertEqual(float(loss_stage.price_b), 81.64)
        self.assertEqual(float(loss_stage.amount_b), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression,
                         '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression,
                         '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_call_vertical.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=81.64, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=79.99, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_call_vertical.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=83.33, old_price=82.22, expect='unknown'
        )

    def test_max_profit_in_stage(self):
        """
        Test even in stage method
        """
        max_profit_stage = self.long_call_vertical.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_profit_stage, price=86.66, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=83.2, expect=False)

    def test_max_profit_get_status(self):
        """
        Test even get status method
        """
        max_profit_stage = self.long_call_vertical.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_get_status(max_profit_stage, new_price=85.32, old_price=86.7, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=86.8, old_price=86.7, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=85.6, old_price=85.6, expect='unknown')

    def test_max_loss_in_stage(self):
        """
        Test even in stage method
        """
        max_loss_stage = self.long_call_vertical.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_loss_stage, price=77.84, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=81, expect=False)

    def test_max_loss_get_status(self):
        """
        Test even get status method
        """
        max_loss_stage = self.long_call_vertical.create_max_loss_stage()

        print max_loss_stage
        print '.' * 60
        self.check_get_status(max_loss_stage, new_price=78.18, old_price=76.96, expect='easing')
        self.check_get_status(max_loss_stage, new_price=78.64, old_price=79.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=79.5, old_price=79.5, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_call_vertical.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=84.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=81.33, expect=False)

    def test_profit_get_status(self):
        """
        Test even get status method
        """
        profit_stage = self.long_call_vertical.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=83.5, old_price=84.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=83.5, old_price=82.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=82.64, old_price=82.64, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_call_vertical.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=81.38, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=79.6, expect=False)

    def test_loss_get_status(self):
        """
        Test even get status method
        """
        loss_stage = self.long_call_vertical.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=81.13, old_price=80.22, expect='recovering')
        self.check_get_status(loss_stage, new_price=80.75, old_price=81.13, expect='losing')
        self.check_get_status(loss_stage, new_price=80.75, old_price=80.75, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_call_vertical.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)




























