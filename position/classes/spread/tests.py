# noinspection PyUnresolvedReferences
import position.classes.ready_django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from position.classes.spread.spread import Spread
from position.classes.tests import TestUnitSetUpPrepare
from tos_import.models import Statement
from tos_import.statement.statement_trade.models import TradeSummary
from tos_import.statement.statement_trade.models import FilledOrder


class TestSpread(TestUnitSetUpPrepare):
    def get_object_test(self, test_method, spread, underlying=None, future=None, forex=None):
        """
        Method use for testing get underlying, future and forex
        """
        # create filled order with underlying
        print 'create filled order object...'
        self.filled_order = self.create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            future=self.future,
            forex=self.forex,
            spread=spread,
            contract='ETF',
            side='BUY',
            quantity=1
        )

        # get queryset using filled order object
        print 'get filled order using queryset and run spread class...'
        if future:
            filled_orders = FilledOrder.objects.filter(future=future).all()
            cls = future
        elif forex:
            filled_orders = FilledOrder.objects.filter(forex=forex).all()
            cls = forex
        else:
            filled_orders = FilledOrder.objects.filter(underlying=underlying).all()
            cls = underlying

        self.spread = Spread(
            filled_orders=filled_orders
        )
        result = getattr(self.spread, test_method)()

        print 'get %s result: %s' % (test_method, result)
        print '%s is same? %s == %s? %s' % (
            cls.__class__.__name__,
            result.symbol, cls.symbol,
            result.id == cls.id
        )
        self.assertEqual(result.id, cls.id)

        print 'remove filled order object...'
        self.filled_order.delete()

    def test_get_underlying(self):
        """
        Test get underlying from filled order
        """
        self.get_object_test(
            test_method='get_underlying',
            spread='STOCK',
            underlying=self.underlying
        )

    def test_get_future(self):
        """
        Test get future from filled order
        """
        self.get_object_test(
            test_method='get_future',
            spread='FUTURE',
            future=self.future
        )

    def test_get_forex(self):
        """
        Test get forex from filled order
        """
        self.get_object_test(
            test_method='get_forex',
            spread='FOREX',
            forex=self.forex
        )

    def test_get_name(self):
        """
        Test get name from filled order
        """
        self.spreads = [
            'STOCK', 'COVERED', 'SINGLE', 'FUTURE',
            'FOREX', 'VERTICAL', 'STRANGLE'
        ]

        self.results = [
            'EQUITY', 'HEDGE', 'OPTION', 'FUTURE',
            'FOREX', 'SPREAD', 'SPREAD'
        ]

        for key, spread in enumerate(self.spreads):
            print 'create filled order using spread: %s...' % spread
            self.filled_order = self.create_filled_order(
                trade_summary=self.trade_summary,
                spread=spread,
                contract='ETF',
                underlying=self.underlying,
                side='BUY',
                quantity=1
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

            self.spread = Spread(filled_orders=filled_orders)
            result = self.spread.get_name()

            print 'get_name result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            self.filled_order.delete()

            print '-' * 80

    def test_get_equity_spread(self):
        """
        Test get equity spread name using filled order
        """
        spread = 'STOCK'

        self.contracts = ['STOCK', 'ETF', 'FUND', 'STOCK', 'ETF', 'STOCK', 'STOCK']

        self.sides = ['BUY', 'SELL', 'BUY', 'SELL', 'BUY', 'SELL', 'BUY']

        self.quantities = [100, -200, 421, -81, 999, -4896, 17173]

        self.results = [
            'LONG_STOCK', 'SHORT_STOCK', 'LONG_STOCK', 'SHORT_STOCK',
            'LONG_STOCK', 'SHORT_STOCK', 'LONG_STOCK',
        ]

        for key, contract in enumerate(self.contracts):
            print 'create filled order using spread: %s contract: %s...' % (spread, contract)
            self.filled_order = self.create_filled_order(
                trade_summary=self.trade_summary,
                underlying=self.underlying,
                spread=spread,
                contract=contract,
                side=self.sides[key],
                quantity=self.quantities[key]
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

            self.spread = Spread(filled_orders=filled_orders)
            self.spread.name = self.spread.get_name()
            result = self.spread.get_equity_spread()

            print 'result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            self.filled_order.delete()

            print '-' * 80

    def test_get_hedge_spread(self):
        """
        Test get hedge spread name using filled order
        hedge contain 8 spread names
        """
        spread = 'COVERED'

        self.contracts = [
            ('STOCK', 'CALL'), ('STOCK', 'PUT'), ('STOCK', 'CALL'), ('STOCK', 'PUT'),
            ('STOCK', 'CALL'), ('STOCK', 'PUT'), ('STOCK', 'CALL'), ('STOCK', 'PUT')
        ]

        self.sides = [
            ('BUY', 'BUY'), ('BUY', 'BUY'), ('BUY', 'SELL'), ('BUY', 'SELL'),
            ('SELL', 'BUY'), ('SELL', 'BUY'), ('SELL', 'SELL'), ('SELL', 'SELL')
        ]

        self.quantities = [
            (100, 1), (400, 4), (9000, -90), (700, -7),
            (-5500, 55), (-6400, 64), (-200, -2), (-1000, -10)
        ]

        self.results = [
            'CUSTOM', 'PROTECTIVE_PUT', 'COVERED_CALL', 'CUSTOM',
            'PROTECTIVE_CALL', 'CUSTOM', 'CUSTOM', 'COVERED_PUT'
        ]

        for key, (stock, option) in enumerate(self.contracts):
            print 'create filled order using spread: %s, stock: %s, option: %s...' % (spread, stock, option)
            self.filled_order_stock = self.create_filled_order(
                trade_summary=self.trade_summary,
                underlying=self.underlying,
                spread=spread,
                contract=stock,
                side=self.sides[key][0],
                quantity=self.quantities[key][0]
            )

            self.filled_order_option = self.create_filled_order(
                trade_summary=self.trade_summary,
                underlying=self.underlying,
                spread=spread,
                contract=option,
                side=self.sides[key][1],
                quantity=self.quantities[key][1]
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

            self.spread = Spread(filled_orders=filled_orders)
            self.spread.name = self.spread.get_name()
            result = self.spread.get_hedge_spread()

            print 'result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            print '-' * 80

            self.filled_order_stock.delete()
            self.filled_order_option.delete()

    def test_get_option_spread(self):
        """
        Test get option spread name using filled order
        """
        spread = 'SINGLE'

        self.contracts = ['CALL', 'PUT', 'CALL', 'PUT']

        self.sides = ['BUY', 'BUY', 'SELL', 'SELL']

        self.quantities = [1, 35, -8, -17]

        self.results = ['LONG_CALL', 'LONG_PUT', 'NAKED_CALL', 'NAKED_PUT']

        for key, contract in enumerate(self.contracts):
            print 'create filled order using spread: %s contract: %s...' % (spread, contract)
            self.filled_order = self.create_filled_order(
                trade_summary=self.trade_summary,
                underlying=self.underlying,
                spread=spread,
                contract=contract,
                side=self.sides[key],
                quantity=self.quantities[key]
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

            self.spread = Spread(filled_orders=filled_orders)
            self.spread.name = self.spread.get_name()
            result = self.spread.get_option_spread()

            print 'result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            self.filled_order.delete()

            print '-' * 80

    def test_get_future_spread(self):
        """
        Test get option spread name using filled order
        """
        spread = 'FUTURE'

        self.contracts = ['FUTURE', 'FUTURE']

        self.sides = ['BUY', 'SELL']

        self.quantities = [1, -22]

        self.results = ['LONG_FUTURE', 'SHORT_FUTURE']

        for key, contract in enumerate(self.contracts):
            print 'create filled order using spread: %s contract: %s...' % (spread, contract)
            self.filled_order = self.create_filled_order(
                trade_summary=self.trade_summary,
                future=self.future,
                spread=spread,
                contract=contract,
                side=self.sides[key],
                quantity=self.quantities[key]
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(future=self.future).all()

            self.spread = Spread(filled_orders=filled_orders)
            self.spread.name = self.spread.get_name()
            result = self.spread.get_future_spread()

            print 'result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            self.filled_order.delete()

            print '-' * 80

    def test_get_forex_spread(self):
        """
        Test get option spread name using filled order
        """
        spread = 'FOREX'

        self.contracts = ['FOREX', 'FOREX']

        self.sides = ['BUY', 'SELL']

        self.quantities = [1, -22]

        self.results = ['LONG_FOREX', 'SHORT_FOREX']

        for key, contract in enumerate(self.contracts):
            print 'create filled order using spread: %s contract: %s...' % (spread, contract)
            self.filled_order = self.create_filled_order(
                trade_summary=self.trade_summary,
                forex=self.forex,
                spread=spread,
                contract=contract,
                side=self.sides[key],
                quantity=self.quantities[key]
            )

            print 'get filled order using queryset and run spread class...'
            filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

            self.spread = Spread(filled_orders=filled_orders)
            self.spread.name = self.spread.get_name()
            result = self.spread.get_forex_spread()

            print 'result: %s, expected: %s' % (result, self.results[key])
            self.assertEqual(result, self.results[key])

            self.filled_order.delete()

            print '-' * 80

    def test_two_leg_options_spread(self):
        """
        Test get 2 legs option spread
        """
        self.spreads = ['VERTICAL', 'STRANGLE', 'STRADDLE', 'COMBO', 'BACKRATIO']

        self.four_legs = {
            'VERTICAL': [
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 100},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 105},
                    'result': 'LONG_CALL_VERTICAL'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 100},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 105},
                    'result': 'SHORT_CALL_VERTICAL'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 5, 'strike': 100},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -5, 'strike': 105},
                    'result': 'SHORT_PUT_VERTICAL'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -5, 'strike': 100},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 5, 'strike': 105},
                    'result': 'LONG_PUT_VERTICAL'
                }
            ],
            'STRANGLE': [
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 13, 'strike': 90},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 13, 'strike': 110},
                    'result': 'LONG_STRANGLE'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -37, 'strike': 90},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -37, 'strike': 110},
                    'result': 'SHORT_STRANGLE'
                },
            ],
            'STRADDLE': [
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 49, 'strike': 100},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 49, 'strike': 100},
                    'result': 'LONG_STRADDLE'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -51, 'strike': 100},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -51, 'strike': 100},
                    'result': 'SHORT_STRADDLE'
                },
            ],
            'COMBO': [
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 530, 'strike': 105},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -530, 'strike': 95},
                    'result': 'LONG_COMBO'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -102, 'strike': 95},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 102, 'strike': 105},
                    'result': 'SHORT_COMBO'
                }
            ],
            'BACKRATIO': [
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 20},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 21},
                    'result': 'SHORT_CALL_BACKRATIO'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 20},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 2, 'strike': 21},
                    'result': 'LONG_CALL_BACKRATIO'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 19},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 18},
                    'result': 'LONG_PUT_BACKRATIO'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 19},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 2, 'strike': 18},
                    'result': 'SHORT_PUT_BACKRATIO'
                }
            ]
        }

        for spread in self.spreads:
            two_legs = self.four_legs[spread]

            for option_data in two_legs:
                print 'create 2 filled orders using spread: %s...' % spread
                self.filled_order1 = self.create_filled_order(
                    trade_summary=self.trade_summary,
                    underlying=self.underlying,
                    spread=spread,
                    contract=option_data['option1']['contract'],
                    side=option_data['option1']['side'],
                    quantity=option_data['option1']['quantity'],
                    strike=option_data['option1']['strike']
                )

                self.filled_order2 = self.create_filled_order(
                    trade_summary=self.trade_summary,
                    underlying=self.underlying,
                    spread=spread,
                    contract=option_data['option2']['contract'],
                    side=option_data['option2']['side'],
                    quantity=option_data['option2']['quantity'],
                    strike=option_data['option2']['strike']
                )

                print 'get filled order using queryset and run spread class...'
                filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

                self.spread = Spread(filled_orders=filled_orders)
                self.spread.name = self.spread.get_name()
                result = self.spread.get_two_leg_options_spread()

                print 'result: %s, expected: %s' % (result, option_data['result'])
                self.assertEqual(result, option_data['result'])

                self.filled_order1.delete()
                self.filled_order2.delete()

    def test_three_leg_options_spread(self):
        """
        Test get 3 legs option spread
        """
        self.spreads = ['BUTTERFLY', '~BUTTERFLY']

        self.four_legs = {
            'BUTTERFLY': [
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 55},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 2, 'strike': 57.5},
                    'option3': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 60},
                    'result': 'SHORT_CALL_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 55},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 57.5},
                    'option3': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 60},
                    'result': 'LONG_CALL_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 55},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 2, 'strike': 57.5},
                    'option3': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 60},
                    'result': 'SHORT_PUT_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 55},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 57.5},
                    'option3': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 60},
                    'result': 'LONG_PUT_BUTTERFLY'
                },
                # broken wing butterfly, skew butterfly
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 42},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 43},
                    'option3': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 45},
                    'result': 'LONG_CALL_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 41},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 2, 'strike': 43},
                    'option3': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 44},
                    'result': 'SHORT_CALL_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 90},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 100},
                    'option3': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 105},
                    'result': 'LONG_PUT_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 95},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 2, 'strike': 100},
                    'option3': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 110},
                    'result': 'SHORT_PUT_BROKEN_WING_BUTTERFLY'
                }
            ],
            '~BUTTERFLY': [
                # unbalance
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 28},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 3, 'strike': 29},
                    'option3': {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 30},
                    'result': 'SHORT_CALL_UNBALANCE_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 1, 'strike': 28},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -3, 'strike': 29},
                    'option3': {'contract': 'CALL', 'side': 'BUY', 'quantity': 2, 'strike': 30},
                    'result': 'LONG_CALL_UNBALANCE_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 68},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 5, 'strike': 70},
                    'option3': {'contract': 'PUT', 'side': 'SELL', 'quantity': -3, 'strike': 72},
                    'result': 'SHORT_PUT_UNBALANCE_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 5, 'strike': 90},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -15, 'strike': 100},
                    'option3': {'contract': 'PUT', 'side': 'BUY', 'quantity': 10, 'strike': 110},
                    'result': 'LONG_PUT_UNBALANCE_BUTTERFLY'
                },
                # unbalance broken wing
                {
                    'option1': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 28},
                    'option2': {'contract': 'CALL', 'side': 'BUY', 'quantity': 3, 'strike': 29},
                    'option3': {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 31},
                    'result': 'SHORT_CALL_UNBALANCE_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'CALL', 'side': 'BUY', 'quantity': 5, 'strike': 50},
                    'option2': {'contract': 'CALL', 'side': 'SELL', 'quantity': -12, 'strike': 60},
                    'option3': {'contract': 'CALL', 'side': 'BUY', 'quantity': 7, 'strike': 75},
                    'result': 'LONG_CALL_UNBALANCE_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'SELL', 'quantity': -3, 'strike': 250},
                    'option2': {'contract': 'PUT', 'side': 'BUY', 'quantity': 7, 'strike': 300},
                    'option3': {'contract': 'PUT', 'side': 'SELL', 'quantity': -4, 'strike': 400},
                    'result': 'SHORT_PUT_UNBALANCE_BROKEN_WING_BUTTERFLY'
                },
                {
                    'option1': {'contract': 'PUT', 'side': 'BUY', 'quantity': 1, 'strike': 10},
                    'option2': {'contract': 'PUT', 'side': 'SELL', 'quantity': -3, 'strike': 11},
                    'option3': {'contract': 'PUT', 'side': 'BUY', 'quantity': 2, 'strike': 13},
                    'result': 'LONG_PUT_UNBALANCE_BROKEN_WING_BUTTERFLY'
                }
            ]
        }

        for spread in self.spreads:
            three_legs = self.four_legs[spread]

            for option_data in three_legs:
                print 'create 3 filled orders using spread: %s...' % spread
                self.filled_order1 = self.create_filled_order(
                    trade_summary=self.trade_summary,
                    underlying=self.underlying,
                    spread=spread,
                    contract=option_data['option1']['contract'],
                    side=option_data['option1']['side'],
                    quantity=option_data['option1']['quantity'],
                    strike=option_data['option1']['strike']
                )

                self.filled_order2 = self.create_filled_order(
                    trade_summary=self.trade_summary,
                    underlying=self.underlying,
                    spread=spread,
                    contract=option_data['option2']['contract'],
                    side=option_data['option2']['side'],
                    quantity=option_data['option2']['quantity'],
                    strike=option_data['option2']['strike']
                )

                self.filled_order3 = self.create_filled_order(
                    trade_summary=self.trade_summary,
                    underlying=self.underlying,
                    spread=spread,
                    contract=option_data['option3']['contract'],
                    side=option_data['option3']['side'],
                    quantity=option_data['option3']['quantity'],
                    strike=option_data['option3']['strike']
                )

                print 'get filled order using queryset and run spread class...'
                filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

                self.spread = Spread(filled_orders=filled_orders)
                self.spread.name = self.spread.get_name()
                result = self.spread.get_three_leg_options_spread()

                print 'result: %s, expected: %s' % (result, option_data['result'])
                self.assertEqual(result, option_data['result'])

                self.filled_order1.delete()
                self.filled_order2.delete()
                self.filled_order3.delete()

                print '-' * 80

    def test_four_leg_options_spread(self):
        """
        Test get 4 legs option spread
        """
        self.spreads = ['CONDOR', '~CONDOR', 'IRON CONDOR', '~IRON CONDOR']

        self.four_legs = {
            'CONDOR': [
                # standard
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 82.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 85},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 87.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 90}
                    ],
                    'result': 'LONG_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 82.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 85},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 87.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 90},
                    ],
                    'result': 'SHORT_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +23, 'strike': 40},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -23, 'strike': 30},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -23, 'strike': 20},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +23, 'strike': 10},
                    ],
                    'result': 'LONG_PUT_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -70, 'strike': 410},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +70, 'strike': 310},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +70, 'strike': 210},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -70, 'strike': 110},
                    ],
                    'result': 'SHORT_PUT_CONDOR'
                },
                # broken wing
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 82.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 85},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 87.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 92.5},
                    ],
                    'result': 'LONG_BROKEN_WING_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 72.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 67.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 55},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 52.5},
                    ],
                    'result': 'SHORT_BROKEN_WING_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +22, 'strike': 40},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -22, 'strike': 35},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -22, 'strike': 20},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +22, 'strike': 10},
                    ],
                    'result': 'LONG_BROKEN_WING_PUT_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -89, 'strike': 8},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +89, 'strike': 9},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +89, 'strike': 10},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -89, 'strike': 12},
                    ],
                    'result': 'SHORT_BROKEN_WING_PUT_CONDOR'
                },
            ],
            '~CONDOR': [
                # unbalance
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +2, 'strike': 70},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -2, 'strike': 67.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 55},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 52.5}
                    ],
                    'result': 'LONG_UNBALANCE_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 67.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 70},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -18, 'strike': 52.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +18, 'strike': 55}
                    ],
                    'result': 'SHORT_UNBALANCE_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +23, 'strike': 40},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -23, 'strike': 30},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -22, 'strike': 20},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +22, 'strike': 10},
                    ],
                    'result': 'LONG_UNBALANCE_PUT_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -89, 'strike': 12},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +89, 'strike': 11},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +79, 'strike': 10},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -79, 'strike': 9},
                    ],
                    'result': 'SHORT_UNBALANCE_PUT_CONDOR'
                },
                # broken wing

                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +12, 'strike': 72.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -12, 'strike': 67.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 55},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 52.5},
                    ],
                    'result': 'LONG_UNBALANCE_BROKEN_WING_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -3, 'strike': 70},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +3, 'strike': 67.5},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +4, 'strike': 52.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -4, 'strike': 57.5},
                    ],
                    'result': 'SHORT_UNBALANCE_BROKEN_WING_CALL_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +89, 'strike': 12},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -89, 'strike': 11},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -95, 'strike': 10},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +95, 'strike': 8},

                    ],
                    'result': 'LONG_UNBALANCE_BROKEN_WING_PUT_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -55, 'strike': 40},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +55, 'strike': 35},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +21, 'strike': 20},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -21, 'strike': 10}
                    ],
                    'result': 'SHORT_UNBALANCE_BROKEN_WING_PUT_CONDOR'
                },
            ],
            'IRON CONDOR': [
                # standard

                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +14, 'strike': 70},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -14, 'strike': 67.5},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -14, 'strike': 55},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +14, 'strike': 52.5},
                    ],
                    'result': 'LONG_IRON_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 70},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 67.5},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +1, 'strike': 55},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -1, 'strike': 52.5},
                    ],
                    'result': 'SHORT_IRON_CONDOR'
                },
                # broken wing
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +5, 'strike': 16.5},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -5, 'strike': 15.5},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -5, 'strike': 14},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +5, 'strike': 12.5},

                    ],
                    'result': 'LONG_BROKEN_WING_IRON_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -80, 'strike': 220},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +80, 'strike': 210},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +80, 'strike': 190},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -80, 'strike': 170},
                    ],
                    'result': 'SHORT_BROKEN_WING_IRON_CONDOR'
                },
            ],
            '~IRON CONDOR': [
                # unbalance iron condor
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 70},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 67.5},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +2, 'strike': 55},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 52.5},
                    ],
                    'result': 'SHORT_UNBALANCE_IRON_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +3, 'strike': 120},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -3, 'strike': 110},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 90},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +2, 'strike': 80},
                    ],
                    'result': 'LONG_UNBALANCE_IRON_CONDOR'
                },
                # unbalance broken wing iron condor
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -1, 'strike': 70},
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +1, 'strike': 65},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +2, 'strike': 55},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 52.5},
                    ],
                    'result': 'SHORT_UNBALANCE_BROKEN_WING_IRON_CONDOR'
                },
                {
                    'orders': [
                        {'contract': 'CALL', 'side': 'BUY', 'quantity': +3, 'strike': 120},
                        {'contract': 'CALL', 'side': 'SELL', 'quantity': -3, 'strike': 110},
                        {'contract': 'PUT', 'side': 'SELL', 'quantity': -2, 'strike': 90},
                        {'contract': 'PUT', 'side': 'BUY', 'quantity': +2, 'strike': 70},
                    ],
                    'result': 'LONG_UNBALANCE_BROKEN_WING_IRON_CONDOR'
                },
            ]
        }

        for spread in self.spreads:
            four_legs = self.four_legs[spread]

            for sample_data in four_legs:
                print 'create 4 filled orders using spread: %s...' % spread

                orders = list()
                for order in sample_data['orders']:
                    orders.append(
                        self.create_filled_order(
                            trade_summary=self.trade_summary,
                            underlying=self.underlying,
                            spread=spread,
                            contract=order['contract'],
                            side=order['side'],
                            quantity=order['quantity'],
                            strike=order['strike']
                        )
                    
                    )

                print 'get filled order using queryset and run spread class...'
                filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

                self.spread = Spread(filled_orders=filled_orders)
                self.spread.name = self.spread.get_name()
                result = self.spread.get_four_leg_options_spread()

                print 'result: %s, expected: %s' % (result, sample_data['result'])
                self.assertEqual(result, sample_data['result'])

                for order in orders:
                    order.delete()
                    
                print '-' * 80

    def test_get_spread_module(self):
        """
        Test get spread module name using get_spread result
        """
        self.filled_order = self.create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            future=self.future,
            forex=self.forex,
            spread='STOCK',
            contract='ETF',
            side='BUY',
            quantity=1
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.spread = Spread(filled_orders=filled_orders)

        self.spreads = [
            'SHORT_FUTURE', 'SHORT_CALL_BACKRATIO', 'LONG_PUT_VERTICAL',
            'SHORT_PUT_UNBALANCE_BUTTERFLY', 'LONG_BROKEN_WING_CALL_CONDOR'
        ]
        self.results = [
            'ShortFuture', 'ShortCallBackratio', 'LongPutVertical',
            'ShortPutUnbalanceButterfly', 'LongBrokenWingCallCondor'
        ]

        for spread, expect in zip(self.spreads, self.results):
            self.spread.spread = spread

            result = self.spread.get_spread_module()

            print 'spread name: %s' % spread
            print 'result module: %s' % result
            print '.' * 60

            self.assertEqual(result, expect)

    def method_test_get_account(self, side, net_price, expect):
        """
        Test get account method that return credit or debit
        """
        self.filled_order = self.create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side=side,
            net_price=net_price
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)
        self.spread = Spread(filled_orders=filled_orders)

        result = self.spread.get_account()

        print 'side: %s, net_price: %.2f' % (side, net_price)
        print 'result: %s, expect: %s' % (result, expect)
        self.assertEqual(result, expect)

        filled_orders.delete()

    def test_get_account_debit(self):
        """
        Test get account for debit, credit and balance spread
        """
        self.method_test_get_account(side='BUY', net_price=21.55, expect='DEBIT')
        self.method_test_get_account(side='SELL', net_price=-7.36, expect='CREDIT')
        self.method_test_get_account(side='BUY', net_price=0.0, expect='BALANCE')

    def method_test_get_probability(self, spread, expect):
        """
        Test get probability for each type of spread
        """
        self.filled_order = self.create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread=spread,
            contract=spread,
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying)
        self.spread = Spread(filled_orders=filled_orders)

        result = self.spread.get_probability()

        print 'spread: %s' % spread
        print 'result: %s, expect: %s' % (result, expect)
        self.assertDictEqual(result, expect)

        filled_orders.delete()

    def test_get_probability(self):
        """
        Test get probability for stock, future and forex only
        """
        expect = dict(profit=0.5, even=0, loss=0.5, name='EVEN')

        self.method_test_get_probability(spread='EQUITY', expect=expect)
        self.method_test_get_probability(spread='FUTURE', expect=expect)
        self.method_test_get_probability(spread='FOREX', expect=expect)

    # todo: the hard part, unable to do it... skip build spread view


class TestGetSpread(TestUnitSetUpPrepare):
    def test_get_spread(self):
        """
        Test save position using data in db
        can use production database or another database for test
        """
        try:
            statement = Statement.objects.get(date='2015-01-29')
        except ObjectDoesNotExist:
            self.skipTest("Please use 'Unittest' for testing.\n")
            raise ObjectDoesNotExist()

        trade_summary = TradeSummary.objects.filter(statement=statement).first()
        filled_order_manager = FilledOrder.objects.filter(trade_summary=trade_summary)
        underlying_symbols = filled_order_manager.values_list('underlying__symbol', flat=True).distinct()
        underlying_symbols = [symbol for symbol in underlying_symbols if symbol]  # drop none

        print underlying_symbols

        future_symbols = filled_order_manager.values_list('future__symbol', flat=True).distinct()
        future_symbols = [symbol for symbol in future_symbols if symbol]  # drop none

        forex_symbols = filled_order_manager.values_list('forex__symbol', flat=True).distinct()
        forex_symbols = [symbol for symbol in forex_symbols if symbol]  # drop none

        print 'Underlying...'
        for underlying_symbol in underlying_symbols:
            open_filled_orders = filled_order_manager.filter(
                Q(underlying__symbol=underlying_symbol) & Q(pos_effect='TO OPEN')
            )
            if open_filled_orders.exists():
                self.spread = Spread(filled_orders=open_filled_orders)

                self.spread.name = self.spread.get_name()
                print 'Underlying: %s' % self.spread.get_underlying()
                print 'Name: %s' % self.spread.name
                print 'Spread: %s' % self.spread.get_spread()
                print ''

        print '-' * 80 + '\n'

        print 'Future...'
        for future_symbol in future_symbols:
            open_filled_orders = filled_order_manager.filter(
                Q(future__symbol=future_symbol) & Q(pos_effect='TO OPEN')
            )

            if open_filled_orders.exists():
                self.spread = Spread(filled_orders=open_filled_orders)

                self.spread.name = self.spread.get_name()
                print 'Future: %s' % self.spread.get_future()
                print 'Name: %s' % self.spread.name
                print 'Spread: %s' % self.spread.get_spread()
                print ''

        print '-' * 80 + '\n'

        print 'Forex...'
        for forex_symbol in forex_symbols:
            print forex_symbol
            open_filled_orders = filled_order_manager.filter(
                Q(forex__symbol=forex_symbol) & Q(pos_effect='TO OPEN')
            )

            if open_filled_orders.exists():
                self.spread = Spread(filled_orders=open_filled_orders)

                self.spread.name = self.spread.get_name()
                print 'Forex: %s' % self.spread.get_forex()
                print 'Name: %s' % self.spread.name
                print 'Spread: %s' % self.spread.get_spread()
                print ''
