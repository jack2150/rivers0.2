from long_put_backratio import StageLongPutBackratio
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongPutBackratio1(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='SELL',
            quantity=-1,
            strike=125,
            price=6.15,
            net_price=1.75
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='BUY',
            quantity=2,
            strike=120,
            price=3.95,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put_backratio = StageLongPutBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put_backratio.create_even_stage1()
        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 113.25,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=113.25, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=114, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=even_stage, new_price=113.25, old_price=113.25, expect='UNKNOWN'
        )

    def test_create_max_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_put_backratio.create_max_loss_stage1()
        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 120.0,
                'amount_a': -675.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=120, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=122, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(max_loss_stage, new_price=120, old_price=120, expect='UNKNOWN')

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put_backratio.create_profit_stage1()
        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 113.25,
                'amount_a': 0.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': 'DECREASING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'PROFITING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=112, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=116, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(profit_stage, new_price=112, old_price=111, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=109, old_price=110, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=112, old_price=112, expect='UNKNOWN')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put_backratio.create_loss_stage1()
        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 113.25,
                'amount_a': 0.0,
                'price_b': 120.00,
                'amount_b': -675.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=115, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=111, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(loss_stage, new_price=116, old_price=117, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=118, old_price=116, expect='LOSING')
        self.check_get_status(loss_stage, new_price=116, old_price=116, expect='UNKNOWN')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put_backratio.create_loss_stage2()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 120.00,
                'amount_a': -675.0,
                'price_b': 125.0,
                'amount_b': -175.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=122, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=118, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(loss_stage, new_price=123, old_price=122, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=123, old_price=124, expect='LOSING')
        self.check_get_status(loss_stage, new_price=123, old_price=123, expect='UNKNOWN')

    def test_create_max_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_put_backratio.create_max_loss_stage2()
        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 125.0,
                'amount_a': -175.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'EASING',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'WORST',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=126, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=124, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(max_loss_stage, new_price=127, old_price=127, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_put_backratio.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)


class TestStageLongPutBackratio2(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='SELL',
            quantity=-1,
            strike=20,
            price=2.0,
            net_price=-0.2
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='BUY',
            quantity=2,
            strike=18.0,
            price=0.9,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put_backratio = StageLongPutBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put_backratio.create_even_stage1()
        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 16.20,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=16.2, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=17.2, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=even_stage, new_price=16.2, old_price=16.2, expect='UNKNOWN'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put_backratio.create_even_stage2()
        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 19.80,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=19.8, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=19, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=even_stage, new_price=19.8, old_price=19.8, expect='UNKNOWN'
        )

    def test_create_max_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_put_backratio.create_max_loss_stage1()
        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 18.0,
                'amount_a': -180.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=18, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=19, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=max_loss_stage, new_price=18, old_price=18, expect='UNKNOWN'
        )

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put_backratio.create_profit_stage1()
        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 16.2,
                'amount_a': 0.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': 'DECREASING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'PROFITING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=15, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=16.5, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(profit_stage, new_price=15, old_price=14.5, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=13, old_price=15, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=16, old_price=16, expect='UNKNOWN')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put_backratio.create_loss_stage1()
        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 16.2,
                'amount_a': 0.0,
                'price_b': 18.00,
                'amount_b': -180.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=17, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=18.5, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(loss_stage, new_price=16.8, old_price=17, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=17.5, old_price=17, expect='LOSING')
        self.check_get_status(loss_stage, new_price=17, old_price=17, expect='UNKNOWN')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put_backratio.create_loss_stage2()
        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 18.00,
                'amount_a': -180.0,
                'price_b': 19.8,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=19.5, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=20, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(loss_stage, new_price=19.3, old_price=18.6, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=18.5, old_price=19.2, expect='LOSING')
        self.check_get_status(loss_stage, new_price=18.5, old_price=18.5, expect='UNKNOWN')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put_backratio.create_profit_stage2()
        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 19.8,
                'amount_a': 0.0,
                'price_b': 20.0,
                'amount_b': 20.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=19.9, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=21, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(profit_stage, new_price=19.95, old_price=19.98, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=19.95, old_price=19.92, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=19.9, old_price=19.9, expect='UNKNOWN')

    def test_create_max_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        max_profit_stage = self.long_put_backratio.create_max_profit_stage()
        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 20.0,
                'amount_a': 20.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'VANISHING',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'GUARANTEEING',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=21, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=19, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(max_profit_stage, new_price=20.5, old_price=21, expect='VANISHING')
        self.check_get_status(max_profit_stage, new_price=22, old_price=21, expect='GUARANTEEING')
        self.check_get_status(max_profit_stage, new_price=21, old_price=21, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_put_backratio.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)


class TestStageLongPutBackratio3(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='SELL',
            quantity=-1,
            strike=380,
            price=23.2,
            net_price=0.0
        )

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='BACKRATIO',
            contract='PUT',
            side='BUY',
            quantity=2,
            strike=355,
            price=11.6,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put_backratio = StageLongPutBackratio(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put_backratio.create_even_stage1()
        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 330.00,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=330.0, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=331.0, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=even_stage, new_price=330, old_price=330, expect='UNKNOWN'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put_backratio.create_even_stage2()
        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 380.00,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=380.0, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=379.0, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=even_stage, new_price=380, old_price=380, expect='UNKNOWN'
        )

    def test_create_max_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        max_loss_stage = self.long_put_backratio.create_max_loss_stage1()
        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 355.0,
                'amount_a': -2500.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=355, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=345, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(
            stage_cls=max_loss_stage, new_price=355, old_price=355, expect='UNKNOWN'
        )

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put_backratio.create_profit_stage1()
        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 330.0,
                'amount_a': 0.0,
                'price_b': 0,
                'amount_b': 0,
                'left_status': 'DECREASING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'PROFITING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=320, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=331, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(profit_stage, new_price=321, old_price=310, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=315, old_price=320, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=320, old_price=320, expect='UNKNOWN')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put_backratio.create_loss_stage1()
        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 330.0,
                'amount_a': 0.0,
                'price_b': 355.0,
                'amount_b': -2500.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=340, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=360, expect=False)

        print '\n' + ':' * 80 + '\n'

        self.check_get_status(loss_stage, new_price=335, old_price=345, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=345, old_price=340, expect='LOSING')
        self.check_get_status(loss_stage, new_price=341, old_price=341, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_put_backratio.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)