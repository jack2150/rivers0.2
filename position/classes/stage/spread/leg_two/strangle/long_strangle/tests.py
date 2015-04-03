from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder
from long_strangle import StageLongStrangle


class TestStageLongStrangle(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 85, 'price': 1.18, 'net_price': 2.55},
            'buy_put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                        'strike': 80, 'price': 1.37, 'net_price': 0.0},
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

        self.long_strangle = StageLongStrangle(
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
                'price_a': 87.55,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=87.55, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=87, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=87.55, old_price=87.55, expect='UNKNOWN'
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
                'price_a': 77.45,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=77.45, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=77.5, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=77.45, old_price=77.45, expect='UNKNOWN'
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
                'price_a': 87.55,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=88, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=87, expect=False)

        self.check_get_status(profit_stage, new_price=89, old_price=90, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=89, old_price=88, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=88, old_price=88, expect='UNKNOWN')

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
                'price_a': 77.45,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'DECREASING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'PROFITING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=76, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=78, expect=False)

        self.check_get_status(profit_stage, new_price=77.3, old_price=76, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=76, old_price=77, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=76, old_price=76, expect='UNKNOWN')

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
                'price_a': 85.0,
                'amount_a': -255.0,
                'price_b': 87.55,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=86, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=88, expect=False)

        self.check_get_status(loss_stage, new_price=86.5, old_price=85.5, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=85.5, old_price=86, expect='LOSING')
        self.check_get_status(loss_stage, new_price=86, old_price=86, expect='UNKNOWN')

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
                'price_a': 77.45,
                'amount_a': 0.0,
                'price_b': 80.0,
                'amount_b': -255.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=78, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=76, expect=False)

        self.check_get_status(loss_stage, new_price=78, old_price=79, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=79.5, old_price=79, expect='LOSING')
        self.check_get_status(loss_stage, new_price=78, old_price=78, expect='UNKNOWN')

    def test_create_max_loss_stage1(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.long_strangle.create_max_loss_stage1()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 82.5,
                'amount_a': -255.0,
                'price_b': 85.0,
                'amount_b': -255.0,
                'left_status': 'EASING',
                'left_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
                'right_status': 'WORST',
                'right_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=83, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=85.5, expect=False)

        self.check_get_status(max_loss_stage, new_price=84, old_price=83.5, expect='EASING')
        self.check_get_status(max_loss_stage, new_price=82.8, old_price=83.5, expect='WORST')
        self.check_get_status(max_loss_stage, new_price=83, old_price=83, expect='UNKNOWN')

    def test_create_max_loss_stage2(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.long_strangle.create_max_loss_stage2()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 80.0,
                'amount_a': -255.0,
                'price_b': 82.5,
                'amount_b': -255.0,
                'left_status': 'EASING',
                'left_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
                'right_status': 'WORST',
                'right_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=81, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=83, expect=False)

        self.check_get_status(max_loss_stage, new_price=80.6, old_price=82, expect='EASING')
        self.check_get_status(max_loss_stage, new_price=82.3, old_price=81, expect='WORST')
        self.check_get_status(max_loss_stage, new_price=81, old_price=81, expect='UNKNOWN')

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
