from protective_put import StageProtectivePut
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageProtectivePut(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'BUY', 'quantity': 100,
                      'strike': 0, 'price': 55.95, 'net_price': 0.0},
            'option': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1,
                       'strike': 55, 'price': 1.04, 'net_price': 56.99},
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

        self.protective_put = StageProtectivePut(filled_orders=filled_orders)

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.protective_put.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='56.99 == {price}',
            detail={
                'price_a': 56.99,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=56.99, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=58.1, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=57.2, old_price=57.2, expect='unknown'
        )

    def test_create_max_loss_stage(self):
        """
        Create max loss stage using filled orders data
        """
        max_loss_stage = self.protective_put.create_max_loss_stage()

        self.method_test_create_stage(
            stage=max_loss_stage,
            name='MAX_LOSS',
            expression='{price} <= 55.00',
            detail={
                'price_a': 55.0,
                'amount_a': -199.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'easing',
                'left_expression': '{old_price} < {new_price} <= {price_a}',
                'right_status': 'worst',
                'right_expression': '{new_price} < {old_price} <= {price_a}',
            }
        )

        self.check_in_stage(stage_cls=max_loss_stage, price=52.3, expect=True)
        self.check_in_stage(stage_cls=max_loss_stage, price=56.99, expect=False)

        self.check_get_status(max_loss_stage, new_price=54.6, old_price=53.8, expect='easing')
        self.check_get_status(max_loss_stage, new_price=53.8, old_price=54.5, expect='worst')
        self.check_get_status(max_loss_stage, new_price=52.3, old_price=52.3, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.protective_put.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='55.00 < {price} < 56.99',
            detail={
                'price_a': 55.0,
                'amount_a': -199.0,
                'price_b': 56.99,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
                'right_status': 'losing',
                'right_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=56.2, expect=True)
        self.check_in_stage(stage_cls=loss_stage, price=57.2, expect=False)

        self.check_get_status(loss_stage, new_price=56.5, old_price=56, expect='recovering')
        self.check_get_status(loss_stage, new_price=55.5, old_price=56, expect='losing')
        self.check_get_status(loss_stage, new_price=55.99, old_price=55.99, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.protective_put.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='56.99 < {price}',
            detail={
                'price_a': 56.99,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=57.2, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=56.2, expect=False)

        self.check_get_status(profit_stage, new_price=57.22, old_price=58.3, expect='decreasing')
        self.check_get_status(profit_stage, new_price=59.3, old_price=58.3, expect='profiting')
        self.check_get_status(profit_stage, new_price=57.3, old_price=57.3, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.protective_put.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
