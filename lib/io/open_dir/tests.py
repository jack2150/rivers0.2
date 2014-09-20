import os
from django.test import TestCase
from lib.io.open_dir import OpenDir


#noinspection PyPep8Naming
from rivers.settings import FILES


class TestOpenDir(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        self.open_dir = OpenDir()

        self.path = os.path.join(FILES['position_statement'], '2014-08-01-PositionStatement.csv')

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'

        del self.open_dir, self.path

    def test_get_files_from_folder(self):
        """
        Test open folder then get a list of files
        """
        files = self.open_dir.get_files_from_folder()

        print 'folder: %s' % self.open_dir.folder

        for k, f in enumerate(files):
            print k, f
            self.assertIn('PositionStatement.csv', f)
            self.assertIn('position_statement', f)

    def test_get_date_from_fpath(self):
        """
        Test get date from file path
        """
        date = self.open_dir.get_date_from_fpath(path=self.path)

        print 'path: %s' % self.path
        print 'date: %s' % date

        self.assertEqual(date.count('-'), 2)

    def test_make_dict(self):
        """
        Test make dict from file path
        """
        file_dict = self.open_dir.make_dict(path=self.path)

        print 'dict date: %s' % file_dict['Date']
        print 'dict path: %s' % file_dict['Path']

    def test_get_fname_from_path(self):
        """
        Test get file name from file path
        """
        fname = self.open_dir.get_fname_from_path(path=self.path)

        print 'fname: %s' % fname

    def test_to_list(self):
        """
        open dir primary method get files inside tos.pos folder
        """
        print 'import dir: \n%s \n' % self.open_dir.folder

        files = self.open_dir.to_list()

        print 'files inside dir:'
        for f in files:
            print 'Date: %s, Path: %s' % (f['Date'], f['Path'])

            self.assertIn('PositionStatement.csv', f['Path'])

    def test_to_json(self):
        """
        convert open dir property files into json format and ready for use
        """
        print 'json format:'
        json_str = self.open_dir.to_json()

        for json in json_str[1:-1].split(','):
            print json

        self.assertEqual(type(json_str), str)

    def test_get_path(self):
        """
        Test get path using date
        :return:
        """
        dates = [
            '2014-08-01',
            '2013-12-20',
            '2014-08-02'
        ]

        for key, date in enumerate(dates):
            path = self.open_dir.get_path(date)

            print 'date: %s' % date
            print 'path: %s\n' % path

            if key == 1:
                self.assertEqual(date, '2013-12-20')
                self.assertFalse(path)
            else:
                self.assertIn(date, path)
                self.assertIn('.csv', path)
                self.assertEqual(type(path), str)
