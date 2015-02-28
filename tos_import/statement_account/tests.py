from datetime import datetime
from glob import glob
import os
from pprint import pprint
from django.utils.timezone import utc
from tos_import.test_files import *
from tos_import.real_files import real_path
from tos_import.classes.test import TestSetUp
from tos_import.statement_account import models


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

        self.account_summary = models.AccountSummary(
            statement=self.statement,
            date=self.date,
            **self.items
        )

        self.cls_var = self.account_summary
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
        self.account_summary.save()

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
            account_summary=self.account_summary,
            **self.items
        )

        self.cls_var = self.forex_summary

        self.expect_keys = (
            'statement_account', 'cash', 'upl', 'floating',
            'equity', 'margin', 'available_equity', 'risk_level'
        )


class TestOrderHistory(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            underlying=self.underlying
        )
        self.order_history.set_dict(items=self.items)

        self.cls_var = self.order_history

        self.expect_keys = (
            'status', 'pos_effect', 'price', 'time_placed',
            'statement_account', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'tif', 'order', 'symbol',
            'quantity'
        )


class TestTradeHistory(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            underlying=self.underlying
        )
        self.trade_history.set_dict(self.items)

        self.cls_var = self.trade_history

        self.expect_keys = (
            'pos_effect', 'price', 'execute_time', 'statement_account',
            'order_type', 'net_price', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'symbol', 'quantity'
        )


class TestCashBalance(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

        self.items = {
            'description': 'SOLD -1 VERTICAL FXI 100 AUG 14 40/38.5 PUT @.59', 'commissions': -3.0,
            'time': '02:49:35', 'contract': 'TRD', 'ref_no': 798680668, 'amount': 59.0, 'fees': -0.07,
            'balance': 956.94
        }

        self.cash_balance = models.CashBalance(
            account_summary=self.account_summary,
            **self.items
        )

        self.cls_var = self.cash_balance
        self.expect_keys = (
            'ref_no', 'amount', 'balance', 'contract', 'time',
            'commissions', 'fees', 'statement_account', 'description'
        )


class TestProfitLoss(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            underlying=self.underlying
        )
        self.profit_loss.set_dict(self.items)

        self.cls_var = self.profit_loss

        self.expect_keys = (
            'pl_pct', 'description', 'pl_ytd', 'pl_open', 'margin_req',
            'symbol', 'statement_account', 'pl_day', 'mark_value'
        )


class TestHoldingEquities(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            underlying=self.underlying
        )
        self.holding_equity.set_dict(self.items)

        self.cls_var = self.holding_equity
        self.expect_keys = (
            'symbol', 'trade_price', 'description', 'statement_account',
            'quantity', 'mark', 'mark_value'
        )


class TestHoldingOptions(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            underlying=self.underlying
        )
        self.holding_option.set_dict(self.items)

        self.cls_var = self.holding_option
        self.expect_keys = (
            'statement_account', 'contract', 'option_code', 'expire_date', 'strike',
            'symbol', 'trade_price', 'statement_account', 'quantity', 'mark', 'mark_value'
        )


class TestFutureStatement(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

        self.items = {
            'execute_date': '2014-11-13', 'description': 'BOT +1 /YMZ4 @17559.00',
            'commissions': 5.0, 'trade_date': '2014-11-13', 'contract': 'TRD',
            'execute_time': '08:23:06', 'ref_no': 449712262.0,
            'amount': 17559.0, 'fees': 17559.0, 'balance': 24995.52
        }

        self.future_statement = models.FutureStatement(
            account_summary=self.account_summary
        )
        self.future_statement.set_dict(self.items)

        self.cls_var = self.future_statement
        self.expect_keys = [
            'statement_account', 'execute_date', 'execute_time', 'contract',
            'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
        ]


class TestHoldingFuture(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            future=self.future
        )
        self.holding_future.set_dict(self.items)

        self.cls_var = self.holding_future
        self.expect_keys = [
            'statement_account', 'future',
            'quantity', 'mark', 'pl_day', 'trade_price'
        ]


class TestForexStatement(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

        self.items = {
            'amount_usd': -22.4, 'description': 'BOT +10000 USD/JPY @115.755', 'commissions': 0.0,
            'contract': 'TRD', 'ref_no': 450077888.0, 'amount': -2590.0, 'time': '04:13:53',
            'date': '2014-11-14', 'balance': 9973.6
        }

        self.forex_statement = models.ForexStatement(
            account_summary=self.account_summary
        )
        self.forex_statement.set_dict(self.items)

        self.cls_var = self.forex_statement
        self.expect_keys = [
            'ref_no', 'amount', 'balance', 'contract', 'time', 'commissions',
            'amount_usd', 'statement_account', 'description'
        ]


class TestHoldingForex(TestAccountStatement):
    def setUp(self):
        TestAccountStatement.setUp(self)
        self.account_summary.save()

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
            account_summary=self.account_summary,
            forex=self.forex
        )
        self.holding_forex.set_dict(self.items)

        self.cls_var = self.holding_forex
        self.expect_keys = [
            'statement_account', 'forex', 'fpl',
            'quantity', 'mark', 'trade_price'
        ]


# noinspection PyUnresolvedReferences
class TestSaveAccountStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.acc_files = glob(os.path.join(test_acc_path, '*.csv'))

        self.acc_files = self.acc_files + [
            #os.path.join(test_path, '2014-11-19', '2014-11-19-AccountStatement.csv'),
            #os.path.join(test_path, '2014-11-25', '2014-11-25-AccountStatement.csv'),
            os.path.join(real_path, '2015-02-27', '2015-02-28-AccountStatement.csv')
        ]

        self.save_acc = None

    def ready_account_summary(self):
        """
        Test method for ready up account statement
        """
        acc_file = self.acc_files[0]
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

        self.save_acc = models.SaveAccountStatement(
            date=date,
            statement=statement,
            file_data=acc_data
        )

    def test_save_account_summary(self):
        """
        Test save account statement method
        """
        self.ready_account_summary()
        self.save_acc.save_account_summary()

        print 'Statement count: %d' % models.Statement.objects.count()
        print 'AccountStatement count: %d' % models.AccountSummary.objects.count()

        self.assertEqual(models.Statement.objects.count(), 1)
        self.assertEqual(models.AccountSummary.objects.count(), 1)

        pprint(models.AccountSummary.objects.all())

    def test_save_single_with_underlying(self):
        """
        Test save single (only underlying, no future or forex) into class
        """
        self.ready_account_summary()
        self.save_acc.save_account_summary()

        cls_list = [
            models.CashBalance,
            models.ForexStatement,
            models.FutureStatement,
            models.HoldingEquity,
            models.HoldingOption
        ]
        data_list = [
            self.save_acc.cash_balance,
            self.save_acc.forex_statement,
            self.save_acc.future_statement,
            self.save_acc.holding_equity,
            self.save_acc.holding_option,
        ]

        for save_cls, save_data in zip(cls_list, data_list):
            self.save_acc.save_single_with_underlying(
                save_cls=save_cls,
                save_data=save_data
            )

        print 'CashBalance count: %d' % models.CashBalance.objects.count()
        print 'ForexStatement count: %d' % models.ForexStatement.objects.count()
        print 'FutureStatement count: %d' % models.FutureStatement.objects.count()
        print 'HoldingEquity count: %d' % models.HoldingEquity.objects.count()
        print 'HoldingOption count: %d' % models.HoldingOption.objects.count()

        self.assertGreaterEqual(models.CashBalance.objects.count(), 0)
        self.assertGreaterEqual(models.ForexStatement.objects.count(), 0)
        self.assertGreaterEqual(models.FutureStatement.objects.count(), 0)
        self.assertGreaterEqual(models.HoldingEquity.objects.count(), 0)
        self.assertGreaterEqual(models.HoldingOption.objects.count(), 0)

    def test_save_profit_loss(self):
        """
        Test save profit loss into class
        """
        self.ready_account_summary()
        self.save_acc.save_account_summary()

        self.save_acc.save_profit_loss(
            save_data=self.save_acc.profit_loss
        )

        print 'Underlying count: %d' % models.Underlying.objects.count()
        print 'Future count: %d' % models.Future.objects.count()
        print 'ProfitLoss count: %d' % models.ProfitLoss.objects.count()

        self.assertGreaterEqual(models.Underlying.objects.count(), 1)
        self.assertGreaterEqual(models.Future.objects.count(), 1)
        self.assertGreaterEqual(models.ProfitLoss.objects.count(), 1)

        for future in models.Future.objects.all():
            pprint(future.json(), width=300)

    def test_save_holding_forex(self):
        """
        Test save holding forex into class
        """
        self.ready_account_summary()
        self.save_acc.save_account_summary()

        self.save_acc.save_holding_forex(
            save_data=self.save_acc.holding_forex
        )

        print 'Forex count: %d' % models.Forex.objects.count()
        print 'HoldingForex count: %d' % models.HoldingForex.objects.count()

        self.assertGreaterEqual(models.Forex.objects.count(), 1)
        self.assertGreaterEqual(models.HoldingForex.objects.count(), 1)

    def test_save_holding_future(self):
        """
        Test save holding future into class
        """
        self.ready_account_summary()
        self.save_acc.save_account_summary()

        self.save_acc.save_holding_future(
            save_data=self.save_acc.holding_future
        )

        print 'Future count: %d' % models.Future.objects.count()
        print 'HoldingFuture count: %d' % models.HoldingFuture.objects.count()

        self.assertGreaterEqual(models.Future.objects.count(), 1)
        self.assertGreaterEqual(models.HoldingFuture.objects.count(), 1)

    def test_save_history(self):
        """
        Test save order history or trade history with
        underlying or future or forex foreign key
        """
        self.ready_account_summary()

        self.save_acc.save_account_summary()

        self.save_acc.save_history(
            save_cls=models.OrderHistory,
            save_data=self.save_acc.order_history
        )

        self.save_acc.save_history(
            save_cls=models.TradeHistory,
            save_data=self.save_acc.trade_history
        )

        print 'Underlying count: %d' % models.Underlying.objects.count()
        print 'Future count: %d' % models.Future.objects.count()
        print 'Forex count: %d' % models.Forex.objects.count()
        print 'OrderHistory count: %d' % models.OrderHistory.objects.count()
        print 'OrderHistory count: %d' % models.TradeHistory.objects.count()

        self.assertGreaterEqual(models.Underlying.objects.count(), 1)
        self.assertGreaterEqual(models.Future.objects.count(), 1)
        self.assertGreaterEqual(models.Forex.objects.count(), 1)
        self.assertGreaterEqual(models.OrderHistory.objects.count(), 1)
        self.assertGreaterEqual(models.TradeHistory.objects.count(), 1)

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
            print 'AccountStatement count: %d' % models.AccountSummary.objects.count()
            print 'ForexSummary count: %d' % models.ForexSummary.objects.count()
            print 'ForexStatement count: %d' % models.ForexStatement.objects.count()
            print 'FutureStatement count: %d' % models.FutureStatement.objects.count()

            print 'HoldingEquity count: %d' % models.HoldingEquity.objects.count()
            print 'HoldingOption count: %d' % models.HoldingOption.objects.count()

            print 'Underlying count: %d' % models.Underlying.objects.count()
            print 'Future count: %d' % models.Future.objects.count()
            print 'HoldingFuture count: %d' % models.HoldingFuture.objects.count()
            print 'Forex count: %d' % models.Forex.objects.count()
            print 'HoldingForex count: %d' % models.HoldingForex.objects.count()

            print 'ProfitLoss count: %d' % models.ProfitLoss.objects.count()
            print 'OrderHistory count: %d' % models.OrderHistory.objects.count()
            print 'TradeHistory count: %d' % models.TradeHistory.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.AccountSummary.objects.count(), no)
            self.assertGreaterEqual(models.ForexSummary.objects.count(), 0)
            self.assertGreaterEqual(models.ForexStatement.objects.count(), 0)
            self.assertGreaterEqual(models.FutureStatement.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingEquity.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingOption.objects.count(), 0)

            self.assertGreaterEqual(models.Underlying.objects.count(), 0)
            self.assertGreaterEqual(models.Future.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingFuture.objects.count(), 0)
            self.assertGreaterEqual(models.Forex.objects.count(), 0)
            self.assertGreaterEqual(models.HoldingForex.objects.count(), 0)
            self.assertGreaterEqual(models.ProfitLoss.objects.count(), 0)
            self.assertGreaterEqual(models.OrderHistory.objects.count(), 0)
            self.assertGreaterEqual(models.TradeHistory.objects.count(), 0)

            print '\n' + '-' * 100 + '\n'
