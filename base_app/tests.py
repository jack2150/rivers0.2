from lib.test import TestSetUp
from django.core.urlresolvers import reverse


class TestViews(TestSetUp):
    def test_index(self):
        """
        Not yet!!!
        """
        pass

    def test_logic_js(self):
        """
        Test logic js url return a correct files
        """
        response = self.client.get(reverse('base_logic_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['menu_init']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)

    def test_webix_js(self):
        """
        Test webix js url return a correct files
        """
        response = self.client.get(reverse('base_webix_js'))

        print 'content-type: %s\n' % response['Content-Type']
        self.assertEqual(response['Content-Type'], 'application/javascript')

        for item in ['menu_links']:
            print '"%s" var found!' % item
            self.assertIn(item, response.content)
