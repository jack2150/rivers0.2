import os

from django.test import TestCase

from tos_import.classes.io.open_pos import OpenPos
from tos_import.statement.statement_position import models


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