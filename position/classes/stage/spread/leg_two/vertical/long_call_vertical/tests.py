from position.classes.stage.tests import TestUnitSetUpStage
from long_call_vertical import StageLongCallVertical
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongCallVertical(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 80, 'price': 3.15, 'net_price': 0.0},
            'sell_call': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                          'strike': 85, 'price': 1.51, 'net_price': 4.66},
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

        self.long_call_vertical = StageLongCallVertical(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_call_vertical.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='81.64 == {price}',
            detail={
                'price_a': 81.64,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=81.64, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=79.99, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=83.33, old_price=82.22, expect='unknown'
        )

    def test_create_max_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        max_profit_stage = self.long_call_vertical.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='85.00 <= {price}',
            detail={
                'price_a': 85.0,
                'amount_a': 336.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'guaranteeing',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=86.66, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=83.2, expect=False)

        self.check_get_status(max_profit_stage, new_price=85.32, old_price=86.7, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=86.8, old_price=86.7, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=85.6, old_price=85.6, expect='unknown')

    def test_create_max_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        max_loss_stage = self.long_call_vertical.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price} <= 80.00',
            detail={
                'price_a': 80.0,
                'amount_a': 164.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'worst',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=77.84, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=81, expect=False)

        self.check_get_status(max_loss_stage, new_price=78.18, old_price=76.96, expect='easing')
        self.check_get_status(max_loss_stage, new_price=78.64, old_price=79.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=79.5, old_price=79.5, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        profit_stage = self.long_call_vertical.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='81.64 < {price} < 85.00',
            detail={
                'price_a': 81.64,
                'amount_a': 0.0,
                'price_b': 85.0,
                'amount_b': 336.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=84.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=81.33, expect=False)

        self.check_get_status(profit_stage, new_price=83.5, old_price=84.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=83.5, old_price=82.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=82.64, old_price=82.64, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        loss_stage = self.long_call_vertical.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='80.00 < {price} < 81.64',
            detail={
                'price_a': 80.0,
                'amount_a': -164.0,
                'price_b': 81.64,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=81.38, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=79.6, expect=False)

        self.check_get_status(loss_stage, new_price=81.13, old_price=80.22, expect='recovering')
        self.check_get_status(loss_stage, new_price=80.75, old_price=81.13, expect='losing')
        self.check_get_status(loss_stage, new_price=80.75, old_price=80.75, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_call_vertical.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
