from position.classes.stage.tests import TestUnitSetUpStage
from short_call_vertical import StageShortCallVertical
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageShortCallVertical(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 80, 'price': 3.15, 'net_price': 0.0},
            'sell_call': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                          'strike': 75, 'price': 5.6, 'net_price': -2.45},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.short_call_vertical = StageShortCallVertical(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_call_vertical.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='77.55 == {price}',
            detail={
                'price_a': 77.55,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=77.55, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=79.99, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=77.55, old_price=77.55, expect='unknown'
        )

    def test_create_max_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        max_profit_stage = self.short_call_vertical.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price} <= 75.00',
            detail={
                'price_a': 75.0,
                'amount_a': 245.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'guaranteeing',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=75, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=78.25, expect=False)

        self.check_get_status(max_profit_stage, new_price=74.91, old_price=74.5, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=72.9, old_price=74.5, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=73.3, old_price=73.3, expect='unknown')

    def test_create_max_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        max_loss_stage = self.short_call_vertical.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='80.00 <= {price}',
            detail={
                'price_a': 80.0,
                'amount_a': -255.00,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'worst',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=80.85, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=79.22, expect=False)

        self.check_get_status(max_loss_stage, new_price=81.97, old_price=82.1, expect='easing')
        self.check_get_status(max_loss_stage, new_price=83.5, old_price=82.1, expect='worst')
        self.check_get_status(max_loss_stage, new_price=82.2, old_price=82.2, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        profit_stage = self.short_call_vertical.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='75.00 < {price} < 77.55',
            detail={
                'price_a': 75.00,
                'amount_a': 245.00,
                'price_b': 77.55,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=76.66, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=78.2, expect=False)

        self.check_get_status(profit_stage, new_price=76.33, old_price=75.91, expect='decreasing')
        self.check_get_status(profit_stage, new_price=75.91, old_price=76.4, expect='profiting')
        self.check_get_status(profit_stage, new_price=75.8, old_price=75.8, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        loss_stage = self.short_call_vertical.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='77.55 < {price} < 80.00',
            detail={
                'price_a': 77.55,
                'amount_a': 0.0,
                'price_b': 80.0,
                'amount_b': -255.00,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=79.22, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=80.46, expect=False)

        self.check_get_status(loss_stage, new_price=77.93, old_price=79.77, expect='recovering')
        self.check_get_status(loss_stage, new_price=79.2, old_price=78.12, expect='losing')
        self.check_get_status(loss_stage, new_price=78.88, old_price=78.88, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_call_vertical.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
