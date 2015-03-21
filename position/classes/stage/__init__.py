# todo: more easy understand and test that context

"""
if no match for all stage, then is even
equity: 2 stages
1. P > BE profit
2. p < BE loss
no max profit, max loss

vertical: 4 stages
1. BE < P < MP profit
2. BE > P > ML loss
3. P > MP max profit
4. P < ML max loss

combo: 3 stages
1. A < P < B, even or profit or loss
2. P < A, loss
3. P > B, profit
"""
from position.classes.context.tests import TestUnitSetUpDB


class TestUnitSetUpStage(TestUnitSetUpDB):
    def check_in_stage(self, stage_cls, price, expect):
        """
        Check PositionStage in_stage method return correct boolean
        :param stage_cls: PositionStage
        :param price: float
        :param expect: boolean
        """
        print 'check in_stage...'
        print 'using current_price: %.2f' % price
        result = stage_cls.in_stage(price=price)
        print 'eval result: %s' % result
        self.assertEqual(result, expect)
        print '.' * 60

    def check_get_status(self, stage_cls, new_price, old_price, expect):
        """
        Check PositionStage get_status method return correct string direction
        :param stage_cls: PositionStage
        :param new_price: float
        :param old_price: float
        :param expect: str
        """
        print 'check get_status...'
        print 'using new_price: %.2f, old_price: %.2f' % (new_price, old_price)
        result = stage_cls.get_status(new_price=new_price, old_price=old_price)
        print 'eval result: %s' % result
        self.assertEqual(result, expect)
        print '.' * 60