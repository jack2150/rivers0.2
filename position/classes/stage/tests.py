from position.classes.context.tests import TestUnitSetUpDB
from position.models import PositionStage


class TestUnitSetUpStage(TestUnitSetUpDB):
    def method_test_create_stage(self, stage, name, expression, detail):
        """
        Create even stage using filled orders data
        :param stage: PositionStage
        :param name: str
        :param expression: str
        :param detail: dict
        """
        print 'current_stage: %s' % stage
        print '.' * 80
        print 'stage_name: %s' % stage.stage_name
        print 'stage_expression: %s' % stage.stage_expression
        print '.' * 80
        print 'price_a: %.2f' % stage.price_a
        print 'amount_a: %.2f' % stage.amount_a
        print 'price_b: %.2f' % stage.price_b
        print 'amount_b: %.2f' % stage.amount_b
        print '.' * 80
        print 'left_status: %s' % stage.left_status
        print 'left_expression: %s' % stage.left_expression
        print 'right_status: %s' % stage.right_status
        print 'right_expression: %s\n' % stage.right_expression
        print ':' * 80 + '\n'

        self.assertEqual(type(stage), PositionStage)
        self.assertFalse(stage.id)
        self.assertEqual(stage.stage_name, name)
        self.assertEqual(stage.stage_expression, expression)
        self.assertEqual(float(stage.price_a), detail['price_a'])
        self.assertEqual(float(stage.amount_a), detail['amount_a'])
        self.assertEqual(float(stage.price_b), detail['price_b'])
        self.assertEqual(float(stage.amount_b), detail['amount_b'])
        self.assertEqual(stage.left_status, detail['left_status'])
        self.assertEqual(stage.left_expression, detail['left_expression'])
        self.assertEqual(stage.right_status, detail['right_status'])
        self.assertEqual(stage.right_expression, detail['right_expression'])

    def check_in_stage(self, stage_cls, price, expect):
        """
        Check PositionStage in_stage method return correct boolean
        :param stage_cls: PositionStage
        :param price: float
        :param expect: boolean
        """
        print stage_cls
        print '.' * 60
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
        print stage_cls
        print '.' * 60
        print 'check get_status...'
        print 'using new_price: %.2f, old_price: %.2f' % (new_price, old_price)
        result = stage_cls.get_status(new_price=new_price, old_price=old_price)
        print 'eval result: %s' % result
        self.assertEqual(result, expect)
        print '.' * 60
