import os
from pprint import pprint

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from statistic.simple.stat_day.models import *
from tos_import.classes.tests import TestSetUp
from tos_import.files.test_files import test_path


class TestBaseModelListing(TestSetUp):
    def ready_file(self, real_date, file_date):
        if not User.objects.exists():
            User.objects.create_superuser(
                username='jack',
                email='a@b.com',
                password='pass'
            )

        self.date = real_date

        self.account_statement_file = SimpleUploadedFile(
            '%s-AccountStatement.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-AccountStatement.csv' % file_date)).read()
        )
        self.position_statement_file = SimpleUploadedFile(
            '%s-PositionStatement.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-PositionStatement.csv' % file_date)).read()
        )
        self.trade_activity_file = SimpleUploadedFile(
            '%s-TradeActivity.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-TradeActivity.csv' % file_date)).read()
        )

        self.client.login(username='jack', password='pass')

        self.client.post(
            path=reverse('admin:statement_import'),
            data=dict(
                date=self.date,
                account_statement=self.account_statement_file,
                position_statement=self.position_statement_file,
                trade_activity=self.trade_activity_file
            )
        )

    def test_base_models_view(self):
        """
        Test list all admin models
        """
        self.ready_file(real_date='2014-11-17', file_date='2014-11-18')
        self.ready_file(real_date='2014-11-18', file_date='2014-11-19')

        print 'Statement count: %d' % Statement.objects.count()
        print 'DayStat object count: %d' % StatDay.objects.count()
        print 'DayStatHolding object count: %d' % StatDayHolding.objects.count()
        print 'DayStatOptionGreek object count: %d' % StatDayOptionGreek.objects.count()

        response = self.client.get(reverse('admin:base_models_view'))

        print 'running url: %s' % reverse('admin:base_models_view')
        print 'response status code: %d\n' % response.status_code

        app_parent_list = response.context['app_parent_list']
        print 'app_parent_list parameters:'
        pprint(app_parent_list, width=100)
        self.assertEqual(type(app_parent_list), list)
        self.assertGreaterEqual(len(app_parent_list), 0)
        expected_key = ['name', 'label', 'child']
        print 'Expected Key: %s' % expected_key
        for app_parent in app_parent_list:
            for key in app_parent.keys():
                self.assertIn(key, expected_key)
        print '\n'

        app_label_list = response.context['app_label_list']
        print 'app_label_list parameters:'
        pprint(app_label_list, width=100)
        self.assertEqual(type(app_label_list), dict)
        self.assertGreaterEqual(len(app_label_list), 0)
        print 'App label Key: %s' % app_label_list.keys()
        print '\n'

        module_list = response.context['module_list']
        print 'module_list parameters:'
        pprint(module_list, width=100)
        self.assertEqual(type(module_list), list)
        self.assertGreaterEqual(len(module_list), 0)
        expected_key = ['name', 'url', 'app', 'app_label', 'app_parent']
        print 'Expected Key: %s' % expected_key
        for module in module_list:
            for key in module.keys():
                self.assertIn(key, expected_key)
        print '\n'






