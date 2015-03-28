from short_call_backratio import StageShortCallBackratio
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCallBackratio1(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='BUY',
            quantity=1,
            strike=43,
            price=1.42,
            net_price=0.58
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='SELL',
            quantity=-2,
            strike=46,
            price=.42,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call_backratio = StageShortCallBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='48.42 == {price}',
            detail={
                'price_a': 48.42,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=48.42, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=49, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=48.42, old_price=48.42, expect='unknown'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage2()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='43.58 == {price}',
            detail={
                'price_a': 43.58,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=43.58, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=44, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=43.58, old_price=43.58, expect='unknown'
        )

    def test_create_max_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage1()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='46.00 == {price}',
            detail={
                'price_a': 46.0,
                'amount_a': 242.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=46.0, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=47.7, expect=False)

        self.check_get_status(max_profit_stage, new_price=46.6, old_price=46.6, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create profit stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='48.42 < {price}',
            detail={
                'price_a': 48.42,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=49, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=47, expect=False)

        self.check_get_status(loss_stage, new_price=49, old_price=50, expect='recovering')
        self.check_get_status(loss_stage, new_price=51, old_price=50.5, expect='losing')
        self.check_get_status(loss_stage, new_price=49.5, old_price=49.5, expect='unknown')

    def test_create_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='46.00 < {price} < 48.42',
            detail={
                'price_a': 46.0,
                'amount_a': 242.0,
                'price_b': 48.42,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=47, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=49, expect=False)

        self.check_get_status(profit_stage, new_price=47, old_price=46.2, expect='decreasing')
        self.check_get_status(profit_stage, new_price=46.5, old_price=47, expect='profiting')
        self.check_get_status(profit_stage, new_price=47, old_price=47, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='43.58 < {price} < 46.00',
            detail={
                'price_a': 43.58,
                'amount_a': 0.0,
                'price_b': 46.0,
                'amount_b': 242.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=44.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=41, expect=False)

        self.check_get_status(profit_stage, new_price=44, old_price=45, expect='decreasing')
        self.check_get_status(profit_stage, new_price=44.8, old_price=44.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=44.5, old_price=44.5, expect='unknown')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage2()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='43.00 < {price} < 43.58',
            detail={
                'price_a': 43.0,
                'amount_a': -58.0,
                'price_b': 43.58,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=43.2, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=40, expect=False)

        self.check_get_status(loss_stage, new_price=43.4, old_price=43.3, expect='recovering')
        self.check_get_status(loss_stage, new_price=43.2, old_price=43.3, expect='losing')
        self.check_get_status(loss_stage, new_price=43.3, old_price=43.3, expect='unknown')

    def test_create_max_loss_stage1(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.long_call_backratio.create_max_loss_stage1()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price} <= 43.00',
            detail={
                'price_a': 43.0,
                'amount_a': -58.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'worst',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=42.5, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=46, expect=False)

        self.check_get_status(max_loss_stage, new_price=42.5, old_price=41, expect='easing')
        self.check_get_status(max_loss_stage, new_price=41, old_price=42.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=42, old_price=42, expect='unknown')

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
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='BUY',
            quantity=1,
            strike=165,
            price=5.25,
            net_price=-1.0
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='SELL',
            quantity=-2,
            strike=170,
            price=3.25,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call_backratio = StageShortCallBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='176.00 == {price}',
            detail={
                'price_a': 176.0,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=176.0, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=178.0, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=176, old_price=176, expect='unknown'
        )

    def test_create_max_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage1()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='170.00 == {price}',
            detail={
                'price_a': 170.0,
                'amount_a': 600.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=170, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=172, expect=False)

        self.check_get_status(max_profit_stage, new_price=171, old_price=171, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create profit stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='176.00 < {price}',
            detail={
                'price_a': 176,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=177, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=175, expect=False)

        self.check_get_status(loss_stage, new_price=177, old_price=178.5, expect='recovering')
        self.check_get_status(loss_stage, new_price=179, old_price=177, expect='losing')
        self.check_get_status(loss_stage, new_price=177, old_price=177, expect='unknown')

    def test_create_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='170.00 < {price} < 176.00',
            detail={
                'price_a': 170.0,
                'amount_a': 600.0,
                'price_b': 176.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=171, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=169, expect=False)

        self.check_get_status(profit_stage, new_price=174, old_price=173, expect='decreasing')
        self.check_get_status(profit_stage, new_price=173, old_price=174, expect='profiting')
        self.check_get_status(profit_stage, new_price=172, old_price=172, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='165.00 < {price} < 170.00',
            detail={
                'price_a': 165.0,
                'amount_a': 100,
                'price_b': 170.0,
                'amount_b': 600.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=168, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=172, expect=False)

        self.check_get_status(profit_stage, new_price=167, old_price=169, expect='decreasing')
        self.check_get_status(profit_stage, new_price=169, old_price=167, expect='profiting')
        self.check_get_status(profit_stage, new_price=168, old_price=168, expect='unknown')

    def test_create_max_profit_stage2(self):
        """
        Create loss stage using filled orders data
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage2()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price} <= 165.00',
            detail={
                'price_a': 165.0,
                'amount_a': 100.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'guaranteeing',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=164, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=167, expect=False)

        self.check_get_status(max_profit_stage, new_price=163, old_price=163, expect='unknown')

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


class TestStageLongCallBackratio3(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='BUY',
            quantity=1,
            strike=72.5,
            price=1,
            net_price=0.0
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='CALL',
            side='SELL',
            quantity=-2,
            strike=75.0,
            price=0.5,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_call_backratio = StageShortCallBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='77.50 == {price}',
            detail={
                'price_a': 77.5,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=77.50, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=78.0, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=79, old_price=79, expect='unknown'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_backratio.create_even_stage2()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='72.50 <= {price}',
            detail={
                'price_a': 72.5,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

    def test_create_max_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_profit_stage = self.long_call_backratio.create_max_profit_stage1()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='75.00 == {price}',
            detail={
                'price_a': 75.0,
                'amount_a': 250.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=75, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=76, expect=False)

        self.check_get_status(max_profit_stage, new_price=75, old_price=75, expect='unknown')

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='75.00 < {price} < 77.50',
            detail={
                'price_a': 75.0,
                'amount_a': 250.0,
                'price_b': 77.50,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=76.8, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=79, expect=False)

        self.check_get_status(profit_stage, new_price=76.8, old_price=75.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=75.5, old_price=76.8, expect='profiting')
        self.check_get_status(profit_stage, new_price=76.8, old_price=76.8, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.long_call_backratio.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='72.50 < {price} < 75.00',
            detail={
                'price_a': 72.5,
                'amount_a': 0.0,
                'price_b': 75.0,
                'amount_b': 250.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=73.8, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=77, expect=False)

        self.check_get_status(profit_stage, new_price=73.6, old_price=74.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=74.2, old_price=73.8, expect='profiting')
        self.check_get_status(profit_stage, new_price=73.8, old_price=73.8, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create profit stage using filled orders data
        """
        loss_stage = self.long_call_backratio.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='77.50 < {price}',
            detail={
                'price_a': 77.5,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=79, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=76, expect=False)

        self.check_get_status(loss_stage, new_price=77.8, old_price=79, expect='recovering')
        self.check_get_status(loss_stage, new_price=79, old_price=78.5, expect='losing')
        self.check_get_status(loss_stage, new_price=79, old_price=79, expect='unknown')

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
