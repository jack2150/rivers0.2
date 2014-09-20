import os
from django.test import TestCase
from lib.io.open_pos import OpenPos
from pms_app.pos_app.models import Position, PositionInstrument
from pms_app.pos_app.models import PositionStock, PositionOption, Overall
from rivers.settings import FILES


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


class TestSetUpModel(TestSetUp):
    def ready_pos(self):
        """
        Ready up pos object and use as foreign key
        """
        items = {
            'symbol': 'SPX',
            'company': 'SPX',
            'date': '2014-08-01',
        }

        pos = Position(**items)
        pos.save()

        return pos


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

        for position in positions:
            # save positions
            pos = Position(
                symbol=position['Symbol'],
                company=position['Company'],
                date=date
            )
            pos.save()

            # save instrument
            instrument = PositionInstrument()
            instrument.set_dict(position['Instrument'])
            instrument.position = pos
            instrument.save()

            # save stock
            stock = PositionStock()
            stock.set_dict(position['Stock'])
            stock.position = pos
            stock.save()

            # save options
            for pos_option in position['Options']:
                option = PositionOption()
                option.set_dict(pos_option)
                option.position = pos
                option.save()

        pos_overall = Overall(**overall)
        pos_overall.date = date
        pos_overall.save()

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

        pos_count = Position.objects.count()
        overall_count = Overall.objects.count()

        print 'pos count: %d and overall count: %d\n' % (pos_count, overall_count)