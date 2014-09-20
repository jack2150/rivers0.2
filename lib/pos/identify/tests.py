from lib.test import TestReadyUp
from lib.pos.identify import Identify
from pms_app.pos_app.models import Position, PositionSet


class TestIdentify(TestReadyUp):
    def is_methods(self, key, attr, expect):
        """
        Use for each test is_strategy
        :param key: int
        :param attr: str
        :param expect: bool
        """
        self.ready_all(key)

        for position in Position.objects.all():
            pos_set = PositionSet(position)

            self.identify = Identify(pos_set)

            method = getattr(self.identify, attr)
            result = method()
            print 'symbol: %s, stock qty: %d, options len: %d, result: %s' \
                  % (position.symbol, self.identify.pos_set.stock.quantity,
                     self.identify.pos_set.options.count(), result)

            self.assertEqual(result, expect)

        Position.objects.all().delete()

        print '\n' + '-' * 100 + '\n'

    def test_is_closed(self):
        """
        Test identity with closed only positions
        """
        self.is_methods(key=0, attr='is_closed', expect=True)
        self.is_methods(key=1, attr='is_closed', expect=False)

    def test_is_stock(self):
        """
        Test identity with stock only positions
        """
        self.is_methods(key=1, attr='is_stock', expect=True)
        self.is_methods(key=0, attr='is_stock', expect=False)

    def test_is_hedge(self):
        """
        Test identity with hedge (stock + options) positions
        """
        self.is_methods(key=2, attr='is_hedge', expect=True)
        self.is_methods(key=0, attr='is_hedge', expect=False)

    def test_is_one_leg(self):
        """
        Test identity with one leg option positions
        """
        self.is_methods(key=3, attr='is_one_leg', expect=True)
        self.is_methods(key=0, attr='is_one_leg', expect=False)

    def test_is_two_legs(self):
        """
        Test identity with two leg options positions
        """
        self.is_methods(key=4, attr='is_two_legs', expect=True)
        self.is_methods(key=0, attr='is_two_legs', expect=False)

    def test_is_three_legs(self):
        """
        Test identity with three leg options positions
        """
        self.is_methods(key=5, attr='is_three_legs', expect=True)
        self.is_methods(key=0, attr='is_three_legs', expect=False)

    def test_is_four_legs(self):
        """
        Test identity with four leg options positions
        """
        self.is_methods(key=6, attr='is_four_legs', expect=True)
        self.is_methods(key=0, attr='is_four_legs', expect=False)

    def test_identify(self):
        """
        Test core method identify
        """
        self.ready_all()

        for position in Position.objects.all():
            pos_set = PositionSet(position)

            self.identify = Identify(pos_set)

            # auto run identify when use spread
            spread = self.identify.spread

            if spread is not None:
                print '%s\n' % spread(pos_set)

            # todo: to be continue... after all more class
