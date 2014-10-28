from lib.test import TestSetUp
from pms_app import models, admin
from django.core.files.uploadedfile import SimpleUploadedFile
from pprint import pprint


class TestSetUpUnderlying(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.underlying = models.Underlying(
            symbol='SPX',
            company='S&P 500 Index'
        )
        self.underlying.save()


class TestUnderlying(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.underlying = models.Underlying(
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


class TestStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.statement = models.Statement(
            date='2014-10-21',
            account_statement='account statement data',
            position_statement='position statement data',
            trade_activity='trade activity data'
        )

    def test_save(self):
        """
        Test set dict data into pos
        """
        print 'date: %s' % self.statement.date
        print 'account_statement: %s' % self.statement.account_statement
        print 'position_statement: %s' % self.statement.position_statement
        print 'trade_activity: %s\n' % self.statement.trade_activity

        self.statement.save()

        print 'statement saved!'
        print 'statement id: %d' % self.statement.id

        self.assertTrue(self.statement.id)


class TestPmsImportStatementsForm(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-10-21'
        self.account_statement = SimpleUploadedFile('2014-10-22-AccountStatement.csv', 'something')
        self.position_statement = SimpleUploadedFile('2014-10-22-PositionStatement.csv', 'something')
        self.trade_activity = SimpleUploadedFile('2014-10-22-TradeActivity.csv', 'something')

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
        self.pms_form = admin.PmsImportStatementsForm(self.value_data, self.file_data)

        print 'file_date: %s' % self.date
        print 'account statement file: %s' % self.account_statement
        print 'position statement file: %s' % self.position_statement
        print 'trade activity file: %s\n' % self.trade_activity

        print 'running form is_valid...'
        result = self.pms_form.is_valid()
        print 'is_valid result: %s' % result
        #self.assertTrue(result)
        print self.pms_form.errors

    def test_clean_for_same_date(self):
        """
        Test clean method when form is validate for
        make sure file date and all statement filename is same
        which is less than 1 biz day of file date
        """
        wrong_date = '2014-07-20'
        print 'using wrong file date: %s' % wrong_date
        self.pms_form = admin.PmsImportStatementsForm({'date': wrong_date}, self.file_data)

        print 'run is_valid()...\n'
        result = self.pms_form.is_valid()

        print 'result: %s' % result
        self.assertFalse(result)

        errors = self.pms_form.errors.as_text()
        self.assertIn(
            'All statement files must have (-1 biz day) as file date',
            errors
        )

        print 'errors text:'
        print errors

    def validate_file_field_empty_upload(self, fname):
        print 'test with empty file upload'
        self.pms_form = admin.PmsImportStatementsForm({}, {})
        print 'without setup %s file' % fname
        print 'run is_valid()...'
        self.pms_form.is_valid()

        self.assertTrue(self.pms_form.errors[fname])
        print '%s error: %s\n' % (fname, self.pms_form.errors[fname].as_text())

        print '-' * 80 + '\n'

    def validate_file_field_correct_upload(self, fname):
        print 'test with correct file upload'
        self.pms_form = admin.PmsImportStatementsForm({}, {fname: getattr(self, fname)})
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
        self.pms_form = admin.PmsImportStatementsForm(
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
            '2014-10-22', '10-22-2014'
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


class TestPmsImportStatementView(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)
