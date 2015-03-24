from naked_put import StageNakedPut
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageNakedPut(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='SELL',
            quantity=-1,
            strike=40,
            price=0.74
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put = StageNakedPut(
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
        self.assertEqual(even_stage.stage_expression, '39.26 == {price}')
        self.assertEqual(float(even_stage.price_a), 39.26)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.long_put.create_max_profit_stage()

        print 'current_stage: %s' % max_profit_stage
        print 'stage_name: %s' % max_profit_stage.stage_name
        print 'stage_expression: %s' % max_profit_stage.stage_expression
        print 'price_a: %.2f' % max_profit_stage.price_a
        print 'amount_a: %.2f' % max_profit_stage.amount_a
        print 'left_status: %s' % max_profit_stage.left_status
        print 'left_expression: %s' % max_profit_stage.left_expression
        print 'right_status: %s' % max_profit_stage.right_status
        print 'right_expression: %s' % max_profit_stage.right_expression

        self.assertEqual(type(max_profit_stage), PositionStage)
        self.assertFalse(max_profit_stage.id)
        self.assertEqual(max_profit_stage.stage_name, 'MAX_PROFIT')
        self.assertEqual(max_profit_stage.stage_expression, '40.00 <= {price}')
        self.assertEqual(float(max_profit_stage.price_a), 40.0)
        self.assertEqual(float(max_profit_stage.amount_a), 74.0)
        self.assertEqual(max_profit_stage.left_status, 'vanishing')
        self.assertEqual(max_profit_stage.left_expression, '{price_a} <= {new_price} < {old_price}')
        self.assertEqual(max_profit_stage.right_status, 'guaranteeing')
        self.assertEqual(max_profit_stage.right_expression, '{price_a} <= {old_price} < {new_price}')

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
        self.assertEqual(profit_stage.stage_expression, '39.26 < {price} < 40.00')
        self.assertEqual(float(profit_stage.price_a), 39.26)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(float(profit_stage.price_b), 40.00)
        self.assertEqual(float(profit_stage.amount_b), 74.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {old_price} < {new_price} < {price_b}')

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
        self.assertEqual(loss_stage.stage_expression, '{price} < 39.26')
        self.assertEqual(float(loss_stage.price_a), 39.26)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{new_price} < {old_price} < {price_a}')

    def test_even_in_stage(self):
        """
        Test even in stage method
        """
        even_stage = self.long_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=39.26, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=40, expect=False)

    def test_even_get_status(self):
        """
        Test even get status method
        """
        even_stage = self.long_put.create_even_stage()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=39.26, old_price=39.26, expect='unknown'
        )

    def test_max_profit_in_stage(self):
        """
        Test max profit in stage method
        """
        max_profit_stage = self.long_put.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_profit_stage, price=41, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=39, expect=False)

    def test_max_profit_get_status(self):
        """
        Test max profit get status method
        """
        max_profit_stage = self.long_put.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_get_status(max_profit_stage, new_price=40.5, old_price=41, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=43.66, old_price=41, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=42, old_price=42, expect='unknown')

    def test_profit_in_stage(self):
        """
        Test profit in stage method
        """
        profit_stage = self.long_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=39.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=38.5, expect=False)

    def test_profit_get_status(self):
        """
        Test profit get status method
        """
        profit_stage = self.long_put.create_profit_stage()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=39.3, old_price=39.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=39.6, old_price=39.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=39.5, old_price=39.5, expect='unknown')

    def test_loss_in_stage(self):
        """
        Test loss in stage method
        """
        loss_stage = self.long_put.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=41, expect=False)
        self.check_in_stage(stage_cls=loss_stage, price=39, expect=True)

    def test_loss_get_status(self):
        """
        Test loss get status method
        """
        loss_stage = self.long_put.create_loss_stage()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=38.9, old_price=37.2, expect='recovering')
        self.check_get_status(loss_stage, new_price=36.8, old_price=37.2, expect='losing')
        self.check_get_status(loss_stage, new_price=38, old_price=38, expect='unknown')

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
