from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder
from short_straddle import StageShortStraddle


class TestStageShortStraddle(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'sell_call': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                          'strike': 54, 'price': 0.92, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 54, 'price': 0.77, 'net_price': 1.69},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRANGLE',
            contract=self.orders['sell_put']['contract'],
            side=self.orders['sell_put']['side'],
            quantity=self.orders['sell_put']['quantity'],
            strike=self.orders['sell_put']['strike'],
            price=self.orders['sell_put']['price'],
            net_price=self.orders['sell_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.contract_right = 100

        self.short_strangle = StageShortStraddle(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage1(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_strangle.create_even_stage1()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 55.69,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=55.69, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=55, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=55.69, old_price=55.69, expect='unknown'
        )

    def test_create_even_stage2(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_strangle.create_even_stage2()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 52.31,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=52.31, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=53, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=52.31, old_price=52.31, expect='unknown'
        )

    def test_create_loss_stage1(self):
        """
        Create profit stage using filled orders data
        """
        loss_stage = self.short_strangle.create_loss_stage1()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price}',
            detail={
                'price_a': 55.69,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=57, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=55, expect=False)

        self.check_get_status(loss_stage, new_price=57, old_price=58, expect='recovering')
        self.check_get_status(loss_stage, new_price=59, old_price=58, expect='losing')
        self.check_get_status(loss_stage, new_price=57, old_price=57, expect='unknown')

    def test_create_loss_stage2(self):
        """
        Create profit stage using filled orders data
        """
        loss_stage = self.short_strangle.create_loss_stage2()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 52.31,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'losing',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=50, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=53, expect=False)

        self.check_get_status(loss_stage, new_price=51.5, old_price=50, expect='recovering')
        self.check_get_status(loss_stage, new_price=49.9, old_price=50, expect='losing')
        self.check_get_status(loss_stage, new_price=50.5, old_price=50.5, expect='unknown')

    def test_create_profit_stage1(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.short_strangle.create_profit_stage1()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 54.0,
                'amount_a': 169.0,
                'price_b': 55.69,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=55, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=56, expect=False)

        self.check_get_status(profit_stage, new_price=55.2, old_price=55, expect='decreasing')
        self.check_get_status(profit_stage, new_price=54.3, old_price=54.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=54, old_price=54, expect='unknown')

    def test_create_profit_stage2(self):
        """
        Create loss stage using filled orders data
        """
        profit_stage = self.short_strangle.create_profit_stage2()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 52.31,
                'amount_a': 0.0,
                'price_b': 54.0,
                'amount_b': 169.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=53, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=51, expect=False)

        self.check_get_status(profit_stage, new_price=52.8, old_price=53.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=53.5, old_price=53, expect='profiting')
        self.check_get_status(profit_stage, new_price=53, old_price=53, expect='unknown')

    def test_create_max_profit_stage1(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.short_strangle.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 54.0,
                'amount_a': 169.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=54.0, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=55, expect=False)

        self.check_get_status(max_profit_stage, new_price=54, old_price=54, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_strangle.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)