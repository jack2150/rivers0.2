from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder
from long_straddle import StageLongStraddle


class TestStageLongStraddle(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 120, 'price': 2.49, 'net_price': 0.0},
            'buy_put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                        'strike': 120, 'price': 2.16, 'net_price': 4.65},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.contract_right = 100

        self.long_strangle = StageLongStraddle(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_strangle.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 124.65,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=124.65, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=125, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=124.65, old_price=124.65, expect='unknown'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_strangle.create_even_stage2()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 115.35,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=115.35, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=116, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=115.35, old_price=115.35, expect='unknown'
        )

    def test_create_profit_stage1(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_strangle.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 124.65,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=125, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=124, expect=False)

        self.check_get_status(profit_stage, new_price=125, old_price=126, expect='decreasing')
        self.check_get_status(profit_stage, new_price=129, old_price=126, expect='profiting')
        self.check_get_status(profit_stage, new_price=126, old_price=126, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_strangle.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 115.35,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'profiting',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=114, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=116, expect=False)

        self.check_get_status(profit_stage, new_price=113, old_price=112, expect='decreasing')
        self.check_get_status(profit_stage, new_price=111, old_price=113, expect='profiting')
        self.check_get_status(profit_stage, new_price=113, old_price=113, expect='unknown')

    def test_create_loss_stage1(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_strangle.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 120.0,
                'amount_a': -465.0,
                'price_b': 124.65,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=123, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=125, expect=False)

        self.check_get_status(loss_stage, new_price=124, old_price=122, expect='recovering')
        self.check_get_status(loss_stage, new_price=122, old_price=123, expect='losing')
        self.check_get_status(loss_stage, new_price=123, old_price=123, expect='unknown')

    def test_create_loss_stage2(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_strangle.create_loss_stage2()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 115.35,
                'amount_a': 0.0,
                'price_b': 120.0,
                'amount_b': -465.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=118, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=114, expect=False)

        self.check_get_status(loss_stage, new_price=116, old_price=118, expect='recovering')
        self.check_get_status(loss_stage, new_price=119, old_price=117, expect='losing')
        self.check_get_status(loss_stage, new_price=117, old_price=117, expect='unknown')

    def test_create_max_loss_stage1(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.long_strangle.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 120.0,
                'amount_a': -465.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=120, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=119, expect=False)

        self.check_get_status(max_loss_stage, new_price=120, old_price=120, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_strangle.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
