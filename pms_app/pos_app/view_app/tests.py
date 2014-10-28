import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from rivers.settings import FILES
from pms_app.pos_app import models


class TestViews(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        self.file_date = '2014-08-01'
        self.real_date = '2014-07-31'

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'

    def ready_up(self):
        """
        Insert positions and overall into db then start testing
        """
        self.client.get(reverse('pos_import_app_complete', args=(self.file_date,)))
        self.move_csv_back_to_folder()

        pos_count = models.Underlying.objects.count()
        overall_count = models.Overall.objects.count()

        print 'pos count: %d and overall count: %d' % (pos_count, overall_count)

    def move_csv_back_to_folder(self):
        """
        Move saved csv file back into original folder
        """
        fname = '2014-08-01-PositionStatement.csv'
        original_path = os.path.join(FILES['position_statement'], fname)
        completed_path = os.path.join(FILES['position_statement'], 'save', fname)

        # move back into original folder
        if os.path.isfile(completed_path):
            os.rename(completed_path, original_path)

    def test_index(self):
        """
        Test index with or without date that display default views
        """
        self.ready_up()

        response = self.client.get(reverse('pos_view_app_index', args=(self.real_date,)))
        self.assertEqual(response.status_code, 200)

        #print response
        print 'date: %s' % response.context['date']

        self.assertEqual(self.real_date, response.context['date'])
        self.assertEqual(reverse('pos_view_app_index'), response.context['default_path'])

        self.assertIn('date', response.content)
        self.assertIn('overall_url', response.content)
        self.assertIn('positions_url', response.content)

    def test_date_exists(self):
        """
        Test date exists return true if found and false if not
        """
        response = self.client.get(reverse('pos_view_date_exist', args=(self.real_date,)))

        print 'response: %s\n' % response.content
        self.assertEqual(response.content, 'False')

        self.ready_up()
        print 'after inserted positions...\n'

        response = self.client.get(reverse('pos_view_date_exist', args=(self.real_date,)))
        print 'response: %s' % response.content
        self.assertEqual(response.content, 'True')

    def test_webix_js(self):
        """
        Test webix js url return a correct files
        """
        response = self.client.get(reverse('pos_view_webix_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['pos_calendar', 'overall', 'positions', 'ui_body']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_logic_js(self):
        """
        Test logic js url return a correct files
        """
        response = self.client.get(reverse('pos_view_logic_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['changeDate', 'logic']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_overall_json(self):
        """
        Test view return correct overall json format
        :return:
        """
        self.ready_up()

        response = self.client.get(reverse('pos_view_overall_json', args=(self.real_date,)))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/json')

        print response.content + '\n'

        items = ['date', 'cash_sweep', 'pl_ytd', 'futures_bp', 'bp_adjustment', 'available']
        for item in items:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_positions_json(self):
        """
        Test view return correct positions json format
        :return:
        """
        self.ready_up()

        response = self.client.get(reverse('pos_view_positions_json', args=(self.real_date,)))
        self.assertEqual(response.status_code, 200)

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/json')

        positions = eval(response.content)
        print 'after eval type: %s' % type(positions)

        columns = ['mark_change', 'pl_open', 'pl_day', 'delta', 'bp_effect',
                   'name', 'days', 'mark', 'vega', 'theta', 'pct_change', 'quantity',
                   'gamma', 'trade_price']

        for position in positions:
            print 'pos columns length: %d' % len(position)
            print 'data length: %d' % len(position['data'])
            print 'pos columns names:'
            print position.keys()
            print 'pos json response:'
            print position.__str__()[:150] + '...\n'

            for column in columns:
                # check columns for position with data
                self.assertIn(column, position.keys())
                self.assertIn('data', position.keys())

                for data in position['data']:
                    # check columns for stock and options without data
                    self.assertIn(column, data.keys())

            self.assertEqual(len(position), 15)
            self.assertGreater(len(position['data']), 1)

        self.assertEqual('[{', response.content[:2])
        self.assertEqual('}]', response.content[-2:])
