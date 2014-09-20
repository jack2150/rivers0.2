from django.test import TestCase
from django.core.urlresolvers import reverse
from rivers.settings import FILES
import pms_app.pos_app.models as pm
import os


class TestViews(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        fname = '2014-08-01-PositionStatement.csv'
        self.original_path = os.path.join(FILES['position_statement'], fname)
        self.completed_path = os.path.join(FILES['position_statement'], 'save', fname)

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'

    def move_csv_back_to_folder(self):
        """
        Move saved csv file back into original folder
        """
        # move back into original folder
        if os.path.isfile(self.completed_path):
            os.rename(self.completed_path, self.original_path)

    def test_index(self):
        """
        Test index page is working fine that
        display all positions csv files in javascript
        """
        response = self.client.get(reverse('pos_import_app_index'))
        self.assertEqual(response.status_code, 200)

        print 'files:'
        print response.context['files'].split('},')[0] + '}'
        print ' ' + response.context['files'].split('},')[1]

        self.assertIn('2014-08-01-PositionStatement.csv', response.context['files'])
        self.assertIn('2014-08-02-PositionStatement.csv', response.context['files'])

    def test_complete(self):
        """
        Test complete page is working fine that
        save all positions into db and response correctly
        """
        self.move_csv_back_to_folder()

        date = '2014-08-01'

        url = reverse('pos_import_app_complete', args=(date,))
        response = self.client.get(url)

        print 'date: %s' % date
        print 'response:'
        print response.content

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/json')

        self.assertEqual(response.status_code, 200)

        positions = pm.Position.objects.all()
        self.assertEqual(positions.count(), 21)
        print 'positions saved: %d' % positions.count()

        instruments = pm.PositionInstrument.objects.all()
        self.assertEqual(instruments.count(), 21)
        print 'instruments saved: %d' % instruments.count()

        stocks = pm.PositionStock.objects.all()
        self.assertEqual(stocks.count(), 21)
        print 'stocks saved: %d' % stocks.count()

        options = pm.PositionOption.objects.all()
        self.assertEqual(options.count(), 43)
        print 'options saved: %d' % options.count()

        overall = pm.Overall.objects.all()
        self.assertEqual(overall.count(), 1)
        print 'overall saved: %d' % overall.count()

        # check saved file is in completed folder
        self.assertTrue(os.path.isfile(self.completed_path))
        print 'file now in: %s' % self.completed_path

        # move back into positions folder
        self.move_csv_back_to_folder()
        self.assertTrue(os.path.isfile(self.original_path))

        # view parameters test
        self.assertIn(date, response.content)
        self.assertIn(date, response.content)

    def test_webix_js(self):
        """
        Test webix js url return a correct files
        """
        response = self.client.get(reverse('pos_import_webix_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['pos_file_header', 'pos_file_tree', 'import_button', 'ui_body']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_logic_js(self):
        """
        Test logic js url return a correct files
        """
        response = self.client.get(reverse('pos_import_logic_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['page', 'complete', 'logic']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_files_json(self):
        """
        Test files json return correct data
        """
        response = self.client.get(reverse('pos_import_files_json'))
        print reverse('pos_import_files_json')

        print 'response:'
        print response.content[:48]
        print response.content[48:].split('},')[0] + '}'
        print ' ' + response.content[48:].split('},')[1]

        print '\n' + 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/json')

        for item in ['id', 'Positions', 'open', 'data', 'value']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

        self.assertIn('2014-08-01-PositionStatement.csv', response.content)
        self.assertIn('2014-08-02-PositionStatement.csv', response.content)

