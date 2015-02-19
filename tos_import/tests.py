from rivers import urls
from django.contrib.auth.models import User
from tos_import.test_files import *
from tos_import.classes.test import TestSetUp
from tos_import.admin import *
from tos_import.statement_account.models import *
from tos_import.statement_position.models import *
from tos_import.statement_trade.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from pprint import pprint


class TestSetUpUnderlying(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.underlying = Underlying(
            symbol='SPX',
            company='S&P 500 Index'
        )
        self.underlying.save()


class TestUnderlying(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.underlying = Underlying(
            symbol='SPX',
            company='S&P 500 Index'
        )

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.underlying.save()

        print 'Underlying saved!'
        print 'underlying id: %d' % self.underlying.id

        self.assertTrue(self.underlying.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'Underlying in normal: %s' % self.underlying
        print 'Underlying in json: %s\n' % self.underlying.json()

        json = eval(self.underlying.json())

        print 'convert into dict:'
        pprint(json)

        for key in json.keys():
            self.assertIn(key, ('symbol', 'company'))


class TestFuture(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.future = Future(
            lookup='ES',
            symbol='SPX',
            description='E-mini S&P 500 Index Futures',
            session='ETH',
            expire_date='DEC 14',
            spc='1/50'
        )

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.future.save()

        print 'Future saved!'
        print 'Future id: %d' % self.future.id

        self.assertTrue(self.future.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'Future in normal: %s' % self.future
        print 'Future in json: %s\n' % self.future.json()

        json = eval(self.future.json())

        print 'convert into dict:'
        pprint(json)

        for key in json.keys():
            self.assertIn(key, (
                'lookup', 'symbol', 'description',
                'session', 'expire_date', 'spc'
            ))


class TestForex(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.forex = Forex(
            symbol='GBP/JPY',
            description='GBPound/Japanese Yen Spot',
        )

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.forex.save()

        print 'Forex saved!'
        print 'Forex id: %d' % self.forex.id

        self.assertTrue(self.forex.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'Forex in normal: %s' % self.forex
        print 'Forex in json: %s\n' % self.forex.json()

        json = eval(self.forex.json())

        print 'convert into dict:'
        pprint(json)

        for key in json.keys():
            self.assertIn(key, (
                'symbol', 'description'
            ))


class TestStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.statement = Statement(
            date='2014-11-14',
            account_statement='account statement data',
            position_statement='position statement data',
            trade_activity='trade activity data'
        )

    def test_save(self):
        """
        Test set dict data into pos
        """
        print 'date: %s' % self.statement.date
        print 'statement_account: %s' % self.statement.account_statement
        print 'position_statement: %s' % self.statement.position_statement
        print 'trade_activity: %s\n' % self.statement.trade_activity

        self.statement.save()

        print 'statement saved!'
        print 'statement id: %d' % self.statement.id

        self.assertTrue(self.statement.id)


class TestSaveAppModel(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.save_app_model = SaveAppModel(
            date='2014-11-14',
            statement=None,
            file_data=''
        )

    def get_methods(self, cls, test_method, data1, data2):
        """
        test method for get underlying, future and forex
        """
        print 'save %s into underlying...' % data1['symbol']
        cls(**data1).save()

        cls_name = cls.__name__

        print 'get existing from db...'
        print 'total %s in db: %d' % (cls_name, cls.objects.count())
        self.assertEqual(cls.objects.count(), 1)
        print 'run get %s with %s...' % (cls_name, data1['symbol'])
        cls_obj = getattr(self.save_app_model, test_method)(**data1)
        self.assertEqual(cls_obj.id, 1)

        print '\n' + 'save new into db...'
        print 'run get %s with %s...' % (cls_name, data2['symbol'])
        cls_obj = getattr(self.save_app_model, test_method)(**data2)
        self.assertEqual(cls_obj.id, 2)
        self.assertEqual(cls.objects.count(), 2)
        print 'total %s in db: %d' % (cls_name, cls.objects.count())
        print cls.objects.all()

    def test_get_underlying(self):
        """
        Test get existing underlying or save new underlying into model
        """
        self.get_methods(
            cls=Underlying,
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
            cls=Future,
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

        future = self.save_app_model.get_future(
            symbol='', lookup='ES'
        )

        self.assertEqual(future.lookup, 'ES')

    def test_get_forex(self):
        """
        Test get existing underlying or save new underlying into model
        """
        self.get_methods(
            cls=Forex,
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


class TestReadyStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.statement = Statement(
            date='2014-11-14',
            account_statement='account statement data',
            position_statement='position statement data',
            trade_activity='trade activity data'
        )
        self.statement.save()


class TestPmsImportStatementsForm(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-11-14'
        self.account_statement = SimpleUploadedFile('2014-11-15-AccountStatement.csv', 'something')
        self.position_statement = SimpleUploadedFile('2014-11-15-PositionStatement.csv', 'something')
        self.trade_activity = SimpleUploadedFile('2014-11-15-TradeActivity.csv', 'something')

        self.value_data = dict(
            date=self.date
        )

        self.file_data = dict(
            account_statement=self.account_statement,
            position_statement=self.position_statement,
            trade_activity=self.trade_activity
        )

    def test_is_valid(self):
        """
        Test import form is valid working fine
        """
        self.pms_form = PmsImportStatementsForm(self.value_data, self.file_data)

        print 'file_date: %s' % self.date
        print 'account statement file: %s' % self.account_statement
        print 'position statement file: %s' % self.position_statement
        print 'trade activity file: %s\n' % self.trade_activity

        print 'running form is_valid...'
        result = self.pms_form.is_valid()
        print 'is_valid result: %s' % result
        print self.pms_form.errors

    def test_clean_for_same_date(self):
        """
        Test clean method when form is validate for
        make sure file date and all statement filename is same
        which is less than 1 biz day of file date
        """
        wrong_date = '2014-07-20'
        print 'using wrong file date: %s' % wrong_date
        self.pms_form = PmsImportStatementsForm({'date': wrong_date}, self.file_data)

        print 'run is_valid()...\n'
        result = self.pms_form.is_valid()

        print 'result: %s' % result
        self.assertFalse(result)

        errors = self.pms_form.errors.as_text()
        self.assertIn('All date must have (-1 BDay', errors)

        print 'errors text:'
        print errors

    def validate_file_field_empty_upload(self, fname):
        print 'test with empty file upload'
        self.pms_form = PmsImportStatementsForm({}, {})
        print 'without setup %s file' % fname
        print 'run is_valid()...'
        self.pms_form.is_valid()

        self.assertTrue(self.pms_form.errors[fname])
        print '%s error: %s\n' % (fname, self.pms_form.errors[fname].as_text())

        print '-' * 80 + '\n'

    def validate_file_field_correct_upload(self, fname):
        print 'test with correct file upload'
        self.pms_form = PmsImportStatementsForm({}, {fname: getattr(self, fname)})
        print '%s file: %s' % (fname, getattr(self, fname))
        print 'run is_valid()...'

        self.assertFalse(fname in self.pms_form.errors.keys())
        print 'without any %s error...\n' % fname

        print '-' * 80 + '\n'

    def validate_file_field_with_invalid_filename(self, fname, head_text, wrong_fname, error_message):
        """
        Test method for different type of filename
        :param fname: str
        :param head_text: str
        :param wrong_fname: str
        """
        print head_text
        self.pms_form = PmsImportStatementsForm(
            {}, {fname: SimpleUploadedFile(wrong_fname, 'something')}
        )
        print 'without setup %s file' % wrong_fname
        print 'run is_valid()...'
        self.pms_form.is_valid()

        self.assertTrue(self.pms_form.errors[fname])
        print '%s error: %s\n' % (fname, self.pms_form.errors[fname].as_text())

        self.assertIn(error_message, self.pms_form.errors[fname].as_text())

        print '-' * 80 + '\n'

    def validate_file_field_wrong_filename(self, fname):
        """
        Test file field with wrong filename
        :param fname: str filename
        """
        wrong_fname = getattr(self, fname).name.replace(
            ''.join(map(lambda x: x.capitalize(), fname.split('_'))), 'wrong-filename'
        )

        self.validate_file_field_with_invalid_filename(
            fname,
            'test with wrong filename',
            wrong_fname,
            'Incorrect filename'
        )

    def validate_file_field_wrong_file_date(self, fname):
        """
        Test file field with wrong file date
        :param fname: str filename
        """
        wrong_fname = getattr(self, fname).name.replace(
            '2014-11-15', '11-15-2014'
        )

        self.validate_file_field_with_invalid_filename(
            fname,
            'test with wrong file date...',
            wrong_fname,
            'Incorrect file date'
        )

    def validate_file_field_wrong_file_ext(self, fname):
        """
        Test file field with wrong file extension
        :param fname: str filename
        """
        wrong_fname = getattr(self, fname).name.replace(
            'csv', 'html'
        )

        self.validate_file_field_with_invalid_filename(
            fname,
            'test with wrong file ext...',
            wrong_fname,
            'Incorrect file extension'
        )

    def test_validate_account_statement(self):
        """
        Test validate account statement file upload field is working
        """
        self.validate_file_field_empty_upload('account_statement')
        self.validate_file_field_correct_upload('account_statement')
        self.validate_file_field_wrong_filename('account_statement')
        self.validate_file_field_wrong_file_date('account_statement')
        self.validate_file_field_wrong_file_ext('account_statement')

    def test_validate_position_statement(self):
        """
        Test validate position statement file upload field is working
        """
        self.validate_file_field_empty_upload('position_statement')
        self.validate_file_field_correct_upload('position_statement')
        self.validate_file_field_wrong_filename('position_statement')
        self.validate_file_field_wrong_file_date('position_statement')
        self.validate_file_field_wrong_file_ext('position_statement')

    def test_validate_trade_activity(self):
        """
        Test validate trade activity file upload field is working
        """
        self.validate_file_field_empty_upload('trade_activity')
        self.validate_file_field_correct_upload('trade_activity')
        self.validate_file_field_wrong_filename('trade_activity')
        self.validate_file_field_wrong_file_date('trade_activity')
        self.validate_file_field_wrong_file_ext('trade_activity')


# noinspection PyUnresolvedReferences
class TestPmsImportStatementView(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.user = User.objects.create_superuser(
            username='jack',
            email='a@b.com',
            password='pass'
        )

        self.date = '2014-11-14'

        self.account_statement = SimpleUploadedFile(
            '2014-11-15-AccountStatement.csv',
            open(os.path.join(test_path, '2014-11-15', '2014-11-15-AccountStatement.csv')).read()
        )
        self.position_statement = SimpleUploadedFile(
            '2014-11-15-PositionStatement.csv',
            open(os.path.join(test_path, '2014-11-15', '2014-11-15-PositionStatement.csv')).read()
        )
        self.trade_activity = SimpleUploadedFile(
            '2014-11-15-TradeActivity.csv',
            open(os.path.join(test_path, '2014-11-15', '2014-11-15-TradeActivity.csv')).read()
        )

    def test_submit_import_statement_form(self):
        """
        Test open import statement url and set post data then upload files
        :return: None
        """
        print 'login as superuser...'
        self.client.login(username='jack', password='pass')

        print 'submit import statements form with post data...'
        response = self.client.post(
            path=reverse('admin:statement_import'),
            data=dict(
                date=self.date,
                account_statement=self.account_statement,
                position_statement=self.position_statement,
                trade_activity=self.trade_activity
            )
        )

        print 'testing redirect back into import form...'
        self.assertRedirects(
            response,
            reverse('admin:statement_import', kwargs={'statement_id': 1}),
            status_code=302,
            target_status_code=200,
            msg_prefix='',
        )

        print 'check statements is successful insert db...'
        response = self.client.get(response['location'])
        self.assertTrue(response.context['statement_id'])
        self.assertContains(response, 'All statements was inserted successfully.')

        print 'Statement count: %d\n' % Statement.objects.count()

        print 'Underlying count: %d' % Underlying.objects.count()
        print 'Future count: %d' % Future.objects.count()
        print 'Forex count: %d\n' % Forex.objects.count()

        print '-' * 100 + '\n' + 'Account Statement\n' + '-' * 100
        print 'AccountStatement count: %d' % AccountSummary.objects.count()
        print 'ProfitsLosses count: %d' % ProfitLoss.objects.count()
        print 'TradeHistory count: %d' % TradeHistory.objects.count()
        print 'OrderHistory count: %d' % OrderHistory.objects.count()
        print 'Equities count: %d' % HoldingEquity.objects.count()
        print 'Options count: %d' % HoldingOption.objects.count()
        print 'HoldingFuture count: %d' % HoldingFuture.objects.count()
        print 'HoldingForex count: %d' % HoldingForex.objects.count()
        print 'ForexStatement count: %d' % ForexStatement.objects.count()
        print 'FutureStatement count: %d' % FutureStatement.objects.count()
        print 'CashBalance count: %d' % CashBalance.objects.count()

        print '-' * 100 + '\n' + 'Position Statement\n' + '-' * 100
        print 'PositionStatement count: %d' % PositionSummary.objects.count()
        print 'Statement count: %d' % Statement.objects.count()
        print 'PositionStatement count: %d' % PositionSummary.objects.count()
        print 'PositionInstrument count: %d' % PositionInstrument.objects.count()
        print 'PositionEquity count: %d' % PositionEquity.objects.count()
        print 'PositionOption count: %d\n' % PositionOption.objects.count()
        print 'PositionFuture count: %d\n' % PositionFuture.objects.count()
        print 'PositionForex count: %d\n' % PositionForex.objects.count()

        print '-' * 100 + '\n' + 'Trade Activity\n' + '-' * 100
        print 'TradeActivity count: %d' % TradeSummary.objects.count()
        print 'WorkingOrder count: %d' % WorkingOrder.objects.count()
        print 'FilledOrder count: %d' % FilledOrder.objects.count()
        print 'CancelledOrder count: %d' % CancelledOrder.objects.count()
        print 'RollingStrategy count: %d\n' % RollingStrategy.objects.count()
