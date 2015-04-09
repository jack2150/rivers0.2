from data.models import Stock, OptionContract, Option
from tos_import.classes.tests import TestSaveModel
from tos_import.models import Underlying


class TestStock(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        self.symbol = 'IBM'
        self.underlying = Underlying(
            symbol=self.symbol,
            company='INTL BUSINESS MACHINES COM'
        )
        self.underlying.save()

        "{'high': 99.99, 'last': 99.64, 'volume': 6097146.0, 'low': 98.89, " \
        "'date': '2015-04-02', 'open': 99.44, 'net_change': 0.49}"

        self.items = {'high': 99.99, 'last': 99.64, 'volume': 6097146.0, 'low': 98.89,
                      'date': '2015-04-02', 'open': 99.44, 'net_change': 0.49}

        self.test_cls = Stock(
            underlying=self.underlying,
            source='tos_thinkback',
        )
        self.test_cls.data = self.items

        self.expect_keys = ['date', 'volume', 'open', 'high', 'low', 'last',
                            'net_change']

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()

        print 'underlying: %s' % self.test_cls.underlying
        print 'source: %s' % self.test_cls.source


class TestOptionContract(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        self.underlying = Underlying(
            symbol='IBM',
            company='INTL BUSINESS MACHINES COM'
        )
        self.underlying.save()

        self.items = {'ex_month': 'APR1', 'ex_year': 15, 'option_code': 'JNJ150402C85',
                      'right': 100, 'side': 'CALL', 'special': 'Weeklys', 'strike': '85'}

        self.test_cls = OptionContract(
            underlying=self.underlying,
            source='tos_thinkback',
            **self.items
        )

        self.expect_keys = [
            'ex_month', 'ex_year', 'right', 'special', 'strike', 'side', 'option_code'
        ]

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()

        print 'underlying: %s' % self.test_cls.underlying
        print 'source: %s' % self.test_cls.source


class TestOption(TestSaveModel):
    def setUp(self):
        TestSaveModel.setUp(self)

        self.underlying = Underlying(
            symbol='IBM',
            company='INTL BUSINESS MACHINES COM'
        )
        self.underlying.save()

        option_contract = {'ex_month': 'APR1', 'ex_year': 15, 'option_code': 'JNJ150402C92',
                           'right': 100, 'side': 'CALL', 'special': 'Weeklys', 'strike': '92'}

        self.option_contract = OptionContract(
            underlying=self.underlying,
            source='tos_thinkback',
            **option_contract
        )
        self.option_contract.save()

        self.items = {'ask': 7.9, 'bid': 7.55, 'date': '2015-04-02', 'delta': 0.96, 'dte': 0,
                      'extrinsic': 0.085, 'gamma': 0.02, 'impl_vol': 90.16, 'intrinsic': 7.64,
                      'open_int': 20.0, 'prob_itm': 95.23, 'prob_otm': 4.77, 'prob_touch': 9.45,
                      'theo_price': 0.0, 'theta': -0.22, 'vega': 0.0, 'volume': 0.0}

        self.test_cls = Option(
            option_contract=self.option_contract,
            **self.items
        )

        self.expect_keys = [
            'date', 'dte',
            'bid', 'ask', 'delta', 'gamma', 'theta', 'vega',
            'theo_price', 'impl_vol', 'prob_itm', 'prob_otm', 'prob_touch', 'volume',
            'open_int', 'intrinsic', 'extrinsic'
        ]

    def test_save(self):
        """
        Test save into db
        """
        self.method_test_save()

        print 'contract: %s' % self.test_cls.option_contract

    def test_set_data_dict(self):
        """
        Test set raw data dict into model then save
        auto create foreign key option_contract and set it
        """
        self.items = {'ask': 14.9, 'bid': 14.55, 'date': '2015-04-02', 'delta': 0.97, 'dte': 0,
                      'extrinsic': 0.085, 'gamma': 0.01, 'impl_vol': 159.66, 'intrinsic': 14.64,
                      'open_int': 0.0, 'prob_itm': 96.86, 'prob_otm': 3.14, 'prob_touch': 6.18,
                      'theo_price': 0.0, 'theta': -0.25, 'vega': 0.0, 'volume': 0.0}

        self.test_cls = Option(
            option_contract=self.option_contract
        )

        self.test_cls.data = self.items
        self.method_test_save()

        print 'contract: %s' % self.test_cls.option_contract

















