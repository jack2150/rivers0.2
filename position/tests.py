# noinspection PyUnresolvedReferences
import position.classes.ready_django
from django.db.models import Q
from pprint import pprint
from position.models import *
from tos_import.classes.tests import TestSetUpDB, TestReadyFile
from tos_import.files.real_files import real_path
from tos_import.models import Statement
from tos_import.statement.statement_account.models import AccountSummary, ProfitLoss
from tos_import.statement.statement_position.models import PositionSummary, PositionInstrument
from tos_import.statement.statement_trade.models import FilledOrder


class TestContext(TestSetUpDB):
    def setUp(self):
        TestSetUpDB.setUp(self)

        self.prices = [12.5, 20.7, 33.94, 8.71, 114.81]
        self.conditions = ['>', '<', '==', '<=', '>=']
        self.amounts = [139.00, 2267.49, 339.47, 71.66, 10088.83]
        self.limits = [True, False, True, True, False]

        self.cls = None

    def test_save(self):
        if self.cls:
            for key in range(5):
                if self.cls in [MaxProfit, MaxLoss]:
                    items = dict(
                        price=self.prices[key],
                        condition=self.conditions[key],
                        limit=self.limits[key],
                        amount=self.amounts[key]
                    )
                else:
                    items = dict(
                        price=self.prices[key],
                        condition=self.conditions[key]
                    )

                test_cls = self.cls(**items)
                test_cls.save()
                print '%s saved...' % self.cls.__name__

                self.assertTrue(test_cls.id)
                self.assertEqual(test_cls.price, self.prices[key])
                self.assertEqual(test_cls.condition, self.conditions[key])

                print test_cls.__unicode__() + '\n'


class TestBreakEven(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.cls = BreakEven


class TestStartProfit(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.cls = StartProfit


class TestStartLoss(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.cls = StartLoss


class TestMaxProfit(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.cls = MaxProfit


class TestMaxLoss(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.cls = MaxLoss


class TestPositionPL(TestContext):
    def setUp(self):
        TestContext.setUp(self)

        self.items = list()

    def ready_context(self):
        for key in range(5):
            break_even = BreakEven(
                price=self.prices[key],
                condition=self.conditions[key]
            )
            break_even.save()

            start_profit = StartProfit(
                price=self.prices[key],
                condition=self.conditions[key]
            )
            start_profit.save()

            start_loss = StartLoss(
                price=self.prices[key],
                condition=self.conditions[key]
            )
            start_loss.save()

            max_profit = MaxProfit(
                price=self.prices[key],
                condition=self.conditions[key],
                limit=self.limits[key],
                amount=self.amounts[key]
            )
            max_profit.save()

            max_loss = MaxLoss(
                price=self.prices[key],
                condition=self.conditions[key],
                limit=self.limits[key],
                amount=self.amounts[key]
            )
            max_loss.save()

            self.items.append(dict(
                break_even=break_even,
                start_profit=start_profit,
                start_loss=start_loss,
                max_profit=max_profit,
                max_loss=max_loss,
            ))


class TestPositionContext(TestPositionPL):
    def test_save(self):
        self.ready_context()

        for item in self.items:
            print 'item:'
            pprint(item)
            print ''

            position_context = PositionContext(
                break_even=item['break_even'],
                start_profit=item['start_profit'],
                start_loss=item['start_loss'],
                max_profit=item['max_profit'],
                max_loss=item['max_loss']
            )
            position_context.save()

            print 'saved object:'
            print position_context
            self.assertTrue(position_context.id)

            self.assertEqual(type(position_context.break_even), BreakEven)
            self.assertEqual(type(position_context.start_profit), StartProfit)
            self.assertEqual(type(position_context.start_loss), StartLoss)
            self.assertEqual(type(position_context.max_profit), MaxProfit)
            self.assertEqual(type(position_context.max_loss), MaxLoss)

            print '\n'


class TestPositionContexts(TestPositionPL):
    def test_save(self):
        self.ready_context()

        for item1, item2 in zip(self.items[0::2], self.items[1::2]):
            print 'item:'
            pprint(item1)
            pprint(item2)
            print ''

            position_context1 = PositionContext(
                break_even=item1['break_even'],
                start_profit=item1['start_profit'],
                start_loss=item1['start_loss'],
                max_profit=item1['max_profit'],
                max_loss=item1['max_loss']
            )
            position_context1.save()

            position_context2 = PositionContext(
                break_even=item2['break_even'],
                start_profit=item2['start_profit'],
                start_loss=item2['start_loss'],
                max_profit=item2['max_profit'],
                max_loss=item2['max_loss']
            )
            position_context2.save()

            position_contexts = PositionContexts(
                left=position_context1,
                right=position_context2,
            )
            position_contexts.save()

            print 'saved object:'
            print position_contexts.left.__unicode__()
            print position_contexts.right.__unicode__()
            self.assertTrue(position_context1.id)

            self.assertEqual(type(position_context1.break_even), BreakEven)
            self.assertEqual(type(position_context1.start_profit), StartProfit)
            self.assertEqual(type(position_context1.start_loss), StartLoss)
            self.assertEqual(type(position_context1.max_profit), MaxProfit)
            self.assertEqual(type(position_context1.max_loss), MaxLoss)

            print '\n'


class TestPositionSet(TestPositionPL, TestReadyFile):
    def setUp(self):
        TestPositionPL.setUp(self)

        self.ready_context()

        self.position_context = PositionContext(
            break_even=self.items[0]['break_even'],
            start_profit=self.items[1]['start_profit'],
            start_loss=self.items[2]['start_loss'],
            max_profit=self.items[3]['max_profit'],
            max_loss=self.items[4]['max_loss']
        )
        self.position_context.save()

        self.names = ['EQUITY', 'OPTION', 'SPREAD', 'FUTURE', 'FOREX']
        self.spreads = ['LONG STOCK', 'LONG PUT', 'BULL CALL VERTICAL', 'NGQ3', 'USD/CAD']

        self.real_date = '2015-01-29'
        self.file_date = '2015-01-30'

        TestReadyFile.ready_real_file(
            path=real_path,
            real_date=self.real_date,
            file_date=self.file_date
        )

        self.assertTrue(Statement.objects.exists())

        self.name = ''
        self.spread = ''

        # select use filled order
        for filled_oder in FilledOrder.objects.all():
            if filled_oder.spread == 'STOCK':
                self.filled_order = filled_oder
        else:
            self.underlying = self.filled_order.underlying
            self.name = 'EQUITY'
            self.spread = 'LONG_STOCK'  # try save only, without identify

            # get instrument and profit loss
            self.statement = self.filled_order.trade_summary.statement

            account_summary = AccountSummary.objects.filter(statement=self.statement)
            position_summary = PositionSummary.objects.filter(statement=self.statement)

            self.position_instrument = PositionInstrument.objects.filter(
                Q(position_summary=position_summary) & Q(underlying=self.underlying)
            ).first()

            self.profit_loss = ProfitLoss.objects.filter(
                Q(account_summary=account_summary) & Q(underlying=self.underlying)
            ).first()

        print 'ready all items:'
        print 'underlying: %s' % self.underlying.symbol
        print 'name: %s' % self.name
        print 'spread: %s' % self.spread
        print self.position_instrument
        print self.profit_loss
        print ''

    def test_save(self):
        """
        Test save position set with all data into table...
        """
        position_set = PositionSet(
            underlying=self.underlying,
            name=self.name,
            spread=self.spread,
            context=self.position_context
        )
        position_set.save()
        self.assertTrue(position_set.id)
        self.assertEqual(PositionSet.objects.count(), 1)

        print 'run save...\n'
        print position_set
        print position_set.context

        self.filled_order.position_set = position_set
        self.filled_order.save()

        self.position_instrument.position_set = position_set
        self.position_instrument.save()

        self.profit_loss.position_set = position_set
        self.profit_loss.save()

        self.assertTrue(self.filled_order.position_set.id)
        self.assertTrue(self.position_instrument.position_set.id)
        self.assertTrue(self.profit_loss.position_set.id)

        print position_set.filledorder_set.all()
        print position_set.positioninstrument_set.all()
        print position_set.profitloss_set.all()

        self.assertTrue(position_set.filledorder_set.exists())
        self.assertTrue(position_set.positioninstrument_set.exists())
        self.assertTrue(position_set.positioninstrument_set.exists())














