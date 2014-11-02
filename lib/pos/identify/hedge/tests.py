from lib.test import TestReadyUp
from pms_app.pos_app.models import Underlying, InstrumentStock, InstrumentOption, PositionSet
from lib.pos.identify.hedge import HedgeIdentify
from lib.pos.spread import hedge


class TestHedgeIdentify(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)

        self.stock = InstrumentStock()
        self.option = InstrumentOption()

    def stock_cond_method(self, attr, expected):
        """
        For test condition methods
        """
        for qty, expect in zip([1, -1], expected):
            self.stock.quantity = qty

            hedge_identify = HedgeIdentify(self.stock, self.option)
            result = getattr(hedge_identify, attr)()

            self.assertEqual(result, expect)

            print 'stock quantity: %d' % qty
            print 'result: %s\n' % result

    def test_long_stock(self):
        """
        Test is long stock condition
        """
        self.stock_cond_method('long_stock', [True, False])

    def test_short_stock(self):
        """
        Test is short stock condition
        """
        self.stock_cond_method('short_stock', [False, True])

    def option_conditions(self, attr, expect_results):
        """
        Test is buy call condition
        """
        options = [(c, q) for c in ['CALL', 'PUT'] for q in [1, -1]]
        print options

        for (contract, quantity), expect in zip(options, expect_results):
            self.option.contract = contract
            self.option.quantity = quantity

            hedge_identify = HedgeIdentify(self.stock, self.option)
            result = getattr(hedge_identify, attr)()

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

    def test_is_balance(self):
        """
        Test both stock and option are in balance quantity
        """
        samples = [(100, 1), (100, 2), (200, 2), (300, 1)]
        expect_results = [True, False, True, False]

        for (stock_qty, option_qty), expect in zip(samples, expect_results):
            self.stock.quantity = stock_qty
            self.option.quantity = option_qty

            hedge_identify = HedgeIdentify(self.stock, self.option)
            result = hedge_identify.is_balance()

            self.assertEqual(result, expect)

            print 'stock quantity: %d' % stock_qty
            print 'option quantity: %d' % option_qty
            print 'result: %s\n' % result

    def test_get_cls(self):
        """
        Test get name using stock identify class
        """
        self.ready_all(key=2)

        for position in Underlying.objects.all():
            stock = InstrumentStock.objects.filter(position=position).first()
            """:type: PositionStock"""

            option = InstrumentOption.objects.filter(position=position).first()
            """:type: PositionOption"""

            hedge_identify = HedgeIdentify(stock, option)

            cls = hedge_identify.get_class()

            self.assertIn(
                cls,
                [hedge.CoveredCall, hedge.ProtectiveCall,
                 hedge.CoveredPut, hedge.ProtectivePut,
                 None]
            )

            print cls(PositionSet(stock.underlying))
