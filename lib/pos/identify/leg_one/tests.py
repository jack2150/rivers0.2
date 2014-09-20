from lib.test import TestReadyUp
from pms_app.pos_app.models import PositionOption, PositionSet
from lib.pos.identify.leg_one import LegOneIdentify
from lib.pos.spread.leg_one import CallLong, CallNaked, PutLong, PutNaked


class TestLegOneIdentify(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)

        self.option = PositionOption()

    def option_conditions(self, attr, expect_results):
        """
        Test is buy call condition
        """
        options = [(c, q) for c in ['CALL', 'PUT'] for q in [1, -1]]
        print options

        for (contract, quantity), expect in zip(options, expect_results):
            self.option.contract = contract
            self.option.quantity = quantity

            leg_one_identify = LegOneIdentify(self.option)
            result = getattr(leg_one_identify, attr)()

            self.assertEqual(result, expect)

            print 'quantity: %d, contract: %s' % (quantity, contract)
            print 'result: %s\n' % result

    def test_long_call_option(self):
        """
        Test is long call condition
        """
        self.option_conditions('long_call_option', [True, False, False, False])

    def test_short_call_option(self):
        """
        Test is short call condition
        """
        self.option_conditions('short_call_option', [False, True, False, False])

    def test_long_put_option(self):
        """
        Test is long put condition
        """
        self.option_conditions('long_put_option', [False, False, True, False])

    def test_short_put_option(self):
        """
        Test is short put condition
        """
        self.option_conditions('short_put_option', [False, False, False, True])

    def test_get_cls(self):
        """
        Test get name using stock identify class
        """
        self.ready_all(key=3)

        for option in PositionOption.objects.exclude(quantity=0).all():
            leg_one_identify = LegOneIdentify(option)

            cls = leg_one_identify.get_class()

            print 'class name: %s' % cls.__name__

            self.assertIn(
                cls,
                [CallLong, CallNaked,
                 PutLong, PutNaked,
                 None]
            )

            print cls(PositionSet(option.position))
