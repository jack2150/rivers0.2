from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder
from short_combo import StageShortCombo


class TestStageShortCombo1(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=211,
            price=2.26,
            net_price=0.0
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='PUT',
            side='BUY',
            quantity=1,
            strike=204,
            price=2.72,
            net_price=0.46
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.short_combo = StageShortCombo(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_combo.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 203.54,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=203.54, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=204, expect=False)

        self.check_get_status(even_stage, new_price=203.54, old_price=203.54, expect='unknown')

    def test_create_max_loss_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_loss_stage = self.short_combo.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 204.0,
                'amount_a': -46.0,
                'price_b': 211.0,
                'amount_b': -46.0,
                'left_status': 'easing',
                'left_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
                'right_status': 'worst',
                'right_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=207, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=203, expect=False)

        self.check_get_status(max_loss_stage, new_price=204, old_price=206, expect='easing')
        self.check_get_status(max_loss_stage, new_price=208, old_price=206, expect='worst')
        self.check_get_status(max_loss_stage, new_price=206, old_price=206, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.short_combo.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 211.0,
                'amount_a': -46.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=212, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=210, expect=False)

        self.check_get_status(loss_stage, new_price=212, old_price=214, expect='recovering')
        self.check_get_status(loss_stage, new_price=216, old_price=214, expect='losing')
        self.check_get_status(loss_stage, new_price=215, old_price=215, expect='unknown')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.short_combo.create_loss_stage2()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 203.54,
                'amount_a': 0.0,
                'price_b': 204.0,
                'amount_b': 46.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=203.8, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=204.1, expect=False)

        self.check_get_status(loss_stage, new_price=203.6, old_price=203.8, expect='recovering')
        self.check_get_status(loss_stage, new_price=203.9, old_price=203.7, expect='losing')
        self.check_get_status(loss_stage, new_price=203.8, old_price=203.8, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.short_combo.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 203.54,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=203, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=205, expect=False)

        self.check_get_status(profit_stage, new_price=202, old_price=201, expect='decreasing')
        self.check_get_status(profit_stage, new_price=201, old_price=202, expect='profiting')
        self.check_get_status(profit_stage, new_price=202, old_price=202, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_combo.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)


class TestStageShortCombo2(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=209,
            price=4.86,
            net_price=0.0
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='PUT',
            side='BUY',
            quantity=1,
            strike=204,
            price=4.52,
            net_price=-0.34
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.short_combo = StageShortCombo(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_combo.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 209.34,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=209.34, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=209, expect=False)

        self.check_get_status(even_stage, new_price=209.34, old_price=209.34, expect='unknown')

    def test_create_max_profit_stage(self):
        """
        Create max loss stage using filled orders data
        """
        max_profit_stage = self.short_combo.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 204,
                'amount_a': 34.0,
                'price_b': 209,
                'amount_b': 34.0,
                'left_status': 'vanishing',
                'left_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
                'right_status': 'guaranteeing',
                'right_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=207, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=203, expect=False)

        self.check_get_status(max_profit_stage, new_price=208, old_price=206, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=204, old_price=206, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=206, old_price=206, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.short_combo.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 209.34,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=211, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=209, expect=False)

        self.check_get_status(loss_stage, new_price=212, old_price=214, expect='recovering')
        self.check_get_status(loss_stage, new_price=216, old_price=214, expect='losing')
        self.check_get_status(loss_stage, new_price=215, old_price=215, expect='unknown')

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.short_combo.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 209.0,
                'amount_a': -34.0,
                'price_b': 209.34,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=209.2, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=209.5, expect=False)

        self.check_get_status(profit_stage, new_price=209.3, old_price=209.1, expect='decreasing')
        self.check_get_status(profit_stage, new_price=209.2, old_price=209.3, expect='profiting')
        self.check_get_status(profit_stage, new_price=209.2, old_price=209.2, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.short_combo.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 204,
                'amount_a': -34.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=203, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=205, expect=False)

        self.check_get_status(profit_stage, new_price=203, old_price=201, expect='decreasing')
        self.check_get_status(profit_stage, new_price=201, old_price=202, expect='profiting')
        self.check_get_status(profit_stage, new_price=202, old_price=202, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_combo.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)


class TestStageShortCombo3(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='CALL',
            side='SELL',
            quantity=-1,
            strike=210,
            price=4.25,
            net_price=0.0
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract='PUT',
            side='BUY',
            quantity=1,
            strike=203,
            price=4.25,
            net_price=0.0
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.short_combo = StageShortCombo(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_combo.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 203.0,
                'amount_a': 0.0,
                'price_b': 210.0,
                'amount_b': 0.0,
                'left_status': 'losing',
                'left_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=206, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=202, expect=False)

        self.check_get_status(even_stage, new_price=208, old_price=206, expect='profiting')
        self.check_get_status(even_stage, new_price=204, old_price=206, expect='losing')
        self.check_get_status(even_stage, new_price=205, old_price=205, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.short_combo.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 210.0,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=211, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=210, expect=False)

        self.check_get_status(loss_stage, new_price=212, old_price=214, expect='recovering')
        self.check_get_status(loss_stage, new_price=216, old_price=214, expect='losing')
        self.check_get_status(loss_stage, new_price=215, old_price=215, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.short_combo.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 203.0,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=202, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=205, expect=False)

        self.check_get_status(profit_stage, new_price=202, old_price=201, expect='decreasing')
        self.check_get_status(profit_stage, new_price=201, old_price=202, expect='profiting')
        self.check_get_status(profit_stage, new_price=202, old_price=202, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_combo.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
