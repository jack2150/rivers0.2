from datetime import datetime
from glob import glob
from pprint import pprint
from django.utils.timezone import utc
from lib.io.open_ta import OpenTA
from lib.test import TestSetUp
from pms_app.ta_app import models
from pms_app.tests import TestReadyStatement
from rivers.settings import FILES


class TestTradeActivity(TestReadyStatement):
    def setUp(self):
        TestReadyStatement.setUp(self)

        self.date = '2014-09-19'
        self.items = [self.date]
        self.trade_activity = models.TradeActivity(
            statement=self.statement,
            date=self.date
        )

        self.cls_var = self.trade_activity
        self.expect_keys = ['statement', 'date']

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


class TestWorkingOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_activity.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)

        self.items = {
            'status': 'WORKING', 'pos_effect': 'AUTO', 'quantity': -100, 'symbol': 'FB',
            'contract': 'STOCK', 'order': 'LMT', 'time_placed': use_dt, 'spread': 'STOCK',
            'expire_date': '', 'strike': 0.0, 'tif': 'GTC', 'mark': 74.5, 'price': 82.0,
            'side': 'SELL'
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.working_order = models.WorkingOrder(
            trade_activity=self.trade_activity,
            underlying=self.underlying
        )
        self.working_order.set_dict(self.items)

        self.cls_var = self.working_order
        self.expect_keys = [
            'status', 'pos_effect', 'price', 'time_placed', 'date', 'mark', 'contract', 'side',
            'spread', 'expire_date', 'strike', 'tif', 'order', 'symbol', 'quantity'
        ]


class TestFilledOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_activity.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'pos_effect': 'AUTO', 'exec_time': use_dt, 'net_price': 1.05, 'symbol': 'GOOG',
            'contract': 'PUT', 'side': 'BUY', 'price': 10.8, 'spread': 'VERTICAL',
            'expire_date': 'SEP 14', 'strike': 582.5, 'order': 'MKT', 'quantity': 1
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.filled_order = models.FilledOrder(
            trade_activity=self.trade_activity,
            underlying=self.underlying
        )
        self.filled_order.set_dict(self.items)

        self.cls_var = self.filled_order
        self.expect_keys = [
            'pos_effect', 'exec_time', 'price', 'date', 'net_price', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'order', 'symbol', 'quantity'
        ]


class TestCancelledOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_activity.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'status': 'CANCELED', 'pos_effect': 'AUTO', 'time_cancelled': use_dt,
            'price': 82.0, 'contract': 'STOCK', 'side': 'SELL', 'symbol': 'FB',
            'spread': 'STOCK', 'expire_date': '', 'strike': 0.0, 'tif': 'DAY',
            'order': 'LMT', 'quantity': -100
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.cancelled_order = models.CancelledOrder(
            trade_activity=self.trade_activity,
            underlying=self.underlying
        )
        self.cancelled_order.set_dict(self.items)

        self.cls_var = self.cancelled_order
        self.expect_keys = [
            'status', 'pos_effect', 'price', 'date', 'time_cancelled', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'tif', 'order', 'symbol', 'quantity'
        ]


class TestRollingStrategy(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_activity.save()

        self.items = {
            'status': 'WAIT TRG', 'right': 100, 'strike_price': 77.5, 'days_begin': 2.0, 'new_expire_date': 'NOV4 14',
            'symbol': 'FB', 'ex_month': 'NOV', 'call_by': 'Strike +1 ATM', 'contract': 'CALL', 'order_price': 'AUTO',
            'ex_year': 14, 'move_to_market_time_start': '11:00:00', 'active_time_start': '08:45:00',
            'active_time_end': '09:00:00', 'side': -1, 'move_to_market_time_end': '14:45:00'
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.rolling_strategy = models.RollingStrategy(
            trade_activity=self.trade_activity,
            underlying=self.underlying
        )
        self.rolling_strategy.set_dict(self.items)

        self.cls_var = self.rolling_strategy
        self.expect_keys = [
            'ex_month', 'days_begin', 'right', 'strike_price', 'move_to_market_time_end',
            'new_expire_date', 'symbol', 'contract', 'strategy', 'call_by', 'status', 'order_price',
            'ex_year', 'date', 'move_to_market_time_start', 'active_time_start', 'side',
            'active_time_end'
        ]


class TestOpenTASaveAll(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.ta_files = glob(FILES['trade_activity'] + '/*.csv')

    def insert_db(self, no, trade_activity, test_model, data_list):
        """
        Save related data into model with pos statement
        :param no: int
        :param trade_activity: TradeActivity
        :param test_model: any models.class
        :param data_list: list of dict
        """
        ids = list()
        for data in data_list:
            # if symbol key exists in data_list
            if 'symbol' in data.keys():
                test_cls = test_model(trade_activity=trade_activity)

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
                test_cls = test_model(trade_activity=trade_activity)
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
        Open TA file data then save all fields into db
        """
        for key, ta_file in enumerate(self.ta_files, start=1):
            print '%d. run filename: %s' % (key, ta_file)
            print 'starting...\n'

            date = ta_file[51:61]
            data = open(ta_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement='None',
                trade_activity=data,
            )
            statement.save()

            trade_activity = models.TradeActivity(
                statement=statement,
                date=date
            )
            trade_activity.save()

            print 'statement id: %d' % statement.id
            print 'trade_activity id: %d' % trade_activity.id

            print 'using open_ta to make dict data...'
            ta_data = OpenTA(data=data).read()

            print 'keys: %s\n' % ta_data.keys()

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.FilledOrder,
                data_list=ta_data['filled_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.CancelledOrder,
                data_list=ta_data['cancelled_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.WorkingOrder,
                data_list=ta_data['working_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.RollingStrategy,
                data_list=ta_data['rolling_strategy']
            )

            print '\n' + '-' * 100


class TestSaveTradeActivity(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.ta_files = glob(FILES['trade_activity'] + '/*.csv')

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, ta_file in enumerate(self.ta_files, start=1):
            print '%d. run filename: %s' % (no, ta_file)
            print 'starting...\n'

            date = ta_file[51:61]
            ta_data = open(ta_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement=ta_data,
                trade_activity='None',
            )
            statement.save()

            save_ta = models.SaveTradeActivity(
                date=date,
                statement=statement,
                file_data=ta_data
            )
            save_ta.save_all()

            print 'Statement count: %d' % models.Statement.objects.count()
            print 'TradeActivity count: %d' % models.TradeActivity.objects.count()
            print 'WorkingOrder count: %d' % models.WorkingOrder.objects.count()
            print 'FilledOrder count: %d' % models.FilledOrder.objects.count()
            print 'CancelledOrder count: %d' % models.CancelledOrder.objects.count()
            print 'RollingStrategy count: %d\n' % models.RollingStrategy.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.TradeActivity.objects.count(), no)
            self.assertGreater(models.WorkingOrder.objects.count(), 0)
            self.assertGreater(models.FilledOrder.objects.count(), 0)
            self.assertGreater(models.CancelledOrder.objects.count(), 0)
            self.assertGreater(models.RollingStrategy.objects.count(), -1)
