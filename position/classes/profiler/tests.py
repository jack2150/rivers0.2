from position.classes.tests import TestUnitSetUp
from datetime import datetime
from pprint import pprint
from data.holidays import is_holiday
from data.models import Stock
from data.offdays import is_offdays
from profiler import Profiler
from position.models import PositionSet, PositionOpinion
from tos_import.classes.tests import TestSetUpDB
from tos_import.models import Underlying


class TestProfilerLongStock(TestSetUpDB):
    def create_opinion(self, date, position_set, direction, decision='HOLD'):
        """
        Create position opinion
        :param date: str or datetime
        :param direction: str
        :param decision: str
        :return: PositionOpinion
        """
        position_opinion = PositionOpinion()

        position_opinion.position_set = position_set
        position_opinion.date = date
        position_opinion.direction = direction
        position_opinion.decision = decision
        position_opinion.save()

        return position_opinion

    def setUp(self):
        TestSetUpDB.setUp(self)

        # set date
        self.date = '2015-04-28'

        # create underlying
        self.underlying = Underlying(symbol='AAPL', company='APPLE INC')

        # create position set
        self.position_set = PositionSet()
        self.position_set.underlying = self.underlying
        self.position_set.name = 'EQUITY'
        self.position_set.spread = 'LONG_STOCK'
        self.position_set.start_date = datetime.strptime('2015-04-13', '%Y-%m-%d').date()
        self.position_set.stop_date = datetime.strptime('2015-04-28', '%Y-%m-%d').date()
        self.position_set.save()

        # create position opinion
        self.position_opinion = self.create_opinion(
            date=Profiler.move_bday(self.date, 1),
            position_set=self.position_set,
            direction='BULL'
        )

        # create profiler now
        self.profiler = Profiler(
            position_set=self.position_set, date=self.date
        )

    def test_move_bday(self):
        """
        Test next bday that skip holidays and offdays
        """
        print 'using date: %s' % self.date

        for day in [1, -1]:
            print 'run next_bday...'
            next_bday = self.profiler.move_bday(self.date, day)
            """:type: datetime"""

            print 'get result: %s' % next_bday

            self.assertEqual(type(next_bday), datetime)
            self.assertNotEqual(self.date, next_bday)

            self.assertFalse(is_holiday(next_bday))
            self.assertFalse(is_offdays(next_bday))

            print '.' * 60

    def test_create_opinion_button(self):
        """
        Test create opinion button
        """
        print 'run create_opinion_button...'
        opinion_button = self.profiler.create_opinion_button()

        print 'opinion_button:'
        print opinion_button

        self.assertEqual(type(opinion_button), dict)
        self.assertTrue(opinion_button['saved'])
        self.assertEqual(opinion_button['object'].id, self.position_opinion.id)

        print '\n' + '.' * 60 + '\n'
        print 'test false...'
        print '\n' + '.' * 60 + '\n'

        print 'run create_opinion_button...'
        self.profiler = Profiler(self.position_set, date='2015-04-09')
        opinion_button = self.profiler.create_opinion_button()

        self.assertEqual(type(opinion_button), dict)
        self.assertFalse(opinion_button['saved'])

        print 'opinion_button:'
        print opinion_button

    def test_create_position_opinions(self):
        """
        Create position opinions for profiler view
        """
        # create position opinion
        self.position_opinion0 = self.create_opinion(
            date='2015-04-08',
            position_set=self.position_set,
            direction='BULL'
        )
        self.position_opinion1 = self.create_opinion(
            date='2015-04-09',
            position_set=self.position_set,
            direction='BEAR'
        )

        position_opinions = self.profiler.create_position_opinions()

        for position_opinion in position_opinions:
            print 'opinion: %s' % position_opinion
            print 'bull: %s' % position_opinion.bull
            print 'bear: %s' % position_opinion.bear

            print '.' * 60

            self.assertEqual(type(position_opinion.bull['count']), int)
            self.assertGreaterEqual(position_opinion.bull['count'], 0)
            self.assertEqual(type(position_opinion.bull['correct']), int)
            self.assertGreaterEqual(position_opinion.bull['correct'], 0)
            self.assertEqual(type(position_opinion.bull['correct_pct']), float)
            self.assertGreaterEqual(position_opinion.bull['correct_pct'], 0)
            self.assertEqual(type(position_opinion.bull['wrong']), int)
            self.assertGreaterEqual(position_opinion.bull['wrong'], 0)
            self.assertEqual(type(position_opinion.bull['wrong_pct']), float)
            self.assertGreaterEqual(position_opinion.bull['wrong_pct'], 0)

            self.assertEqual(type(position_opinion.bear['count']), int)
            self.assertGreaterEqual(position_opinion.bear['count'], 0)
            self.assertEqual(type(position_opinion.bear['correct']), int)
            self.assertGreaterEqual(position_opinion.bear['correct'], 0)
            self.assertEqual(type(position_opinion.bear['correct_pct']), float)
            self.assertGreaterEqual(position_opinion.bear['correct_pct'], 0)
            self.assertEqual(type(position_opinion.bear['wrong']), int)
            self.assertGreaterEqual(position_opinion.bear['wrong'], 0)
            self.assertEqual(type(position_opinion.bear['wrong_pct']), float)
            self.assertGreaterEqual(position_opinion.bear['wrong_pct'], 0)

    def test_create_position_dates(self):
        """
        Test create position dates
        """
        position_dates = self.profiler.create_position_dates()

        print 'position_dates:'
        pprint(position_dates)

        self.assertEqual(type(position_dates), dict)

        self.assertFalse(position_dates['dte'])
        self.assertFalse(position_dates['expire_date'])
        self.assertEqual(position_dates['pass_bdays'], 12)
        self.assertEqual(position_dates['pass_days'], 16)

        self.assertEqual(position_dates['start_date'],
                         datetime.strptime('2015-04-13', '%Y-%m-%d').date())
        self.assertEqual(position_dates['stop_date'],
                         datetime.strptime('2015-04-28', '%Y-%m-%d').date())


class TestProfiler2(TestUnitSetUp):
    def setUp(self):
        TestUnitSetUp.setUp(self)

        self.position_set = PositionSet.objects.get(id=65)
        self.date = self.position_set.filledorder_set.order_by('trade_summary__date') \
            .last().trade_summary.date.strftime('%Y-%m-%d')

        self.profiler = Profiler(
            position_set=self.position_set, date=self.date
        )

    def test_create_historical_positions(self):
        """
        Test create historical positions
        """
        print 'run create_historical_positions...'
        historical_positions = self.profiler.create_historical_positions()

        self.assertGreaterEqual(len(historical_positions), 1)

        print 'historical_positions:'
        for historical_position in historical_positions:
            print historical_position

            self.assertEqual(type(historical_position), PositionSet)
            self.assertEqual(
                historical_position.underlying.id,
                self.position_set.underlying.id
            )

    def test_set_stocks(self):
        """
        Test set stocks from position_set date
        """
        print 'empty stocks:'
        print self.profiler.stocks

        print 'run set_stocks...'
        self.profiler.set_stocks()

        print 'stocks:'
        for stock in self.profiler.stocks:
            print stock.date, stock
            self.assertEqual(type(stock), Stock)
            self.assertEqual(stock.symbol, self.position_set.underlying.symbol)

        # make sure date is less than 1 bday of start_date
        self.assertEqual(self.profiler.stocks.last().date, self.profiler.position_set.stop_date)
        self.assertNotEqual(self.profiler.stocks.first().date, self.position_set.start_date)
