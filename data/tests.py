from tos_import.classes.tests import TestSaveModel, TestSetUpDB
from calendar import month_name
from datetime import datetime
from glob import glob
import os
from pprint import pprint
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from data.classes import OpenThinkBack
from data.views import THINKBACK_DIR
from data.models import *
from tos_import.classes.tests import TestSetUp


class TestStock(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        self.symbol = 'IBM'

        self.items = {'high': 99.99, 'last': 99.64, 'volume': 6097146.0, 'low': 98.89,
                      'date': '2015-04-02', 'open': 99.44, 'net_change': 0.49}

        self.test_cls = Stock()
        self.test_cls.symbol = self.symbol
        self.test_cls.source = 'tos_thinkback'

        self.test_cls.data = self.items

        self.expect_keys = ['date', 'volume', 'open', 'high', 'low']

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()
        print 'close: %s' % self.test_cls.close
        print 'symbol: %s' % self.test_cls.symbol
        print 'source: %s' % self.test_cls.source


class TestOptionContract(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        self.items = {'ex_month': 'APR1', 'ex_year': 15, 'option_code': 'JNJ150402C85',
                      'right': 100, 'side': 'CALL', 'special': 'Weeklys', 'strike': '85'}

        self.test_cls = OptionContract(
            symbol='IBM',
            source='tos_thinkback',
            **self.items
        )

        self.expect_keys = [
            'ex_month', 'ex_year', 'right', 'special', 'strike', 'side', 'option_code'
        ]

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()
        print 'source: %s' % self.test_cls.source


class TestOption(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        option_contract = {'ex_month': 'APR1', 'ex_year': 15, 'option_code': 'JNJ150402C92',
                           'right': 100, 'side': 'CALL', 'special': 'Weeklys', 'strike': '92'}

        self.option_contract = OptionContract(
            symbol='IBM',
            source='tos_thinkback',
            **option_contract
        )
        self.option_contract.save()

        self.items = {'ask': 7.9, 'bid': 7.55, 'date': '2015-04-02', 'delta': 0.96, 'dte': 0,
                      'extrinsic': 0.085, 'gamma': 0.02, 'impl_vol': 90.16, 'intrinsic': 7.64,
                      'open_int': 20.0, 'prob_itm': 95.23, 'prob_otm': 4.77, 'prob_touch': 9.45,
                      'theo_price': 0.0, 'theta': -0.22, 'vega': 0.0, 'volume': 0.0}

        self.test_cls = Option(
            option_contract=self.option_contract,
            **self.items
        )

        self.expect_keys = [
            'date', 'dte',
            'bid', 'ask', 'delta', 'gamma', 'theta', 'vega',
            'theo_price', 'impl_vol', 'prob_itm', 'prob_otm', 'prob_touch', 'volume',
            'open_int', 'intrinsic', 'extrinsic'
        ]

    def tearDown(self):
        TestSaveModel.tearDown(self)

        OptionContract.objects.all().delete()

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()

        print 'contract: %s' % self.test_cls.option_contract

    def test_set_data_dict(self):
        """
        Test set raw data dict into model then save
        auto create foreign key option_contract and set it
        """
        self.items = {'mark': 14.75, 'last': 14.85, 'ask': 14.9, 'bid': 14.55, 'date': '2015-04-02',
                      'delta': 0.97, 'dte': 0, 'extrinsic': 0.085, 'gamma': 0.01, 'impl_vol': 159.66,
                      'intrinsic': 14.64, 'open_int': 0.0, 'prob_itm': 96.86, 'prob_otm': 3.14,
                      'prob_touch': 6.18, 'theo_price': 0.0, 'theta': -0.25, 'vega': 0.0,
                      'volume': 0.0}

        self.test_cls = Option(
            option_contract=self.option_contract
        )

        self.test_cls.data = self.items
        self.method_test_save()

        print 'contract: %s' % self.test_cls.option_contract


class TestGetPrice(TestSetUpDB):
    def setUp(self):
        TestSetUpDB.setUp(self)

        self.symbol = 'IBM'
        self.date = '2015-04-02'
        self.source = 'tos_thinkback'

        self.items = {'high': 99.99, 'last': 99.64, 'volume': 6097146.0, 'low': 98.89,
                      'date': self.date, 'open': 99.44, 'net_change': 0.49}

        self.stock = Stock()
        self.stock.symbol = self.symbol
        self.stock.source = self.source
        self.stock.data = self.items
        self.stock.save()

        print Stock.objects.count()

    def test_get_price(self):
        """
        Test get price from stocks
        :return:
        """
        stock_price = get_price(symbol=self.symbol, date=self.date, source=self.source)

        print 'symbol: %s, date: %s, source: %s' % (self.symbol, self.date, self.source)
        print 'result: %s' % stock_price

        print '.' * 60

        self.source = 'google'
        stock_price = get_price(symbol=self.symbol, date=self.date, source=self.source)

        print 'symbol: %s, date: %s, source: %s' % (self.symbol, self.date, self.source)
        print 'result: %s' % stock_price

        print '.' * 60

        self.source = 'yahoo'
        stock_price = get_price(symbol=self.symbol, date=self.date, source=self.source)

        print 'symbol: %s, date: %s, source: %s' % (self.symbol, self.date, self.source)
        print 'result: %s' % stock_price


class TestOpenThinkBack(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.symbol = 'WFC'
        self.year = '2015'
        self.date = '2015-01-30'
        self.test_path = list()
        for path in glob(os.path.join(THINKBACK_DIR, '*')):
            if os.path.isdir(path):
                self.test_path.append(path)

        self.test_dir = [path for path in self.test_path if self.symbol.lower() in path].pop()

        # single test file
        self.test_file = r'D:\rivers\data' \
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
        #self.client.login()

        response = self.client.get(
            reverse('admin:data_tos_thinkback_import_view', args=('gild',))
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
        # self.assertGreater(stocks.count(), 0)
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
    def setUp(self):
        TestSetUp.setUp(self)

        self.symbol = 'IBM'
        self.date = '2015-04-02'
        self.source = 'tos_thinkback'

        self.items = {'high': 99.99, 'last': 99.64, 'volume': 6097146.0, 'low': 98.89,
                      'date': self.date, 'open': 99.44, 'net_change': 0.49}

        self.stock = Stock()
        self.stock.symbol = self.symbol
        self.stock.source = self.source
        self.stock.data = self.items
        self.stock.save()

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
            reverse('admin:data_select_symbol_view')
        )

        csv_symbols = response.context['csv_symbols']
        web_symbols = response.context['web_symbols']
        self.assertEqual(type(csv_symbols), list)
        self.assertEqual(type(web_symbols), list)

        print 'csv symbol list:'
        pprint(csv_symbols, width=300)

        print '.' * 60

        print 'web symbol list:'
        pprint(web_symbols, width=300)

        print 'other is all ajax...'


class TestDataWebImportView(TestSetUpDB):
    def setUp(self):
        TestSetUpDB.setUp(self)

        # create user
        User.objects.create_superuser(
            username='jack',
            email='a@b.com',
            password='pass'
        )

    def tearDown(self):
        TestSetUpDB.tearDown(self)

        # remove user
        User.objects.filter(username='jack').delete()

    def test_view_google_not_exist(self):
        """
        Test web get google data without any google row
        """
        self.client.login(username='jack', password='pass')
        self.client.login()

        test_symbol = 'AAPL'

        stock_first = Stock()
        stock_first.symbol = test_symbol
        stock_first.data = {
            'date': '2015-01-02', 'high': 111.44, 'last': 109.33, 'low': 107.35,
            'net_change': -1.05, 'open': 111.39, 'volume': 53204626.0, 'source': 'tos_thinkback'
        }

        stock_last = Stock()
        stock_last.symbol = test_symbol
        stock_last.data = {
            'date': '2015-01-30', 'high': 120.0, 'last': 117.16, 'low': 116.85,
            'net_change': -1.74, 'open': 118.4, 'volume': 83745461.0, 'source': 'tos_thinkback'
        }

        Stock.objects.bulk_create([stock_first, stock_last])
        print 'existing stocks:'
        for stock in Stock.objects.all():
            print stock.symbol, stock.source, stock.date, stock.close

        self.assertEqual(Stock.objects.count(), 2)

        response = self.client.get(
            reverse('admin:data_web_import_view', args=(test_symbol.upper(),))
        )

        stocks = response.context['stocks']
        self.assertEqual(type(stocks), list)

        stocks = Stock.objects.all()
        # self.assertGreater(stocks.count(), 2)
        print 'stock count: %d' % Stock.objects.count()
        for stock in stocks:
            print stock
        else:
            print '...'
            print '.' * 60

    def test_view_only_google_exist(self):
        """
        Test web get google with existing google row in db
        :return:
        """
        self.client.login(username='jack', password='pass')
        self.client.login()

        test_symbol = 'WFC'

        stock_first = Stock()
        stock_first.symbol = test_symbol
        stock_first.data = {
            'date': '2015-01-02', 'high': 55.19, 'last': 54.7, 'low': 54.1935,
            'net_change': -0.12, 'open': 55.11, 'volume': 11700856.0
        }

        stock_google = Stock()
        stock_google.symbol = test_symbol
        stock_google.data = {
            'date': '2015-01-15', 'high': 51.5354, 'last': 50.72, 'low': 50.46,
            'net_change': -0.53, 'open': 51.21, 'volume': 32144687.0
        }
        stock_google.source = 'google'

        stock_yahoo = Stock()
        stock_yahoo.symbol = test_symbol
        stock_yahoo.data = {
            'date': '2015-01-14', 'high': 51.5354, 'last': 50.72, 'low': 50.46,
            'net_change': -0.53, 'open': 52.21, 'volume': 32144687.0
        }
        stock_yahoo.source = 'yahoo'

        stock_last = Stock()
        stock_last.symbol = test_symbol
        stock_last.data = {
            'date': '2015-01-30', 'high': 52.77, 'last': 51.92, 'low': 51.9,
            'net_change': -0.84, 'open': 52.2, 'volume': 21754793.0
        }

        Stock.objects.bulk_create([stock_first, stock_google, stock_last])
        for stock in Stock.objects.all():
            print stock.symbol, stock.source, stock.date, stock.close

        self.assertEqual(Stock.objects.count(), 45)

        response = self.client.get(
            reverse('admin:data_web_import_view', args=(test_symbol.upper(),))
        )

        stocks = response.context['stocks']
        self.assertEqual(type(stocks), list)

        stocks = Stock.objects.filter(symbol=test_symbol).all()
        self.assertGreater(stocks.count(), 2)

        # exactly 1 google 2015-01-15 date
        self.assertEqual(
            len([stock.date for stock in stocks.filter(source='google')
                 if stock.date.strftime('%Y-%m-%d') == '2015-01-15']), 1
        )

        print 'stock count: %d' % Stock.objects.count()
        for stock in stocks:
            print stock
        else:
            print '...'
            print '.' * 60











