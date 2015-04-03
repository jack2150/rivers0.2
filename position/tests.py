# noinspection PyUnresolvedReferences
import position.classes.ready_django
from django.db.models import Q
from position.models import *
from tos_import.classes.tests import TestSetUpDB, TestReadyFile
from tos_import.files.real_files import real_path
from tos_import.models import Statement
from tos_import.statement.statement_account.models import AccountSummary, ProfitLoss
from tos_import.statement.statement_position.models import PositionSummary, PositionInstrument
from tos_import.statement.statement_trade.models import FilledOrder


class TestPositionSet(TestReadyFile):
    def setUp(self):
        TestReadyFile.setUp(self)

        self.items = list()

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
        )
        position_set.save()

        self.assertTrue(position_set.id)
        self.assertEqual(PositionSet.objects.count(), 1)

        print 'run save...\n'
        print position_set

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

    def method_test_current_stage(self, position_set, price, expect):
        """
        Use for test current stage result
        :param position_set: PositionSet
        :param price: float
        :param expect: str
        """
        result = position_set.get_stage(price=price).stage_name
        self.assertEqual(result, expect)
        print 'using price: %.2f, result: %s, expect: %s' % (price, result, expect)

    def test_current_stage(self):
        """
        Test get current stage for this position set
        """
        position_set = PositionSet(
            underlying=self.underlying,
            name=self.name,
            spread=self.spread,
        )
        position_set.save()
        self.position_instrument.position_set = position_set
        self.position_instrument.save()

        print 'using filled_order net_price: %.2f' % self.filled_order.net_price

        position_set.positionstage_set.create(
            stage_name='PROFIT',
            stage_expression='{price_a} < {current_price}',
            price_a=14.93
        )
        position_set.positionstage_set.create(
            stage_name='EVEN',
            stage_expression='{price_a} == {current_price}',
            price_a=14.93
        )
        position_set.positionstage_set.create(
            stage_name='LOSS',
            stage_expression='{current_price} < {price_a}',
            price_a=14.93
        )

        print 'position_stage list:'
        for position_stage in position_set.positionstage_set.all():
            print position_stage

        self.method_test_current_stage(position_set, 14.93, 'EVEN')
        self.method_test_current_stage(position_set, 15.5, 'PROFIT')
        self.method_test_current_stage(position_set, 13.8, 'LOSS')


class TestPositionStage(TestSetUpDB):
    def setUp(self):
        TestSetUpDB.setUp(self)

        underlying = Underlying(
            symbol='AAPL',
            company='Apple Inc.'
        )
        underlying.save()

        self.position_set = PositionSet(
            name='EQUITY',
            spread='LONG_STOCK',
            status='OPEN',
            underlying=underlying
        )
        self.position_set.save()

        self.stage = PositionStage()
        self.stage.stage_name = 'PROFIT'
        self.stage.stage_expression = '{price_a} < {current_price}'

        self.stage.price_a = 127.85
        self.stage.amount_a = 0.0

        self.stage.left_status = 'decreasing'
        self.stage.left_expression = '{price_a} < {new_price} < {old_price}'
        self.stage.right_status = 'profiting'
        self.stage.right_expression = '{price_a} < {old_price} < {new_price}'
        self.stage.position_set = self.position_set

    def test_save(self):
        """
        Test save position stage
        """
        self.stage.save()
        print 'saved...'

        print '.' * 60
        print 'position_stage: %s' % self.stage
        print 'position_stage id: %d' % self.stage.id
        print 'status_name: %s' % self.stage.stage_name
        print 'status_expression: %s' % self.stage.stage_expression
        print 'position_set: %s' % self.stage.position_set
        print '.' * 60
        print 'price_a: %s' % self.stage.price_a
        print 'amount_a: %s' % self.stage.amount_a
        print '.' * 60
        print 'left_status: %s' % self.stage.left_status
        print 'left_expression: %s' % self.stage.left_expression
        print 'right_status: %s' % self.stage.right_status
        print 'right_expression: %s' % self.stage.right_expression

        self.assertTrue(self.stage.id)
        self.assertEqual(self.stage.position_set, self.position_set)

    def test_in_stage(self):
        """
        Test price is in current stage
        """
        self.stage.save()

        current_price = 130.0
        print 'using current_price: %.2f' % current_price
        result = self.stage.in_stage(current_price=current_price)
        print 'eval result: %s' % result
        self.assertTrue(result)

        print '.' * 60

        current_price = 125.0
        print 'using current_price: %.2f' % current_price
        result = self.stage.in_stage(current_price=current_price)
        print 'eval result: %s' % result
        self.assertFalse(result)

    def test_get_status(self):
        """
        Test stage eval method that return left or right status
        """
        self.stage.save()

        new_price = 130.00
        old_price = 135.00
        print 'using new_price: %.2f, old_price: %.2f' % (new_price, old_price)
        result = self.stage.get_status(new_price=new_price, old_price=old_price)
        print 'eval result: %s' % result
        self.assertEqual(result, 'decreasing')

        print '.' * 60

        new_price = 140.00
        old_price = 135.00
        print 'using new_price: %.2f, old_price: %.2f' % (new_price, old_price)
        result = self.stage.get_status(new_price=new_price, old_price=old_price)
        print 'eval result: %s' % result
        self.assertEqual(result, 'profiting')

        print '.' * 60

        new_price = 130.00
        old_price = 130.00
        print 'using new_price: %.2f, old_price: %.2f' % (new_price, old_price)
        result = self.stage.get_status(new_price=new_price, old_price=old_price)
        print 'eval result: %s' % result
        self.assertEqual(result, 'UNKNOWN')


















