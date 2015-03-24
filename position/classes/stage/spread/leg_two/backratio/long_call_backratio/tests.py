from long_call_backratio import StageLongCallBackratio
from position.classes.stage import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


# todo: need 2 tests
class TestStageLongCallBackratio(TestUnitSetUpStage):
    """
    ,,3/23/15 03:57:38,BACKRATIO,SELL,-1,TO OPEN,SYMBOL,JUN 15,43,CALL,-.58,LMT,DAY,-.58,WORKING
    ,,,,BUY,+2,TO OPEN,MSFT,JUN 15,46,CALL,,,,,
    """
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=43,
            price=1.42,
            net_price=0.0
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='BUY',
            quantity=2,
            strike=46,
            price=.42,
            net_price=-0.58
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call_backratio = StageLongCallBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage1()

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
        self.assertEqual(even_stage.stage_expression, '48.42 == {price}')
        self.assertEqual(float(even_stage.price_a), 48.42)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage2()

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
        self.assertEqual(even_stage.stage_expression, '43.58 == {price}')
        self.assertEqual(float(even_stage.price_a), 43.58)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage1()

        print 'current_stage: %s' % max_loss_stage
        print 'stage_name: %s' % max_loss_stage.stage_name
        print 'stage_expression: %s' % max_loss_stage.stage_expression
        print 'price_a: %.2f' % max_loss_stage.price_a
        print 'amount_a: %.2f' % max_loss_stage.amount_a
        print 'left_status: %s' % max_loss_stage.left_status
        print 'left_expression: %s' % max_loss_stage.left_expression
        print 'right_status: %s' % max_loss_stage.right_status
        print 'right_expression: %s' % max_loss_stage.right_expression

        self.assertEqual(type(max_loss_stage), PositionStage)
        self.assertFalse(max_loss_stage.id)
        self.assertEqual(max_loss_stage.stage_name, 'MAX_LOSS')
        self.assertEqual(max_loss_stage.stage_expression, '46.00 == {price}')
        self.assertEqual(float(max_loss_stage.price_a), 46.0)
        self.assertEqual(float(max_loss_stage.amount_a), -242.0)
        self.assertEqual(max_loss_stage.left_status, '')
        self.assertEqual(max_loss_stage.left_expression, '')
        self.assertEqual(max_loss_stage.right_status, '')
        self.assertEqual(max_loss_stage.right_expression, '')

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

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
        self.assertEqual(profit_stage.stage_expression, '48.42 < {price}')
        self.assertEqual(float(profit_stage.price_a), 48.42)
        self.assertEqual(float(profit_stage.amount_a), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression, '{price_a} < {new_price} < {old_price}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression, '{price_a} < {old_price} < {new_price}')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

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
        self.assertEqual(loss_stage.stage_expression, '46.00 < {price} < 48.42')
        self.assertEqual(float(loss_stage.price_a), 46.0)
        self.assertEqual(float(loss_stage.amount_a), -242.0)
        self.assertEqual(float(loss_stage.price_b), 48.42)
        self.assertEqual(float(loss_stage.amount_b), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage2()

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
        self.assertEqual(loss_stage.stage_expression, '43.58 < {price} < 46.00')
        self.assertEqual(float(loss_stage.price_a), 43.58)
        self.assertEqual(float(loss_stage.amount_a), 0.0)
        self.assertEqual(float(loss_stage.price_b), 46.0)
        self.assertEqual(float(loss_stage.amount_b), -242.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {old_price} < {new_price} < {price_b}')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        print 'current_stage: %s' % profit_stage
        print 'stage_name: %s' % profit_stage.stage_name
        print 'stage_expression: %s' % profit_stage.stage_expression
        print 'price_a: %.2f' % profit_stage.price_a
        print 'amount_a: %.2f' % profit_stage.amount_a
        print 'price_b: %.2f' % profit_stage.price_b
        print 'amount_b: %.2f' % profit_stage.amount_b
        print 'left_status: %s' % profit_stage.left_status
        print 'left_expression: %s' % profit_stage.left_expression
        print 'right_status: %s' % profit_stage.right_status
        print 'right_expression: %s' % profit_stage.right_expression

        self.assertEqual(type(profit_stage), PositionStage)
        self.assertFalse(profit_stage.id)
        self.assertEqual(profit_stage.stage_name, 'PROFIT')
        self.assertEqual(profit_stage.stage_expression, '43.00 < {price} < 43.58')
        self.assertEqual(float(profit_stage.price_a), 43.0)
        self.assertEqual(float(profit_stage.amount_a), 58.0)
        self.assertEqual(float(profit_stage.price_b), 43.58)
        self.assertEqual(float(profit_stage.amount_b), 0.0)
        self.assertEqual(profit_stage.left_status, 'decreasing')
        self.assertEqual(profit_stage.left_expression,
                         '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(profit_stage.right_status, 'profiting')
        self.assertEqual(profit_stage.right_expression,
                         '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_create_max_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage()

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
        self.assertEqual(max_profit_stage.stage_expression, '{price} <= 43.00')
        self.assertEqual(float(max_profit_stage.price_a), 43.0)
        self.assertEqual(float(max_profit_stage.amount_a), 58.0)
        self.assertEqual(max_profit_stage.left_status, 'vanishing')
        self.assertEqual(max_profit_stage.left_expression,
                         '{old_price} < {new_price} < {price_a}')
        self.assertEqual(max_profit_stage.right_status, 'guaranteeing')
        self.assertEqual(max_profit_stage.right_expression,
                         '{new_price} < {old_price} < {price_a}')

    def test_even_in_stage1(self):
        """
        Test even in stage method
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=48.42, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=49, expect=False)

    def test_even_get_status1(self):
        """
        Test even get status method
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=48.42, old_price=48.42, expect='unknown'
        )

    def test_even_in_stage2(self):
        """
        Test even in stage method
        """
        even_stage = self.long_call_backratio.create_even_stage2()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=43.58, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=44, expect=False)

    def test_even_get_status2(self):
        """
        Test even get status method
        """
        even_stage = self.long_call_backratio.create_even_stage2()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=43.58, old_price=43.58, expect='unknown'
        )

    def test_max_loss_in_stage1(self):
        """
        Test max loss in stage method
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage1()

        print max_loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_loss_stage, price=46.0, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=47.7, expect=False)

    def test_max_loss_get_status1(self):
        """
        Test even get status method
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage1()

        print max_loss_stage
        print '.' * 60
        self.check_get_status(max_loss_stage, new_price=46.6, old_price=46.6, expect='unknown')

    def test_loss_in_stage1(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=47.7, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=49.5, expect=False)

    def test_loss_get_status1(self):
        """
        Test even get status method
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=47.9, old_price=47.7, expect='recovering')
        self.check_get_status(loss_stage, new_price=46.5, old_price=47.7, expect='losing')
        self.check_get_status(loss_stage, new_price=46.5, old_price=46.5, expect='unknown')

    def test_profit_in_stage1(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=48.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=47.5, expect=False)

    def test_profit_get_status1(self):
        """
        Test even get status method
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=49.5, old_price=50, expect='decreasing')
        self.check_get_status(profit_stage, new_price=49, old_price=48.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=49, old_price=49, expect='unknown')

    def test_loss_in_stage2(self):
        """
        Test even in stage method
        """
        loss_stage = self.long_call_backratio.create_loss_stage2()

        print loss_stage
        print '.' * 60
        self.check_in_stage(stage_cls=loss_stage, price=44.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=41, expect=False)

    def test_loss_get_status2(self):
        """
        Test even get status method
        """
        loss_stage = self.long_call_backratio.create_loss_stage2()

        print loss_stage
        print '.' * 60
        self.check_get_status(loss_stage, new_price=44, old_price=45, expect='recovering')
        self.check_get_status(loss_stage, new_price=45, old_price=44, expect='losing')
        self.check_get_status(loss_stage, new_price=45.5, old_price=45.5, expect='unknown')

    def test_profit_in_stage2(self):
        """
        Test even in stage method
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        print profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=profit_stage, price=43.3, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=41, expect=False)

    def test_profit_get_status2(self):
        """
        Test even get status method
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        print profit_stage
        print '.' * 60
        self.check_get_status(profit_stage, new_price=43.5, old_price=43.3, expect='decreasing')
        self.check_get_status(profit_stage, new_price=43.1, old_price=43.3, expect='profiting')
        self.check_get_status(profit_stage, new_price=43.3, old_price=43.3, expect='unknown')

    def test_max_profit_in_stage(self):
        """
        Test max profit in stage method
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_in_stage(stage_cls=max_profit_stage, price=42, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=43.5, expect=False)

    def test_max_profit_get_status(self):
        """
        Test max profit get status method
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage()

        print max_profit_stage
        print '.' * 60
        self.check_get_status(max_profit_stage, new_price=41.5, old_price=41, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=40, old_price=41, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=41, old_price=41, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_call_backratio.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)


class TestStageLongCallBackratio2(TestUnitSetUpStage):
    """
    ,,3/23/15 03:57:38,BACKRATIO,SELL,-1,TO OPEN,SYMBOL,JUN 15,43,CALL,-.58,LMT,DAY,-.58,WORKING
    ,,,,BUY,+2,TO OPEN,MSFT,JUN 15,46,CALL,,,,,
    """

    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=165,
            price=5.25,
            net_price=0.0
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='BUY',
            quantity=2,
            strike=170,
            price=3.25,
            net_price=1.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call_backratio = StageLongCallBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage1()

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
        self.assertEqual(even_stage.stage_expression, '176.00 == {price}')
        self.assertEqual(float(even_stage.price_a), 176.0)
        self.assertEqual(float(even_stage.amount_a), 0.0)
        self.assertEqual(even_stage.left_status, '')
        self.assertEqual(even_stage.left_expression, '')
        self.assertEqual(even_stage.right_status, '')
        self.assertEqual(even_stage.right_expression, '')

    def test_create_max_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage1()

        print 'current_stage: %s' % max_loss_stage
        print 'stage_name: %s' % max_loss_stage.stage_name
        print 'stage_expression: %s' % max_loss_stage.stage_expression
        print 'price_a: %.2f' % max_loss_stage.price_a
        print 'amount_a: %.2f' % max_loss_stage.amount_a
        print 'left_status: %s' % max_loss_stage.left_status
        print 'left_expression: %s' % max_loss_stage.left_expression
        print 'right_status: %s' % max_loss_stage.right_status
        print 'right_expression: %s' % max_loss_stage.right_expression

        self.assertEqual(type(max_loss_stage), PositionStage)
        self.assertFalse(max_loss_stage.id)
        self.assertEqual(max_loss_stage.stage_name, 'MAX_LOSS')
        self.assertEqual(max_loss_stage.stage_expression, '170.00 == {price}')
        self.assertEqual(float(max_loss_stage.price_a), 170.0)
        self.assertEqual(float(max_loss_stage.amount_a), -600.0)
        self.assertEqual(max_loss_stage.left_status, '')
        self.assertEqual(max_loss_stage.left_expression, '')
        self.assertEqual(max_loss_stage.right_status, '')
        self.assertEqual(max_loss_stage.right_expression, '')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

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
        self.assertEqual(loss_stage.stage_expression, '46.00 < {price} < 48.42')
        self.assertEqual(float(loss_stage.price_a), 46.0)
        self.assertEqual(float(loss_stage.amount_a), -242.0)
        self.assertEqual(float(loss_stage.price_b), 48.42)
        self.assertEqual(float(loss_stage.amount_b), 0.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {old_price} < {new_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {new_price} < {old_price} < {price_b}')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage2()

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
        self.assertEqual(loss_stage.stage_expression, '165.00 < {price} < 170.00')
        self.assertEqual(float(loss_stage.price_a), 165.00)
        self.assertEqual(float(loss_stage.amount_a), -100.0)
        self.assertEqual(float(loss_stage.price_b), 170.0)
        self.assertEqual(float(loss_stage.amount_b), -600.0)
        self.assertEqual(loss_stage.left_status, 'recovering')
        self.assertEqual(loss_stage.left_expression, '{price_a} < {new_price} < {old_price} < {price_b}')
        self.assertEqual(loss_stage.right_status, 'losing')
        self.assertEqual(loss_stage.right_expression, '{price_a} < {old_price} < {new_price} < {price_b}')

    def test_create_max_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage2()

        print 'current_stage: %s' % max_loss_stage
        print 'stage_name: %s' % max_loss_stage.stage_name
        print 'stage_expression: %s' % max_loss_stage.stage_expression
        print 'price_a: %.2f' % max_loss_stage.price_a
        print 'amount_a: %.2f' % max_loss_stage.amount_a
        print 'left_status: %s' % max_loss_stage.left_status
        print 'left_expression: %s' % max_loss_stage.left_expression
        print 'right_status: %s' % max_loss_stage.right_status
        print 'right_expression: %s' % max_loss_stage.right_expression

        self.assertEqual(type(max_loss_stage), PositionStage)
        self.assertFalse(max_loss_stage.id)
        self.assertEqual(max_loss_stage.stage_name, 'MAX_LOSS')
        self.assertEqual(max_loss_stage.stage_expression, '{price} <= 165.00')
        self.assertEqual(float(max_loss_stage.price_a), 165.0)
        self.assertEqual(float(max_loss_stage.amount_a), -100.0)
        self.assertEqual(max_loss_stage.left_status, 'easing')
        self.assertEqual(max_loss_stage.left_expression, '{old_price} < {new_price} < {price_a}')
        self.assertEqual(max_loss_stage.right_status, 'worst')
        self.assertEqual(max_loss_stage.right_expression, '{new_price} < {old_price} < {price_a}')


    def test_even_in_stage1(self):
        """
        Test even in stage method
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        print even_stage
        print '.' * 60
        self.check_in_stage(stage_cls=even_stage, price=176.0, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=178.0, expect=False)

    def test_even_get_status1(self):
        """
        Test even get status method
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        print even_stage
        print '.' * 60
        self.check_get_status(
            stage_cls=even_stage, new_price=177, old_price=177, expect='unknown'
        )



















