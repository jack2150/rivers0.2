from naked_call import StageNakedCall
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCall(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=66,
            price=2.95
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call = StageNakedCall(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call.create_even_stage()

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
        self.assertEqual(even_stage.stage_expression, '68.95 == {price}')
        self.assertEqual(float(even_stage.price_a), 68.95)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.long_call.create_max_profit_stage()

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
        self.assertEqual(max_profit_stage.stage_expression, '{price} <= 66.00')
        self.assertEqual(float(max_profit_stage.price_a), 66.00)
        self.assertEqual(float(max_profit_stage.amount_a), 295.0)
        self.assertEqual(max_profit_stage.left_status, 'vanishing')
        self.assertEqual(max_profit_stage.left_expression, '{old_price} < {new_price} <= {price_a}')
        self.assertEqual(max_profit_stage.right_status, 'guaranteeing')
        self.assertEqual(max_profit_stage.right_expression, '{new_price} < {old_price} <= {price_a}')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call.create_profit_stage()

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
        self.assertEqual(profit_stage.stage_expression, '66.00 < {price} < 68.95')
        self.assertEqual(float(profit_stage.price_a), 66.00)
        self.assertEqual(float(profit_stage.amount_a), 295.0)
        self.assertEqual(float(profit_stage.price_b), 68.95)
        self.assertEqual(float(profit_stage.amount_b), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call.create_loss_stage()

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
        self.assertEqual(loss_stage.stage_expression, '68.95 < {price}')
        self.assertEqual(float(loss_stage.price_a), 68.95)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_call.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=68.95, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=69.99, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_call.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=68.95, old_price=68.95, expect='unknown'
        )

    def test_max_profit_in_stage(self):
        """
        Test max profit in stage method
        """
        max_profit_stage = self.long_call.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_profit_stage, price=63.88, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=66.88, expect=False)

    def test_max_profit_get_status(self):
        """
        Test max profit get status method
        """
        max_profit_stage = self.long_call.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_get_status(max_profit_stage, new_price=65, old_price=64, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=64, old_price=65, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=65, old_price=65, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_call.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=67.2, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=69.2, expect=False)

    def test_profit_get_status(self):
        """
        Test even get status method
        """
        profit_stage = self.long_call.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=67.99, old_price=66.3, expect='decreasing')
        self.check_get_status(profit_stage, new_price=66.3, old_price=67.2, expect='profiting')
        self.check_get_status(profit_stage, new_price=67.2, old_price=67.2, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_call.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=69, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=65, expect=False)

    def test_loss_get_status(self):
        """
        Test even get status method
        """
        loss_stage = self.long_call.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=69, old_price=70, expect='recovering')
        self.check_get_status(loss_stage, new_price=69.32, old_price=69, expect='losing')
        self.check_get_status(loss_stage, new_price=69, old_price=69, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_call.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
