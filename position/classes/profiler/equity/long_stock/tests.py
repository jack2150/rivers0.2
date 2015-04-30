import datetime
from decimal import Decimal
from pprint import pprint
from position.classes.tests import TestUnitSetUp
from position.classes.profiler.equity import ProfilerLongStock
from position.models import PositionSet


class TestProfilerLongStock(TestUnitSetUp):
    def setUp(self):
        TestUnitSetUp.setUp(self)

        self.position_set = PositionSet.objects.get(id=65)
        self.date = self.position_set.filledorder_set.order_by('trade_summary__date')\
            .last().trade_summary.date.strftime('%Y-%m-%d')

        self.profiler = ProfilerLongStock(
            position_set=self.position_set, date=self.date
        )

    def test_create_position_info(self):
        """
        Test create profit loss using stock data
        """
        for date in ['2015-04-07', '2015-04-10']:
            print 'using date: %s' % date
            # date is not stop date
            self.date = date
            self.profiler = ProfilerLongStock(self.position_set, self.date)

            print 'run create_position_info...'
            position_info = self.profiler.create_position_info()

            print 'position_info:'
            pprint(position_info)

            self.assertEqual(type(position_info), dict)

            self.assertNotEqual(float(position_info['pl_open']), 0.0)
            self.assertNotEqual(float(position_info['pl_open_pct']), 0.0)
            self.assertNotEqual(float(position_info['pl_day']), 0.0)
            self.assertNotEqual(float(position_info['pl_day_pct']), 0.0)

            if date == '2015-04-07':
                self.assertNotEqual(self.profiler.date, self.profiler.position_set.stop_date)
            elif date == '2015-04-10':
                self.assertEqual(self.profiler.date, self.profiler.position_set.stop_date)

            self.assertEqual(self.profiler.position_set.status, 'CLOSE')

            self.assertIn(
                position_info['stage_id'],
                [s.id for s in self.position_set.positionstage_set.all()]
            )

            self.assertIn(
                position_info['stage'],
                [s.stage_name for s in self.position_set.positionstage_set.all()]
            )

            self.assertEqual(type(position_info['status']), unicode)

            self.assertIn(type(position_info['enter_price']), [Decimal, float])
            self.assertTrue(position_info['enter_price'])
            self.assertIn(type(position_info['exit_price']), [Decimal, float])
            self.assertEqual(type(position_info['quantity']), int)
            self.assertGreater(position_info['quantity'], 0)

            self.assertIn(type(position_info['holding']), [Decimal, float])
            self.assertTrue(position_info['holding'])
            self.assertIn(type(position_info['bp_effect']), [Decimal, float])

            self.assertEqual(type(position_info['date']), datetime.date)

            print '\n' + '.' * 60 + '\n'

    def test_create_position_stocks(self):
        """
        Test create position stocks
        """
        position_stocks = self.profiler.create_position_stocks()

        for position_stock in position_stocks:
            print position_stock['date'], position_stock

            self.assertEqual(len(position_stock.keys()), 21)

            self.assertEqual(type(position_stock['pl_open']), float)
            self.assertEqual(type(position_stock['pl_open_pct']), float)
            self.assertEqual(type(position_stock['pl_day']), float)
            self.assertEqual(type(position_stock['pl_day_pct']), float)

            self.assertGreaterEqual(position_stock['p_open_count'], 0)
            self.assertGreaterEqual(position_stock['p_open_pct'], 0)
            self.assertGreaterEqual(position_stock['l_open_count'], 0)
            self.assertGreaterEqual(position_stock['l_open_pct'], 0)
            self.assertGreaterEqual(position_stock['p_day_count'], 0)
            self.assertGreaterEqual(position_stock['p_day_pct'], 0)
            self.assertGreaterEqual(position_stock['l_day_count'], 0)
            self.assertGreaterEqual(position_stock['l_day_pct'], 0)
