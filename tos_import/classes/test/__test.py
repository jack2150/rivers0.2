from datetime import datetime
import glob
import os
from pprint import pprint

from django.test import TestCase

from tos_import.classes.io.open_pos import OpenPos
from tos_import.files.real_files import real_path
from tos_import.models import Statement
from tos_import.statement.statement_account.models import SaveAccountStatement
from tos_import.statement.statement_position import models
from tos_import.statement.statement_position.models import SavePositionStatement
from tos_import.statement.statement_trade.models import SaveTradeActivity


class TestSetUp(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'


class TestReadyUp(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        self.identify = None

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'

        del self.identify

    def ready_fname(self, date, path):
        """
        Insert positions and overall into db then start testing
        """
        positions, overall = OpenPos(path).read()

        # save position statement
        position_statement = models.PositionSummary(date=date, **overall)
        position_statement.save()

        for position in positions:
            # save positions
            pos = models.Underlying(
                position_statement=position_statement,
                symbol=position['Symbol'],
                company=position['Company']
            )
            pos.save()

            # save instrument
            instrument = models.PositionInstrument()
            instrument.set_dict(position['Instrument'])
            instrument.underlying = pos
            instrument.save()

            # save stock
            stock = models.PositionEquity()
            stock.set_dict(position['Stock'])
            stock.underlying = pos
            stock.save()

            # save options
            for pos_option in position['Options']:
                option = models.PositionOption()
                option.set_dict(pos_option)
                option.underlying = pos
                option.save()

    def ready_all(self, key=None):
        """
        Ready specific files or all files for testing
        """
        test_fname = [
            '2014-03-07-closed.csv',
            '2014-03-10-stock.csv',
            '2014-03-11-hedge.csv',
            '2014-03-12-one-leg.csv',
            '2014-03-13-two-legs.csv',
            '2014-03-14-three-legs.csv',
            '2014-03-17-four-legs-part-1.csv'
        ]

        if key is not None:
            test_fname = [test_fname[key]]

        for fname in test_fname:
            date = fname[:10]
            path = os.path.join(FILES['position_statement'], 'tests', fname)
            self.ready_fname(date=date, path=path)

        position_statement_count = models.PositionSummary.objects.count()
        position_count = models.Underlying.objects.count()


        print 'position statement count: %d and position count: %d\n' \
              % (position_statement_count, position_count)


class TestReadyFile(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

    @classmethod
    def ready_real_file(cls, path, real_date, file_date):
        """
        Prepare data by import file into database
        :param path: str 'real_path or test_path'
        :param real_date: str 'date format 2014-02-27'
        :param file_date: str 'date format 2014-02-28'
        """
        acc_data = open(os.path.join(
            path, real_date, '%s-AccountStatement.csv' % file_date)
        ).read()
        pos_data = open(os.path.join(
            path, real_date, '%s-PositionStatement.csv' % file_date)
        ).read()
        ta_data = open(os.path.join(
            path, real_date, '%s-TradeActivity.csv' % file_date)
        ).read()

        statement = Statement()
        statement.date = real_date
        statement.account_statement = acc_data
        statement.position_statement = pos_data
        statement.trade_activity = ta_data
        statement.save()

        SaveAccountStatement(
            date=file_date,
            statement=statement,
            file_data=acc_data
        ).save_all()

        SavePositionStatement(
            date=file_date,
            statement=statement,
            file_data=pos_data
        ).save_all()

        SaveTradeActivity(
            date=file_date,
            statement=statement,
            file_data=ta_data
        ).save_all()

    @classmethod
    def ready_all_real_files(cls):
        """
        Import all real files in real files folder
        """
        real_files_folder = glob.glob('%s/*' % real_path)

        error_file_folders = list()
        for folder in real_files_folder:
            if os.path.isdir(folder):
                real_date = os.path.basename(folder)

                try:
                    datetime.strptime(real_date, '%Y-%m-%d')
                except ValueError:
                    error_file_folders.append(
                        {
                            'path': folder,
                            'error': real_date.split(' ')[1]
                        }
                    )
                else:
                    # only import error free folder
                    # get file inside and get date
                    statement = glob.glob('%s/*.csv' % folder)[0]
                    file_date = os.path.basename(statement)[0:10]

                    TestReadyFile.ready_real_file(
                        path=real_path,
                        real_date=real_date,
                        file_date=file_date
                    )






































