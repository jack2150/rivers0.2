from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder
from short_strangle import StageShortStrangle


class TestStageShortStrangle(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'sell_call': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                          'strike': 23, 'price': 0.68, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 22, 'price': 0.52, 'net_price': 1.2},
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

        self.short_strangle = StageShortStrangle(
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
                'price_a': 24.2,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=24.2, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=24, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=24.2, old_price=24.2, expect='UNKNOWN'
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
                'price_a': 20.8,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=20.8, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=24, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=20.8, old_price=20.8, expect='UNKNOWN'
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
                'price_a': 24.2,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=25, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=24, expect=False)

        self.check_get_status(loss_stage, new_price=25, old_price=26, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=27, old_price=26, expect='LOSING')
        self.check_get_status(loss_stage, new_price=26, old_price=26, expect='UNKNOWN')

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
                'price_a': 20.8,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'RECOVERING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'LOSING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=20, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=21, expect=False)

        self.check_get_status(loss_stage, new_price=20, old_price=19, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=18, old_price=19, expect='LOSING')
        self.check_get_status(loss_stage, new_price=19, old_price=19, expect='UNKNOWN')

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
                'price_a': 23.0,
                'amount_a': 120.0,
                'price_b': 24.2,
                'amount_b': 0.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=23.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=24.5, expect=False)

        self.check_get_status(profit_stage, new_price=24, old_price=23.5, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=23.2, old_price=23.5, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=23.5, old_price=23.5, expect='UNKNOWN')

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
                'price_a': 20.8,
                'amount_a': 0.0,
                'price_b': 22.0,
                'amount_b': 120.0,
                'left_status': 'DECREASING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'PROFITING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=21.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=23, expect=False)

        self.check_get_status(profit_stage, new_price=21.5, old_price=21.8, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=21.5, old_price=21, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=21.5, old_price=21.5, expect='UNKNOWN')

    def test_create_max_profit_stage1(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.short_strangle.create_max_profit_stage1()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 22.5,
                'amount_a': 120.0,
                'price_b': 23.0,
                'amount_b': 120.0,
                'left_status': 'VANISHING',
                'left_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
                'right_status': 'GUARANTEEING',
                'right_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=22.75, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=23.2, expect=False)

        self.check_get_status(max_profit_stage, new_price=22.9, old_price=22.75, expect='VANISHING')
        self.check_get_status(max_profit_stage, new_price=22.6, old_price=22.75, expect='GUARANTEEING')
        self.check_get_status(max_profit_stage, new_price=22.75, old_price=22.75, expect='UNKNOWN')

    def test_create_max_profit_stage2(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.short_strangle.create_max_profit_stage2()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price} <= {price_b}',
            detail={
                'price_a': 22.0,
                'amount_a': 120.0,
                'price_b': 22.5,
                'amount_b': 120.0,
                'left_status': 'VANISHING',
                'left_expression': '{price_a} <= {new_price} < {old_price} <= {price_b}',
                'right_status': 'GUARANTEEING',
                'right_expression': '{price_a} <= {old_price} < {new_price} <= {price_b}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=22.3, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=22.6, expect=False)

        self.check_get_status(max_profit_stage, new_price=22.2, old_price=22.3, expect='VANISHING')
        self.check_get_status(max_profit_stage, new_price=22.4, old_price=22.3, expect='GUARANTEEING')
        self.check_get_status(max_profit_stage, new_price=22.3, old_price=22.3, expect='UNKNOWN')

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