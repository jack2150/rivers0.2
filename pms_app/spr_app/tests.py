import os
from pprint import pprint
from django.core.urlresolvers import reverse
from lib.test import TestReadyUp
from rivers.settings import FILES


class TestSpreadView(TestReadyUp):
    def setUp(self):
        """
        ready up all variables and test class
        """
        TestReadyUp.setUp(self)

        self.real_date = '2014-08-05'
        self.path = os.path.join(FILES['position_statement'],
                                 '2014-09-06-PositionStatement.csv')

    def ready_spreads(self):
        """
        Ready positions in database before start test
        """
        self.ready_fname(date=self.real_date, path=self.path)

    def test_symbols_json(self):
        """
        Test symbols_ui json make a list of selective json
        """
        self.ready_spreads()

        response = self.client.get(
            reverse('spread_view_symbols_json', args=(self.real_date, ))
        )

        symbols = eval(response.content)
        print symbols

        pprint(symbols, width=60)

        self.assertEqual(type(symbols), list)
        for symbol in symbols:
            self.assertEqual(type(symbol), dict)

            expect_keys = ['id', 'pl_open', 'spread', 'status', 'symbol']
            for key in symbol.keys():
                self.assertIn(key, expect_keys)