from datetime import datetime
from glob import glob
from pprint import pprint
from django.utils.timezone import utc
from lib.io.open_acc import OpenAcc
from lib.test import TestSetUp
from pms_app.acc_app import models
from rivers.settings import FILES


class TestAccountStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'commissions_ytd': 1575.08,
            'futures_commissions_ytd': 0.0,
            'net_liquid_value': 3693.94,
            'option_buying_power': 2206.94,
            'stock_buying_power': 5063.58
        }

        self.statement = models.Statement(
            date=self.date,
            account_statement='All raw file data keep here...',
            position_statement='None',
            trade_activity='None',
        )
        self.statement.save()

        self.account_statement = models.AccountStatement(
            statement=self.statement,
            date=self.date,
            **self.items
        )

        self.cls_var = self.account_statement
        self.expect_keys = (
            'futures_commissions_ytd',
            'stock_buying_power',
            'commissions_ytd',
            'date',
            'net_liquid_value',
            'option_buying_power'
        )

    def test_save(self):
        """
        Method use for test saving data into db
        """
        if self.cls_var:
            print 'sample date: '
            pprint(self.items)

            self.cls_var.save()

            print '\n' + '%s saved!' % self.cls_var.__class__.__name__
            print '%s id: %d' % (self.cls_var.__class__.__name__, self.cls_var.id)

            self.assertTrue(self.cls_var.id)

    def test_json_output(self):
        """
        Method use for test json output
        """
        if self.cls_var:
            cls_name = self.cls_var.__class__.__name__
            print '%s in normal: %s' % (cls_name, self.cls_var.__unicode__())
            print '%s in json: \n%s\n' % (cls_name, self.cls_var.json())

            json = eval(self.cls_var.json())

            print 'dict:'
            print json.keys()

            print 'convert into dict:'
            pprint(json)

            for key in json.keys():
                self.assertIn(key, self.expect_keys)


class TestOrderHistory(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'status': 'CANCELED', 'pos_effect': 'TO CLOSE', 'price': 0.95, 'contract': 'PUT',
            'side': 'BUY', 'symbol': 'FB', 'time_placed': use_dt, 'spread': 'VERTICAL',
            'expire_date': 'JUL4 14', 'strike': 67.0, 'tif': 'GTC', 'order': 'MKT', 'quantity': 1
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.order_history = models.OrderHistory(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.order_history.set_dict(items=self.items)

        self.cls_var = self.order_history

        self.expect_keys = (
            'status', 'pos_effect', 'price', 'time_placed',
            'account_statement', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'tif', 'order', 'symbol',
            'quantity'
        )


class TestTradeHistory(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        use_dt = datetime(2014, 9, 28, 17, 57, 31, 114000, tzinfo=utc)
        self.items = {
            'pos_effect': 'TO CLOSE', 'order_type': 'LMT', 'net_price': 0.96, 'side': 'SELL',
            'contract': 'CALL', 'symbol': 'USO', 'spread': 'VERTICAL', 'expire_date': 'JUL4 14',
            'execute_time': use_dt, 'strike': 37.5, 'price': 0.57, 'quantity': -3
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.trade_history = models.TradeHistory(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.trade_history.set_dict(self.items)

        self.cls_var = self.trade_history

        self.expect_keys = (
            'pos_effect', 'price', 'execute_time', 'account_statement',
            'order_type', 'net_price', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'symbol', 'quantity'
        )


class TestCashBalance(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'description': 'SOLD -1 VERTICAL FXI 100 AUG 14 40/38.5 PUT @.59', 'commissions': -3.0,
            'time': '02:49:35', 'contract': 'TRD', 'ref_no': 798680668, 'amount': 59.0, 'fees': -0.07,
            'balance': 956.94
        }

        self.cash_balance = models.CashBalance(
            account_statement=self.account_statement,
            **self.items
        )

        self.cls_var = self.cash_balance
        self.expect_keys = (
            'ref_no', 'amount', 'balance', 'contract', 'time',
            'commissions', 'fees', 'account_statement', 'description'
        )


class TestProfitsLosses(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'pl_pct': 0.0, 'description': 'GOLDMAN SACHS GROUP INC COM', 'pl_open': 0.0,
            'margin_req': 0.0, 'symbol': 'GS', 'pl_day': 0.0, 'pl_ytd': -292.0
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=self.items['description']
        )
        self.underlying.save()

        self.profits_losses = models.ProfitsLosses(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.profits_losses.set_dict(self.items)

        self.cls_var = self.profits_losses

        self.expect_keys = (
            'pl_pct', 'description', 'pl_ytd', 'pl_open', 'margin_req',
            'symbol', 'account_statement', 'pl_day'
        )


class TestEquities(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'symbol': 'TZA', 'trade_price': 15.12, 'quantity': 200,
            'description': 'DIREXION SHARES TRUST DAILY SMALL CAP BEAR 3X SHAR'
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=self.items['description']
        )
        self.underlying.save()

        self.equities = models.Equities(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.equities.set_dict(self.items)

        self.cls_var = self.equities
        self.expect_keys = (
            'symbol', 'trade_price', 'description', 'account_statement', 'quantity'
        )


class TestOptions(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'symbol': 'TLT', 'contract': 'PUT', 'option_code': 'TLT140816P113',
            'expire_date': 'AUG 14', 'strike': 113.0, 'trade_price': 0.74, 'quantity': 3
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.options = models.Options(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.options.set_dict(self.items)

        self.cls_var = self.options
        self.expect_keys = (
            'contract', 'option_code', 'expire_date', 'strike', 'symbol',
            'trade_price', 'account_statement', 'quantity'
        )


class TestFutures(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'execute_date': '2014-07-23', 'description': 'Enter Market', 'commissions': 4.95, 'fees': 2.34,
            'contract': 'BUY', 'execute_time': '22:21:27', 'ref_no': 'ABC123456', 'amount': 3130.0,
            'trade_date': '2014-07-23', 'balance': 4000.0
        }

        self.futures = models.Futures(
            account_statement=self.account_statement,
            **self.items
        )

        self.cls_var = self.futures
        self.expect_keys = [
            'description', 'commissions', 'execute_time', 'fees', 'account_statement',
            'execute_date', 'contract', 'ref_no', 'amount', 'trade_date', 'balance'
        ]


class TestForex(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'amount_usd': 0.0, 'description': 'Cash balance at the start of the business day 23.07 CST',
            'commissions': 0.0, 'contract': 'BAL', 'ref_no': 0L, 'amount': 0.0, 'time': '13:00:00',
            'balance': 0.0
        }

        self.forex = models.Forex(
            account_statement=self.account_statement,
            **self.items
        )

        self.cls_var = self.forex
        self.expect_keys = [
            'ref_no', 'amount', 'balance', 'contract', 'time', 'commissions',
            'amount_usd', 'account_statement', 'description'
        ]


class TestOpenAccSaveAll(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.acc_files = glob(FILES['account_statement'] + '/*.csv')

    def insert_db(self, no, account_statement, test_model, data_list):
        """
        Save related data into model with pos statement
        :param no: int
        :param account_statement: TradeActivity
        :param test_model: any models.class
        :param data_list: list of dict
        """
        ids = list()
        for data in data_list:
              # if symbol key exists in data_list
            if 'symbol' in data.keys():
                test_cls = test_model(account_statement=account_statement)

                underlying_obj = models.Underlying.objects.filter(symbol=data['symbol'])
                if underlying_obj.count():
                    underlying = underlying_obj.first()
                else:
                    company = ''
                    if 'description' in data.keys():
                        company = data['description']

                    underlying = models.Underlying(
                        symbol=data['symbol'],
                        company=company
                    )
                    underlying.save()

                test_cls.underlying = underlying
                test_cls.set_dict(data)
                test_cls.save()
            else:
                test_cls = test_model(account_statement=account_statement)
                test_cls.set_dict(data)
                test_cls.save()

            ids.append(test_cls.id)

        print '%d. save %s... ids: %s' % (
            no, test_model.__name__, ids
        )

        for saved_cls in test_model.objects.all():
            print saved_cls.id, saved_cls, saved_cls.json()

    def test_read_save(self):
        """
        Open Acc file data then save all fields into db
        """
        for key, acc_file in enumerate(self.acc_files, start=1):
            print '%d. run filename: %s' % (key, acc_file)
            print 'starting...\n'

            date = acc_file[54:64]
            file_data = open(acc_file).read()

            statement = models.Statement(
                date=date,
                account_statement=file_data,
                position_statement='None',
                trade_activity='None',
            )
            statement.save()

            # open acc
            acc_data = OpenAcc(data=file_data).read()

            # start save acc statement
            account_statement = models.AccountStatement(
                statement=statement,
                date=date,
                **acc_data['summary']
            )
            account_statement.save()

            print 'statement id: %d' % statement.id
            print 'account_statement id: %d' % account_statement.id

            # first, must save profits losses
            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.ProfitsLosses,
                data_list=acc_data['profits_losses']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.OrderHistory,
                data_list=acc_data['order_history']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.TradeHistory,
                data_list=acc_data['trade_history']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.CashBalance,
                data_list=acc_data['cash_balance']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.Equities,
                data_list=acc_data['equities']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.Options,
                data_list=acc_data['options']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.Futures,
                data_list=acc_data['futures']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.Forex,
                data_list=acc_data['forex']
            )

            print '\n' + '-' * 100

        print 'underlying count: %d' % models.Underlying.objects.count()


class TestSaveAccountStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.acc_files = glob(FILES['account_statement'] + '/*.csv')

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, acc_file in enumerate(self.acc_files, start=1):
            print '%d. run filename: %s' % (no, acc_file)
            print 'starting...\n'

            date = acc_file[54:64]
            acc_data = open(acc_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement=acc_data,
                trade_activity='None',
            )
            statement.save()

            save_acc = models.SaveAccountStatement(
                date=date,
                statement=statement,
                file_data=acc_data
            )
            save_acc.save_all()

            print 'Statement count: %d' % models.Statement.objects.count()
            print 'AccountStatement count: %d' % models.AccountStatement.objects.count()
            print 'ProfitsLosses count: %d' % models.ProfitsLosses.objects.count()
            print 'TradeHistory count: %d' % models.TradeHistory.objects.count()
            print 'OrderHistory count: %d' % models.OrderHistory.objects.count()
            print 'Equities count: %d' % models.Equities.objects.count()
            print 'Options count: %d' % models.Options.objects.count()
            print 'CashBalance count: %d' % models.CashBalance.objects.count()
            print 'Futures count: %d' % models.Futures.objects.count()
            print 'Forex count: %d\n' % models.Forex.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.AccountStatement.objects.count(), no)
            self.assertGreater(models.ProfitsLosses.objects.count(), 0)
            self.assertGreater(models.TradeHistory.objects.count(), 0)
            self.assertGreater(models.Equities.objects.count(), 0)
            self.assertGreater(models.Options.objects.count(), 0)
            self.assertGreater(models.Options.objects.count(), 0)
            self.assertGreater(models.CashBalance.objects.count(), 0)
            self.assertGreater(models.Futures.objects.count(), 0)
            self.assertGreater(models.Futures.objects.count(), 0)

