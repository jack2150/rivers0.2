from naked_put import StageNakedPut
from position.classes.stage.tests import TestUnitSetUpStage
from position.classes.tests import create_filled_order
from position.models import PositionStage
from tos_import.statement.statement_trade.models import FilledOrder


class TestStageNakedPut(TestUnitSetUpStage):
    def setUp(self):
        TestUnitSetUpStage.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='SELL',
            quantity=-1,
            strike=40,
            price=0.74
        )

        self.contract_right = 100

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)

        self.long_put = StageNakedPut(
            filled_orders=filled_orders, contract_right=self.contract_right
        )

    def test_create_even_stage(self):
        """
        Create even stage using filled orders data
        """
        even_stage = self.long_put.create_even_stage()

        self.method_test_create_stage(
            stage=even_stage,
            name='EVEN',
            expression='{price_a} == {current_price}',
            detail={
                'price_a': 39.26,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': '',
                'left_expression': '',
                'right_status': '',
                'right_expression': '',
            }
        )

        self.check_in_stage(stage_cls=even_stage, price=39.26, expect=True)
        self.check_in_stage(stage_cls=even_stage, price=40, expect=False)

        self.check_get_status(
            stage_cls=even_stage, new_price=39.26, old_price=39.26, expect='unknown'
        )

    def test_create_max_profit_stage(self):
        """
        Create max profit stage using filled orders data
        """
        max_profit_stage = self.long_put.create_max_profit_stage()

        self.method_test_create_stage(
            stage=max_profit_stage,
            name='MAX_PROFIT',
            expression='{price_a} <= {current_price}',
            detail={
                'price_a': 40.0,
                'amount_a': 74.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'vanishing',
                'left_expression': '{price_a} <= {new_price} < {old_price}',
                'right_status': 'guaranteeing',
                'right_expression': '{price_a} <= {old_price} < {new_price}',
            }
        )

        self.check_in_stage(stage_cls=max_profit_stage, price=41, expect=True)
        self.check_in_stage(stage_cls=max_profit_stage, price=39, expect=False)

        self.check_get_status(max_profit_stage, new_price=40.5, old_price=41, expect='vanishing')
        self.check_get_status(max_profit_stage, new_price=43.66, old_price=41, expect='guaranteeing')
        self.check_get_status(max_profit_stage, new_price=42, old_price=42, expect='unknown')

    def test_create_profit_stage(self):
        """
        Create profit stage using filled orders data
        """
        profit_stage = self.long_put.create_profit_stage()

        self.method_test_create_stage(
            stage=profit_stage,
            name='PROFIT',
            expression='{price_a} < {current_price} < {price_b}',
            detail={
                'price_a': 39.26,
                'amount_a': 0.0,
                'price_b': 40.00,
                'amount_b': 74.0,
                'left_status': 'decreasing',
                'left_expression': '{price_a} < {new_price} < {old_price} < {price_b}',
                'right_status': 'profiting',
                'right_expression': '{price_a} < {old_price} < {new_price} < {price_b}',
            }
        )

        self.check_in_stage(stage_cls=profit_stage, price=39.5, expect=True)
        self.check_in_stage(stage_cls=profit_stage, price=38.5, expect=False)

        self.check_get_status(profit_stage, new_price=39.3, old_price=39.5, expect='decreasing')
        self.check_get_status(profit_stage, new_price=39.6, old_price=39.5, expect='profiting')
        self.check_get_status(profit_stage, new_price=39.5, old_price=39.5, expect='unknown')

    def test_create_loss_stage(self):
        """
        Create loss stage using filled orders data
        """
        loss_stage = self.long_put.create_loss_stage()

        self.method_test_create_stage(
            stage=loss_stage,
            name='LOSS',
            expression='{current_price} < {price_a}',
            detail={
                'price_a': 39.26,
                'amount_a': 0.0,
                'price_b': 0.0,
                'amount_b': 0.0,
                'left_status': 'recovering',
                'left_expression': '{old_price} < {new_price} < {price_a}',
                'right_status': 'losing',
                'right_expression': '{new_price} < {old_price} < {price_a}',
            }
        )

        self.check_in_stage(stage_cls=loss_stage, price=41, expect=False)
        self.check_in_stage(stage_cls=loss_stage, price=39, expect=True)

        self.check_get_status(loss_stage, new_price=38.9, old_price=37.2, expect='recovering')
        self.check_get_status(loss_stage, new_price=36.8, old_price=37.2, expect='losing')
        self.check_get_status(loss_stage, new_price=38, old_price=38, expect='unknown')

    def test_create_stages(self):
        """
        Test create stages using filled orders
        """
        print 'run create_stages...'
        stages = self.long_put.create_stages()
        self.assertEqual(type(stages), list)

        for stage in stages:
            print stage
            self.assertEqual(type(stage), PositionStage)
