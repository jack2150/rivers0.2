from calendar import month_name
from datetime import datetime
from glob import glob
import os
from pprint import pprint
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from data.file.tos_thinkback.classes import OpenThinkBack
from data.file.tos_thinkback.csv import THINKBACK_DIR
from data.models import Stock, OptionContract, Option
from tos_import.classes.tests import TestSetUp


class TestOpenThinkBack(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.symbol = 'AAPL'
        self.year = '2015'
        self.date = '2015-01-02'
        self.test_path = list()
        for path in glob(os.path.join(THINKBACK_DIR, '*')):
            if os.path.isdir(path):
                self.test_path.append(path)

        self.test_dir = [path for path in self.test_path if self.symbol.lower() in path].pop()

        # single test file
        self.test_file = r'C:\Users\Jack\Projects\rivers\data/file/tos_thinkback' \
                         r'/csv\%s\%s\%s-StockAndOptionQuoteFor%s.csv' % \
                         (self.symbol.lower(), self.year, self.date, self.symbol.upper())

        self.open_thinkback = OpenThinkBack(
            date=self.date,
            data=open(self.test_file).read()
        )

    def test_get_underlying(self):
        """
        Test get underlying stock price in line 5
        """
        expected_keys = ['date', 'volume', 'open', 'high', 'low', 'last', 'net_change']

        print 'run get_stock...'
        stock = self.open_thinkback.get_stock()

        self.assertEqual(type(stock), dict)

        print 'stock dict:'
        pprint(stock)
        for key, value in stock.items():
            self.assertIn(key, expected_keys)

            if key is not 'date':
                self.assertEqual(type(value), float)
            else:
                self.assertEqual(type(value), str)

    def test_get_cycles(self):
        """
        Test get cycles from each option chain head title
        """
        print 'run get_cycles...'
        cycles = self.open_thinkback.get_cycles()

        self.assertEqual(type(cycles), list)

        print 'cycle dict:'
        pprint(cycles, width=400)

        for cycle in cycles:
            self.assertEqual(type(cycle), dict)

            self.assertEqual(len(cycle['data']), 5)
            self.assertEqual(type(cycle['dte']), int)
            self.assertGreaterEqual(cycle['dte'], 0)
            self.assertEqual(type(cycle['line']), str)
            self.assertGreater(cycle['start'], 10)
            self.assertLess(cycle['start'], cycle['stop'])

    def test_get_cycle_options(self):
        """
        Test get cycle options from option chain
        """
        months = [month_name[i + 1][:3].upper() for i in range(12)]

        contract_keys = [
            'ex_month', 'ex_year', 'right', 'special', 'others',
            'strike', 'side', 'option_code'
        ]

        option_keys = [
            'date', 'dte',
            'last', 'mark', 'bid', 'ask', 'delta', 'gamma', 'theta', 'vega',
            'theo_price', 'impl_vol', 'prob_itm', 'prob_otm', 'prob_touch', 'volume',
            'open_int', 'intrinsic', 'extrinsic'
        ]

        print 'run get_cycles...'
        cycles = self.open_thinkback.get_cycles()

        for cycle in cycles[:1]:
            print 'cycle: %s' % cycle['data']
            print 'run get_cycle_option...'
            options = self.open_thinkback.get_cycle_options(cycle)

            for contract, option in options:
                print 'current contract, option code: %s' % contract['option_code']
                pprint(contract, width=400)

                self.assertEqual(type(contract), dict)
                self.assertEqual(sorted(contract.keys()), sorted(contract_keys))
                self.assertEqual(type(contract['others']), str)

                self.assertEqual(type(contract['ex_month']), str)
                self.assertIn(contract['ex_month'][:3], months)
                if len(contract['ex_month']) == 4:
                    self.assertGreater(int(contract['ex_month'][3]), 0)
                    self.assertLessEqual(int(contract['ex_month'][3]), 12)

                self.assertEqual(type(contract['ex_year']), int)
                self.assertGreater(contract['ex_year'], 0)
                self.assertLessEqual(contract['ex_year'], 99)

                self.assertEqual(type(contract['right']), str)  # not int, str

                self.assertEqual(type(contract['side']), str)
                self.assertIn(contract['side'], ['CALL', 'PUT'])

                self.assertEqual(type(contract['special']), str)
                self.assertIn(contract['special'], ['Weeklys', 'Standard', 'Mini'])

                self.assertEqual(type(contract['strike']), float)
                self.assertGreater(contract['strike'], 0)

                self.assertEqual(type(contract['option_code']), str)

                print 'current option:'
                pprint(option, width=400)

                for key in option.keys():
                    self.assertIn(key, option_keys)
                    if key == 'date':
                        self.assertEqual(type(option['date']), str)
                        self.assertTrue(datetime.strptime(option['date'], '%Y-%m-%d'))
                    elif key == 'dte':
                        self.assertEqual(type(option['dte']), int)
                    else:
                        self.assertEqual(type(option[key]), float)

                print '.' * 80

            print '\n' + '*' * 100 + '\n'

    def test_format(self):
        """
        Test format a raw lines data into dict
        """
        stock, option = self.open_thinkback.format()

        print 'stock: %s' % stock
        print 'option: '
        pprint(option, width=400)

    def test_all(self):
        """
        Test all inside a symbol folder (max 2 year, 3 files)
        :return:
        """
        for year_folder in glob(os.path.join(self.test_dir, '*'))[:2]:
            thinkback_files = glob(os.path.join(year_folder, '*.*'))

            for test_file in thinkback_files[:3]:
                date, symbol = os.path.basename(test_file)[:-4].split('-StockAndOptionQuoteFor')

                raw_data = open(test_file).read()

                open_thinkback = OpenThinkBack(date=date, data=raw_data)
                stock, options = open_thinkback.format()

                print 'stock: %s' % stock
                print 'option count: %d' % len(options)
                print '.' * 80

            print '*' * 100


class TestTosThinkbackImportRunView(TestSetUp):
    def test_view(self):
        self.skipTest("Only test when necessary...")

        if not User.objects.exists():
            User.objects.create_superuser(
                username='jack',
                email='a@b.com',
                password='pass'
            )
        self.client.login(username='jack', password='pass')
        self.client.login()

        response = self.client.get(
            reverse('admin:tos_thinkback_import_run_view', args=('wfc',))
        )

        insert_files = response.context['insert_files']
        for insert_file in insert_files:
            self.assertListEqual(sorted(insert_file.keys()),
                                 sorted(['path', 'stock', 'contracts', 'options']))

            print 'stock: %s, contracts: %d, options: %d path: \n %s\n' % (
                insert_file['stock'], insert_file['contracts'],
                insert_file['options'], insert_file['path']
            )
        else:
            print '.' * 80

        stocks = Stock.objects.all()
        #self.assertGreater(stocks.count(), 0)
        print 'stock count: %d' % Stock.objects.count()
        for stock in stocks[:5]:
            print stock
        else:
            print '...'
            print '.' * 60

        option_contracts = OptionContract.objects.all()
        #self.assertGreater(option_contracts.count(), 0)
        print 'option_contract count: %d' % option_contracts.count()

        for option_contract in option_contracts[:3]:
            print option_contract
        else:
            print '...'
            print '.' * 60

        options = Option.objects.all()
        #self.assertGreater(options.count(), 0)
        print 'options count: %d' % options.count()

        for option in options[:5]:
            print option
        else:
            print '...'
            print '.' * 60


class TestTosThinkbackImportSelectView(TestSetUp):
    def test_view(self):
        if not User.objects.exists():
            User.objects.create_superuser(
                username='jack',
                email='a@b.com',
                password='pass'
            )
        self.client.login(username='jack', password='pass')
        self.client.login()

        response = self.client.get(
            reverse('admin:tos_thinkback_import_select_view')
        )

        symbols = response.context['symbols']
        self.assertEqual(type(symbols), list)

        print 'symbol list:'
        pprint(symbols, width=300)

        print 'other is all ajax...'
