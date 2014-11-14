from datetime import datetime
from glob import glob
import os
from pprint import pprint
from django.utils.timezone import utc
from app_pms.test_files import *
from app_pms.classes.io.open_acc import OpenAcc
from app_pms.classes.test import TestSetUp
from app_pms.app_acc import models


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


class TestForexSummary(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'available_equity': 9450.07,
            'cash': 10000.0,
            'equity': 10014.39,
            'floating': 40.79,
            'margin': 564.32,
            'risk_level': 100.0,
            'upl': -26.4
        }

        self.forex_summary = models.ForexSummary(
            account_statement=self.account_statement,
            **self.items
        )

        self.cls_var = self.forex_summary

        self.expect_keys = (
            'account_statement', 'cash', 'upl', 'floating',
            'equity', 'margin', 'available_equity', 'risk_level'
        )


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


class TestProfitLoss(TestAccountStatement):
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

        self.profit_loss = models.ProfitLoss(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.profit_loss.set_dict(self.items)

        self.cls_var = self.profit_loss

        self.expect_keys = (
            'pl_pct', 'description', 'pl_ytd', 'pl_open', 'margin_req',
            'symbol', 'account_statement', 'pl_day', 'mark_value'
        )


class TestHoldingEquities(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'description': 'GOLDCORP INC COM', 'quantity': 100, 'symbol': 'GG', 'mark': 19.3099,
            'mark_value': 1930.99, 'trade_price': 23.41
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=self.items['description']
        )
        self.underlying.save()

        self.holding_equity = models.HoldingEquity(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.holding_equity.set_dict(self.items)

        self.cls_var = self.holding_equity
        self.expect_keys = (
            'symbol', 'trade_price', 'description', 'account_statement',
            'quantity', 'mark', 'mark_value'
        )


class TestHoldingOptions(TestAccountStatement):
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

        self.holding_option = models.HoldingOption(
            account_statement=self.account_statement,
            underlying=self.underlying
        )
        self.holding_option.set_dict(self.items)

        self.cls_var = self.holding_option
        self.expect_keys = (
            'account_statement', 'contract', 'option_code', 'expire_date', 'strike',
            'symbol', 'trade_price', 'account_statement', 'quantity', 'mark', 'mark_value'
        )


class TestFutureStatement(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'execute_date': '2014-11-13', 'description': 'BOT +1 /YMZ4 @17559.00',
            'commissions': 5.0, 'trade_date': '2014-11-13', 'contract': 'TRD',
            'execute_time': '08:23:06', 'ref_no': 449712262.0,
            'amount': 17559.0, 'fees': 17559.0, 'balance': 24995.52
        }

        self.future_statement = models.FutureStatement(
            account_statement=self.account_statement
        )
        self.future_statement.set_dict(self.items)

        self.cls_var = self.future_statement
        self.expect_keys = [
            'account_statement', 'execute_date', 'execute_time', 'contract',
            'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
        ]


class TestHoldingFuture(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'description': 'E-mini S&P 500 Index Futures', 'quantity': 1.0, 'symbol': '/ESZ4',
            'mark': 2033.25, 'session': 'ETH', 'lookup': 'ES', 'pl_day': 25.0, 'expire_date': 'DEC 14',
            'spc': '1/50', 'trade_price': 2032.75
        }

        self.future = models.Future(
            lookup=self.items['lookup'],
            symbol=self.items['symbol'],
            description=self.items['description'],
            expire_date=self.items['expire_date'],
            session=self.items['session'],
            spc=self.items['spc']
        )
        self.future.save()

        self.holding_future = models.HoldingFuture(
            account_statement=self.account_statement,
            future=self.future
        )
        self.holding_future.set_dict(self.items)

        self.cls_var = self.holding_future
        self.expect_keys = [
            'account_statement', 'future',
            'quantity', 'mark', 'pl_day', 'trade_price'
        ]


class TestForexStatement(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'amount_usd': -22.4, 'description': 'BOT +10000 USD/JPY @115.755', 'commissions': 0.0,
            'contract': 'TRD', 'ref_no': 450077888.0, 'amount': -2590.0, 'time': '04:13:53',
            'date': '2014-11-14', 'balance': 9973.6
        }

        self.forex_statement = models.ForexStatement(
            account_statement=self.account_statement
        )
        self.forex_statement.set_dict(self.items)

        self.cls_var = self.forex_statement
        self.expect_keys = [
            'ref_no', 'amount', 'balance', 'contract', 'time', 'commissions',
            'amount_usd', 'account_statement', 'description'
        ]


class TestHoldingForex(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_statement.save()

        self.items = {
            'description': 'GBPound/Japanese Yen Spot', 'fpl': -4.41,
            'symbol': 'GBP/JPY', 'mark': 181.895,
            'quantity': 10000.0, 'trade_price': 181.927
        }

        self.forex = models.Forex(
            symbol=self.items['symbol'],
            description=self.items['description']
        )
        self.forex.save()

        print 'forex id: %d' % self.forex.id

        self.holding_forex = models.HoldingForex(
            account_statement=self.account_statement,
            forex=self.forex
        )
        self.holding_forex.set_dict(self.items)

        self.cls_var = self.holding_forex
        self.expect_keys = [
            'account_statement', 'forex', 'fpl',
            'quantity', 'mark', 'trade_price'
        ]


class TestOpenAccSaveAll(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.acc_files = glob(
            r'C:\Users\Jack\Projects\rivers\app_pms\tests\account_statement\*.csv'
        )

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
            if 'symbol' in data.keys() and '/' not in data['symbol']:
                # for stock and option only
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

                #pprint(data)

                test_cls.underlying = underlying
                test_cls.set_dict(data)
                test_cls.save()

            elif 'symbol' in data.keys() and '/' in data['symbol']:
                # for future data
                test_cls = test_model(account_statement=account_statement)

                future_obj = models.Future.objects.filter(symbol=data['symbol'])
                if future_obj.count():
                    future = future_obj.first()
                    print future.id
                else:
                    future = models.Future(
                        lookup=data['lookup'],
                        symbol=data['symbol'],
                        description=data['description'],
                        expire_date=data['expire_date'],
                        session=data['session'],
                        spc=data['spc']
                    )
                    future.save()
                test_cls.future = future
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

        #for saved_cls in test_model.objects.all():
        #    print saved_cls.id, saved_cls, saved_cls.json()

    def test_read_save(self):
        """
        Open Acc file data then save all fields  into db
        """
        for key, acc_file in enumerate(self.acc_files, start=1):
            print '%d. run filename: %s' % (key, acc_file)
            print 'starting...\n'

            #date = acc_file[54:64]
            date = os.path.basename(acc_file)[0:10]
            print 'Date: %s' % date

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
                test_model=models.ProfitLoss,
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
                test_model=models.HoldingEquity,
                data_list=acc_data['equities']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.HoldingOption,
                data_list=acc_data['options']
            )

            print acc_data['futures']
            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.HoldingFuture,
                data_list=acc_data['futures']
            )

            self.insert_db(
                no=key,
                account_statement=account_statement,
                test_model=models.ForexStatement,
                data_list=acc_data['forex']
            )

            print '\n' + '-' * 100

        print 'underlying count: %d' % models.Underlying.objects.count()


class TestSaveAccountStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.acc_files = glob(os.path.join(test_acc_path, '*.csv'))

    def get_methods(self, cls, test_method, data1, data2):
        """
        test method for get underlying, future and forex
        """
        print 'save %s into underlying...' % data1['symbol']
        cls(**data1).save()

        save_acc = models.SaveAccountStatement(
            date='2014-11-01', statement=None, file_data=''
        )

        cls_name = cls.__name__

        print 'get existing from db...'
        print 'total %s in db: %d' % (cls_name, cls.objects.count())
        self.assertEqual(cls.objects.count(), 1)
        print 'run get %s with %s...' % (cls_name, data1['symbol'])
        cls_obj = getattr(save_acc, test_method)(**data1)
        self.assertEqual(cls_obj.id, 1)

        print '\n' + 'save new into db...'
        print 'run get %s with %s...' % (cls_name, data2['symbol'])
        cls_obj = getattr(save_acc, test_method)(**data2)
        self.assertEqual(cls_obj.id, 2)
        self.assertEqual(cls.objects.count(), 2)
        print 'total %s in db: %d' % (cls_name, cls.objects.count())
        print cls.objects.all()

    def test_get_underlying(self):
        """
        Test get existing underlying or save new underlying into model
        """
        self.get_methods(
            cls=models.Underlying,
            test_method='get_underlying',
            data1=dict(
                symbol='AAPL',
                company='APPLE INC COM'
            ),
            data2=dict(
                symbol='BAC',
                company='BANK OF AMERICA CORP COM'
            )
        )

    def test_get_future(self):
        """
        Test get future from db or save new db into db
        """
        self.get_methods(
            cls=models.Future,
            test_method='get_future',
            data1=dict(
                lookup='ES',
                symbol='/ESZ4',
                description='E-mini S&P 500 Index Futures',
                expire_date='DEC 14',
                session='ETH',
                spc='1/50'
            ),
            data2=dict(
                lookup='YG',
                symbol='/YGZ4',
                description='Mini Gold Futures',
                expire_date='DEC 14',
                session='ICUS',
                spc='1/33.2'
            )
        )

    def test_get_forex(self):
        """
        Test get existing underlying or save new underlying into model
        """
        self.get_methods(
            cls=models.Forex,
            test_method='get_forex',
            data1=dict(
                symbol='EUR/USD',
                description='Euro/USDollar Spot'
            ),
            data2=dict(
                symbol='GBP/JPY',
                description='GBPound/Japanese Yen Spot'
            )
        )

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, acc_file in enumerate(self.acc_files, start=1):
            print '%d. run filename: %s' % (no, acc_file)
            print 'starting...\n'

            date = os.path.basename(acc_file)[0:10]
            print 'Date: %s' % date

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
            print 'ForexSummary count: %d' % models.ForexSummary.objects.count()
            print 'ForexStatement count: %d' % models.ForexStatement.objects.count()
            print 'FutureStatement count: %d' % models.FutureStatement.objects.count()

            print 'HoldingEquity count: %d' % models.HoldingEquity.objects.count()
            print 'HoldingOption count: %d' % models.HoldingOption.objects.count()

            print 'Future count: %d' % models.Future.objects.count()
            print 'HoldingFuture count: %d' % models.HoldingFuture.objects.count()
            print 'Forex count: %d' % models.Forex.objects.count()
            print 'HoldingForex count: %d' % models.HoldingForex.objects.count()

            print 'ProfitLoss count: %d' % models.ProfitLoss.objects.count()

            #print 'ProfitsLosses count: %d' % models.ProfitLoss.objects.count()
            #print 'TradeHistory count: %d' % models.TradeHistory.objects.count()
            #print 'OrderHistory count: %d' % models.OrderHistory.objects.count()
            #print 'Equities count: %d' % models.HoldingEquity.objects.count()
            #print 'Options count: %d' % models.HoldingOption.objects.count()
            #print 'CashBalance count: %d' % models.CashBalance.objects.count()
            #print 'Futures count: %d' % models.Future.objects.count()
            #print 'Holding Futures count: %d' % models.HoldingFuture.objects.count()
            #print 'Forex count: %d\n' % models.ForexStatement.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.AccountStatement.objects.count(), no)
            self.assertGreaterEqual(models.ForexSummary.objects.count(), 0)
            self.assertGreaterEqual(models.ForexStatement.objects.count(), 0)
            self.assertGreaterEqual(models.FutureStatement.objects.count(), 0)

            self.assertGreaterEqual(models.HoldingEquity.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingOption.objects.count(), 0)

            self.assertGreaterEqual(models.Future.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingFuture.objects.count(), 0)
            self.assertGreaterEqual(models.Forex.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingForex.objects.count(), 0)
            self.assertGreaterEqual(models.ProfitLoss.objects.count(), 0)

            #
            #self.assertGreaterEqual(models.TradeHistory.objects.count(), 0)
            #self.assertGreaterEqual(models.OrderHistory.objects.count(), 0)
            #self.assertGreaterEqual(models.HoldingEquity.objects.count(), 0)
            #self.assertGreaterEqual(models.HoldingOption.objects.count(), 0)
            #self.assertGreaterEqual(models.CashBalance.objects.count(), 0)
            #self.assertGreaterEqual(models.Future.objects.count(), 0)
            #self.assertGreaterEqual(models.HoldingFuture.objects.count(), 0)
            #self.assertGreaterEqual(models.ForexStatement.objects.count(), 0)