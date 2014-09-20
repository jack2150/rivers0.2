from lib.test import TestReadyUp
from pms_app.pos_app.models import PositionStock, PositionSet
from lib.pos.identify.stock import StockIdentify
from lib.pos.spread.stock import StockLong, StockShort


class TestStockIdentify(TestReadyUp):
    def stock_conditions(self, attr, expected):
        """
        For test condition methods
        """
        stock = PositionStock()

        for qty, expect in zip([1, -1], expected):
            stock.quantity = qty

            stock_identify = StockIdentify(stock)
            result = getattr(stock_identify, attr)()

            self.assertEqual(result, expect)

            print 'quantity: %d' % qty
            print 'result: %s\n' % result

    def test_long_stock(self):
        """
        Test is long stock condition
        """
        self.stock_conditions('long_stock', [True, False])

    def test_short_stock(self):
        """
        Test is short stock condition
        """
        self.stock_conditions('short_stock', [False, True])

    def test_get_cls_long_stock(self):
        """
        Test get class return long stock position
        """
        self.ready_all(key=1)
        stock = PositionStock.objects.exclude(quantity__lte=0).first()

        stock_identify = StockIdentify(stock)
        cls = stock_identify.get_class()
        self.assertEqual(cls, StockLong)

        print 'stock quantity: %d' % stock.quantity
        print 'class module: %s\n' % cls

        spread = cls(PositionSet(stock.position))
        print spread

    def test_get_cls_short_stock(self):
        """
        Test get class return long stock position
        """
        self.ready_all(key=1)
        stock = PositionStock.objects.exclude(quantity__gte=0).first()

        stock_identify = StockIdentify(stock)
        cls = stock_identify.get_class()
        self.assertEqual(cls, StockShort)

        print 'stock quantity: %d' % stock.quantity
        print 'class module: %s\n' % cls

        spread = cls(PositionSet(stock.position))
        print spread