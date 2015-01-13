from pprint import pprint
from app_pms.classes.test import TestSetUp
from app_stat import models


class TestSaveData(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.items = {}
        self.test_cls = None
        self.expect_keys = None

    def test_save(self):
        if self.test_cls:
            print 'sample date: '
            pprint(self.items)

            self.test_cls.save()
            self.assertTrue(self.test_cls.id)

            print '\n' + '%s saved!' % self.test_cls.__class__.__name__
            print '%s id: %d' % (self.test_cls.__class__.__name__, self.test_cls.id)

            print self.test_cls

            for key in self.expect_keys:
                result = self.test_cls.__getattribute__(key)
                print '%s: %s' % (key, result)
                self.assertEqual(self.items[key], result)
        else:
            print 'skip test...'


class TestDateStat(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.items = dict(
            date='2014-08-01',
            pl_total=448.52,
            pl_ratio=0.782
        )

        self.test_cls = models.DateStat(**self.items)
        self.expect_keys = ['date', 'pl_total', 'pl_ratio']

