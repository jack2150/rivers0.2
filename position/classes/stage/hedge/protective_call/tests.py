from protective_call import StageProtectiveCall
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageProtectiveCall(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'SELL', 'quantity': -100,
                      'strike': 0, 'price': 52.92, 'net_price': 0.0},
            'option': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                       'strike': 55, 'price': 1.31, 'net_price': 51.61},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.protective_call = StageProtectiveCall(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.protective_call.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 51.61,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=51.61, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=52, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=51.61, old_price=51.61, expect='UNKNOWN'
        )

    def test_create_max_loss_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_loss_stage = self.protective_call.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 55.0,
                'amount_a': -339.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'EASING',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'WORST',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=56.5, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=51.61, expect=False)

        self.check_get_status(max_loss_stage, new_price=55.5, old_price=56.5, expect='EASING')
        self.check_get_status(max_loss_stage, new_price=57.5, old_price=56.5, expect='WORST')
        self.check_get_status(max_loss_stage, new_price=56.5, old_price=56.5, expect='UNKNOWN')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.protective_call.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 51.61,
                'amount_a': 0.0,
                'price_b': 55.00,
                'amount_b': -339.0,
                'left_status': 'RECOVERING',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'LOSING',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=52.3, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=49.9, expect=False)

        self.check_get_status(loss_stage, new_price=52.65, old_price=53.88, expect='RECOVERING')
        self.check_get_status(loss_stage, new_price=54.96, old_price=53.88, expect='LOSING')
        self.check_get_status(loss_stage, new_price=53.88, old_price=53.88, expect='UNKNOWN')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.protective_call.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 51.61,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'DECREASING',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'PROFITING',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=50.1, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=54.5, expect=False)

        self.check_get_status(profit_stage, new_price=47.5, old_price=44.33, expect='DECREASING')
        self.check_get_status(profit_stage, new_price=44.33, old_price=47.5, expect='PROFITING')
        self.check_get_status(profit_stage, new_price=48.5, old_price=48.5, expect='UNKNOWN')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.protective_call.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
