from position.classes.stage.tests import TestUnitSetUpStage
from short_put_vertical import StageShortPutVertical
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageLongPutVertical(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'buy_put': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                        'strike': 25, 'price': 0.65, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 27, 'price': 1.91, 'net_price': -1.26},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_put']['contract'],
            side=self.orders['sell_put']['side'],
            quantity=self.orders['sell_put']['quantity'],
            strike=self.orders['sell_put']['strike'],
            price=self.orders['sell_put']['price'],
            net_price=self.orders['sell_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.short_put_vertical = StageShortPutVertical(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.short_put_vertical.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='25.74 == {price}',
            detail={
                'price_a': 25.74,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=25.74, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=26, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=28.88, old_price=28.88, expect='unknown'
        )

    def test_create_max_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        max_profit_stage = self.short_put_vertical.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='27.00 <= {price}',
            detail={
                'price_a': 27.0,
                'amount_a': 126.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'guaranteeing',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=27.2, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=25.1, expect=False)

        self.check_get_status(max_profit_stage, new_price=27.32, old_price=27.5, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=28.6, old_price=27.5, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=27.5, old_price=27.5, expect='unknown')

    def test_create_max_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        max_loss_stage = self.short_put_vertical.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price} <= 25.00',
            detail={
                'price_a': 25.0,
                'amount_a': -74.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'worst',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=24.1, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=25.1, expect=False)

        self.check_get_status(max_loss_stage, new_price=24.88, old_price=24, expect='easing')
        self.check_get_status(max_loss_stage, new_price=23.5, old_price=24, expect='worst')
        self.check_get_status(max_loss_stage, new_price=24.5, old_price=24.5, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create even stage using filled orders data
        """
        profit_stage = self.short_put_vertical.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='25.74 < {price} < 27.00',
            detail={
                'price_a': 25.74,
                'amount_a': 0.0,
                'price_b': 27.0,
                'amount_b': 126.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=26.3, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=25.3, expect=False)

        self.check_get_status(profit_stage, new_price=26.4, old_price=26.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=26.6, old_price=26.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=26.5, old_price=26.5, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create even stage using filled orders data
        """
        loss_stage = self.short_put_vertical.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='25.00 < {price} < 25.74',
            detail={
                'price_a': 25.0,
                'amount_a': -74.0,
                'price_b': 25.74,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=25.5, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=26.8, expect=False)

        self.check_get_status(loss_stage, new_price=25.33, old_price=25.25, expect='recovering')
        self.check_get_status(loss_stage, new_price=25.11, old_price=25.25, expect='losing')
        self.check_get_status(loss_stage, new_price=25.5, old_price=25.5, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.short_put_vertical.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
