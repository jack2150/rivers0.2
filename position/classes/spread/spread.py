# noinspection PyUnresolvedReferences
from django.db.models.query import QuerySet


# todo: credit or debit, probability of profit (pop-pol, 70%-30%)
class Spread(object):
    """
    primary use to identify spread type and return name and spread
    currency only use for 'TO OPEN' pos effect filled order
    example name: ['EQUITY', 'OPTION', 'SPREAD', 'FUTURE', 'FOREX']
    example spread: ['LONG_STOCK', 'NAKED_CALL', 'FUTURE', 'FOREX']
    """
    def __init__(self, filled_orders):
        """
        :param filled_orders: list of FilledOrder
        """
        if type(filled_orders) is not QuerySet:
            raise TypeError('Parameter is not QuerySet of <FilledOrder> object type.')

        self.filled_orders = filled_orders
        """:type : list of FilledOrder"""

        # identify variable
        self.name = ''  # ['EQUITY', 'HEDGE', 'OPTION', 'SPREAD', 'FUTURE', 'FOREX']
        self.spread = ''

        # effect
        self.account = ''  # credit or debit
        self.probability = {
            'Profit': 0.0,  # all in percentage, 0.7351
            'Even': 0.0,
            'Loss': 0.0
        }

    def get_underlying(self):
        """
        get underlying object from filled orders
        :return: Underlying
        """
        underlying = None
        for filled_order in self.filled_orders:
            if not underlying:
                underlying = filled_order.underlying
            else:
                if underlying.symbol != filled_order.underlying.symbol:
                    raise ValueError(
                        'Different underlying on filled_orders %s != %s' % (
                            underlying.symbol, filled_order.underlying.symbol
                        )
                    )

        return underlying

    def get_future(self):
        """
        get future object from filled orders
        :return: Forex
        """
        future = None
        for filled_order in self.filled_orders:
            if not future:
                future = filled_order.future
            else:
                if future.symbol != filled_order.future.symbol:
                    raise ValueError(
                        'Different future on filled_orders %s != %s' % (
                            future.symbol, filled_order.future.symbol
                        )
                    )

        return future

    def get_forex(self):
        """
        get future object from filled orders
        :return: Future
        """
        forex = None
        for filled_order in self.filled_orders:
            if not forex:
                forex = filled_order.forex
            else:
                if forex.symbol != filled_order.forex.symbol:
                    raise ValueError(
                        'Different forex on filled_orders %s != %s' % (
                            forex.symbol, filled_order.forex.symbol
                        )
                    )

        return forex

    def get_name(self, module=False, lower=False):
        """
        determine name of the spread, all filled orders record must same
        :rtype : str
        """
        spread = ''
        for filled_order in self.filled_orders:
            if spread == '':
                spread = filled_order.spread
            else:
                if spread != filled_order.spread:
                    raise ValueError(
                        'Different name on filled_orders %s != %s' % (
                            spread, filled_order.spread
                        )
                    )

        if spread == 'STOCK':
            name = 'EQUITY'
        elif spread == 'COVERED':
            name = 'HEDGE'
        elif spread == 'SINGLE':
            name = 'OPTION'
        elif spread == 'FUTURE':
            name = 'FUTURE'
        elif spread == 'FOREX':
            name = 'FOREX'
        else:
            name = 'SPREAD'
            if module:
                option_legs = len(self.filled_orders)
                strategy_name = self.filled_orders[0].spread.lower()
                if option_legs == 2:
                    name += '.LEG_TWO.' + strategy_name
                elif option_legs == 3:
                    name += '.LEG_THREE.' + strategy_name
                elif option_legs == 4:
                    name += '.LEG_FOUR.' + strategy_name

        # set class name variable
        self.name = name

        # return name str
        if lower:
            name = name.lower()

        return name

    def get_account(self):
        """
        Get spread is credit or debit
        :return: str
        """
        net_price = 0.0
        for filled_order in self.filled_orders:
            if filled_order.net_price:
                net_price = filled_order.net_price

        if net_price > 0:
            account = 'DEBIT'
        elif net_price < 0:
            account = 'CREDIT'
        else:
            account = 'BALANCE'

        return account

    def get_probability(self):
        """
        Get spread probability of (profit, even, loss)
        :return: dict of str
        """
        spread = ''
        for filled_order in self.filled_orders:
            if spread == '':
                spread = filled_order.spread
            else:
                if spread != filled_order.spread:
                    raise ValueError(
                        'Different name on filled_orders %s != %s' % (
                            spread, filled_order.spread
                        )
                    )

        probability = dict(
            profit=0.5,
            even=0,
            loss=0.5,
            name='EVEN'
        )

        if spread == 'COVERED':
            name = 'HEDGE'
        elif spread == 'SINGLE':
            name = 'OPTION'
        else:
            name = 'SPREAD'

        return probability

    # todo: get iv, then calculate probability...

    def get_equity_spread(self):
        """
        Check equity spread using only quantity
        equity only got 1 stock filled order
        :return: str
        """
        filled_order = self.filled_orders[0]
        if filled_order.quantity > 0 and filled_order.side == 'BUY':
            spread = 'LONG_STOCK'
        elif filled_order.quantity < 0 and filled_order.side == 'SELL':
            spread = 'SHORT_STOCK'
        else:
            spread = 'CUSTOM'

        return spread

    def get_hedge_spread(self):
        """
        Check hedge spread using filled orders quantity and option type
        hedge contain 1 stock and 1 option filled orders
        8 type of spreads, with check balance
        :return: str
        """
        hedges = {
            'long_stock': {
                'long_call': 'CUSTOM',
                'short_call': 'COVERED_CALL',
                'long_put': 'PROTECTIVE_PUT',
                'short_put': 'CUSTOM',
            },
            'short_stock': {
                'long_call': 'PROTECTIVE_CALL',
                'short_call': 'CUSTOM',
                'long_put': 'CUSTOM',
                'short_put': 'COVERED_PUT',
            }
        }

        stock = dict(
            name='',
            balance=0
        )
        option = dict(
            name='',
            balance=0
        )
        for filled_order in self.filled_orders:
            if filled_order.contract == 'STOCK':
                # stock order
                if filled_order.quantity > 0 and filled_order.side == 'BUY':
                    stock['name'] = 'long_stock'
                elif filled_order.quantity < 0 and filled_order.side == 'SELL':
                    stock['name'] = 'short_stock'

                # balance
                stock['balance'] = abs(int(filled_order.quantity / 100))
            else:
                # call or put option order
                if filled_order.quantity > 0 and filled_order.side == 'BUY':
                    option['name'] = 'long_%s' % filled_order.contract.lower()
                elif filled_order.quantity < 0 and filled_order.side == 'SELL':
                    option['name'] = 'short_%s' % filled_order.contract.lower()

                # balance
                option['balance'] = abs(filled_order.quantity)

        # balance check
        if stock['balance'] == option['balance']:
            spread = hedges[stock['name']][option['name']]
        else:
            spread = 'CUSTOM'

        return spread

    def get_option_spread(self):
        """
        Check option spread using filled orders
        option only contain 1 option order
        :rtype : str
        """
        filled_order = self.filled_orders[0]
        if filled_order.quantity > 0 and filled_order.side == 'BUY':
            spread = 'LONG_%s' % filled_order.contract.upper()
        elif filled_order.quantity < 0 and filled_order.side == 'SELL':
            spread = 'NAKED_%s' % filled_order.contract.upper()
        else:
            spread = 'CUSTOM'

        return spread

    def get_future_spread(self):
        """
        Check future spread using filled orders
        future only contain 1 order
        :rtype : str
        """
        filled_order = self.filled_orders[0]
        if filled_order.quantity > 0 and filled_order.side == 'BUY':
            spread = 'LONG_FUTURE'
        elif filled_order.quantity < 0 and filled_order.side == 'SELL':
            spread = 'SHORT_FUTURE'
        else:
            spread = 'CUSTOM'

        return spread

    def get_forex_spread(self):
        """
        Check future spread using filled orders
        forex only contain 1 order
        :rtype : str
        """
        filled_order = self.filled_orders[0]
        if filled_order.quantity > 0 and filled_order.side == 'BUY':
            spread = 'LONG_FOREX'
        elif filled_order.quantity < 0 and filled_order.side == 'SELL':
            spread = 'SHORT_FOREX'
        else:
            spread = 'CUSTOM'

        return spread

    def get_two_leg_options_spread(self):
        """
        Check 2 options spread using filled order data
        vertical, strangle, straddle, combo, back ratio
        2 options x 2 contracts ('call', 'put') x 2 side ('buy', 'sell')
        :return: str
        """
        spread = 'CUSTOM'

        # make sure first item quantity is bigger than second
        if self.filled_orders[0].quantity > self.filled_orders[1].quantity:
            filled_order1 = self.filled_orders[0]
            filled_order2 = self.filled_orders[1]
        else:
            filled_order1 = self.filled_orders[1]
            filled_order2 = self.filled_orders[0]

        if filled_order1.spread == filled_order2.spread == 'VERTICAL':
            if filled_order1.contract == filled_order2.contract == 'CALL':
                if filled_order1.strike > filled_order2.strike:
                    spread = 'SHORT_CALL_VERTICAL'  # 1 105, -1 95
                elif filled_order1.strike < filled_order2.strike:
                    spread = 'LONG_CALL_VERTICAL'  # 1 95, -1 105
            elif filled_order1.contract == filled_order2.contract == 'PUT':
                if filled_order1.strike > filled_order2.strike:
                    spread = 'LONG_PUT_VERTICAL'  # 1 105, -1 95
                elif filled_order1.strike < filled_order2.strike:
                    spread = 'SHORT_PUT_VERTICAL'  # 1 95, -1 105

        elif filled_order1.spread == filled_order2.spread == 'STRANGLE':
            if filled_order1.quantity > 0 and filled_order2.quantity > 0:
                spread = 'LONG_STRANGLE'
            elif filled_order1.quantity < 0 and filled_order2.quantity < 0:
                spread = 'SHORT_STRANGLE'

        elif filled_order1.spread == filled_order2.spread == 'STRADDLE':
            if filled_order1.quantity > 0 and filled_order2.quantity > 0:
                spread = 'LONG_STRADDLE'
            elif filled_order1.quantity < 0 and filled_order2.quantity < 0:
                spread = 'SHORT_STRADDLE'

        elif filled_order1.spread == filled_order2.spread == 'COMBO':
            if filled_order1.contract == 'CALL':
                spread = 'LONG_COMBO'  # 1 call 100 , -1 put 95
            elif filled_order1.contract == 'PUT':
                spread = 'SHORT_COMBO'  # 1 put 100 , -1 call 95

        elif filled_order1.spread == filled_order2.spread == 'BACKRATIO':  # 1, -2: -1, 2
            if filled_order1.contract == filled_order2.contract == 'CALL':  # call, call
                if filled_order1.strike < filled_order2.strike:  # 20 < 21
                    if abs(filled_order1.quantity) < abs(filled_order2.quantity):  # 1 < 2
                        spread = 'SHORT_CALL_BACKRATIO'  # 1 20 call, -2 21 call
                elif filled_order1.strike > filled_order2.strike:  # 21 > 20
                    if abs(filled_order1.quantity) > abs(filled_order2.quantity):  # 2 > 1
                        spread = 'LONG_CALL_BACKRATIO'  # 2 21 call, -1 20 call
            elif filled_order1.contract == filled_order2.contract == 'PUT':  # put, put
                if filled_order1.strike > filled_order2.strike:  # 19, 18
                    if abs(filled_order1.quantity) < abs(filled_order2.quantity):  # 1 < 2
                        spread = 'LONG_PUT_BACKRATIO'  # 1 19 put, -2 18 put
                elif filled_order1.strike < filled_order2.strike:  # 95, 105
                    if abs(filled_order1.quantity) > abs(filled_order2.quantity):  # 2 > 1
                        spread = 'SHORT_PUT_BACKRATIO'  # -1 19 put, 2 18 put

        # todo: calendar spread

        return spread

    def get_three_leg_options_spread(self):
        """
        Check 3 options spread using filled order data
        only contain butterfly that is long or short, balance or unbalance
        :return: str
        """
        spread = 'CUSTOM'

        # order of quantity in tos is 1-2-1 and strike call low to high, put high to low
        filled_order1 = self.filled_orders[0]
        filled_order2 = self.filled_orders[1]
        filled_order3 = self.filled_orders[2]

        if filled_order1.spread == filled_order2.spread == filled_order3.spread == 'BUTTERFLY':
            if filled_order1.contract == filled_order2.contract == filled_order3.contract == 'CALL':
                if filled_order1.side == filled_order3.side == 'BUY' and filled_order2.side == 'SELL':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    if strike_different1 == strike_different2:
                        spread = 'LONG_CALL_BUTTERFLY'
                    else:
                        spread = 'LONG_CALL_BROKEN_WING_BUTTERFLY'

                elif filled_order1.side == filled_order3.side == 'SELL' and filled_order2.side == 'BUY':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    if strike_different1 == strike_different2:
                        spread = 'SHORT_CALL_BUTTERFLY'
                    else:
                        spread = 'SHORT_CALL_BROKEN_WING_BUTTERFLY'

            elif filled_order1.contract == filled_order2.contract == filled_order3.contract == 'PUT':
                if filled_order1.side == filled_order3.side == 'BUY' and filled_order2.side == 'SELL':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    if strike_different1 == strike_different2:
                        spread = 'LONG_PUT_BUTTERFLY'
                    else:
                        spread = 'LONG_PUT_BROKEN_WING_BUTTERFLY'

                elif filled_order1.side == filled_order3.side == 'SELL' and filled_order2.side == 'BUY':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    print strike_different1, ' ', strike_different2

                    if strike_different1 == strike_different2:
                        spread = 'SHORT_PUT_BUTTERFLY'
                    else:
                        spread = 'SHORT_PUT_BROKEN_WING_BUTTERFLY'

        elif filled_order1.spread == filled_order2.spread == filled_order3.spread == '~BUTTERFLY':
            # all unbalance
            if filled_order1.contract == filled_order2.contract == filled_order3.contract == 'CALL':
                if filled_order1.side == filled_order3.side == 'BUY' and filled_order2.side == 'SELL':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    print strike_different1, ' ', strike_different2
                    print filled_order1.side, ' ', filled_order2.side, ' ', filled_order3.side

                    if strike_different1 == strike_different2:
                        spread = 'LONG_CALL_UNBALANCE_BUTTERFLY'
                    else:
                        spread = 'LONG_CALL_UNBALANCE_BROKEN_WING_BUTTERFLY'
                elif filled_order1.side == filled_order3.side == 'SELL' and filled_order2.side == 'BUY':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    print strike_different1, ' ', strike_different2
                    print filled_order1.side, ' ', filled_order2.side, ' ', filled_order3.side

                    if strike_different1 == strike_different2:
                        spread = 'SHORT_CALL_UNBALANCE_BUTTERFLY'
                    else:
                        spread = 'SHORT_CALL_UNBALANCE_BROKEN_WING_BUTTERFLY'

            elif filled_order1.contract == filled_order2.contract == filled_order3.contract == 'PUT':
                if filled_order1.side == filled_order3.side == 'BUY' and filled_order2.side == 'SELL':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    if strike_different1 == strike_different2:
                        spread = 'LONG_PUT_UNBALANCE_BUTTERFLY'
                    else:
                        spread = 'LONG_PUT_UNBALANCE_BROKEN_WING_BUTTERFLY'
                elif filled_order1.side == filled_order3.side == 'SELL' and filled_order2.side == 'BUY':
                    strike_different1 = filled_order2.strike - filled_order1.strike
                    strike_different2 = filled_order3.strike - filled_order2.strike

                    if strike_different1 == strike_different2:
                        spread = 'SHORT_PUT_UNBALANCE_BUTTERFLY'
                    else:
                        spread = 'SHORT_PUT_UNBALANCE_BROKEN_WING_BUTTERFLY'

        return spread

    def get_four_leg_options_spread(self):
        """
        Check 4 options spread using filled order data
        only contain condor or iron condor that is long or short, balance or unbalance, iron butterfly
        :return: str
        """

        spread = 'CUSTOM'

        # order of quantity in tos is 1-2-1 and strike call low to high, put high to low
        fs = self.filled_orders

        strikes = [float(f.strike) for f in self.filled_orders]
        max_strike_index = strikes.index(max(strikes))
        min_strike_index = strikes.index(min(strikes))

        sorted_strikes = sorted([float(f.strike) for f in self.filled_orders], reverse=True)
        strike_range1 = sorted_strikes[0] - sorted_strikes[1]
        strike_range2 = sorted_strikes[2] - sorted_strikes[3]

        if sum([True for f in fs if f.spread == 'CONDOR']) == 4:
            if sum([True for f in fs if f.contract == 'CALL']) == 4:
                if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                    if strike_range1 == strike_range2:
                        spread = 'LONG_CALL_CONDOR'
                    else:
                        spread = 'LONG_BROKEN_WING_CALL_CONDOR'
                else:
                    if strike_range1 == strike_range2:
                        spread = 'SHORT_CALL_CONDOR'
                    else:
                        spread = 'SHORT_BROKEN_WING_CALL_CONDOR'
            elif sum([True for f in fs if f.contract == 'PUT']) == 4:
                if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                    if strike_range1 == strike_range2:
                        spread = 'LONG_PUT_CONDOR'
                    else:
                        spread = 'LONG_BROKEN_WING_PUT_CONDOR'
                else:
                    if strike_range1 == strike_range2:
                        spread = 'SHORT_PUT_CONDOR'
                    else:
                        spread = 'SHORT_BROKEN_WING_PUT_CONDOR'
        elif sum([True for f in fs if f.spread == '~CONDOR']) == 4:
            if sum([True for f in fs if f.contract == 'CALL']) == 4:
                if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                    if strike_range1 == strike_range2:
                        spread = 'LONG_UNBALANCE_CALL_CONDOR'
                    else:
                        spread = 'LONG_UNBALANCE_BROKEN_WING_CALL_CONDOR'
                else:
                    if strike_range1 == strike_range2:
                        spread = 'SHORT_UNBALANCE_CALL_CONDOR'
                    else:
                        spread = 'SHORT_UNBALANCE_BROKEN_WING_CALL_CONDOR'
            elif sum([True for f in fs if f.contract == 'PUT']) == 4:
                if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                    if strike_range1 == strike_range2:
                        spread = 'LONG_UNBALANCE_PUT_CONDOR'
                    else:
                        spread = 'LONG_UNBALANCE_BROKEN_WING_PUT_CONDOR'
                else:
                    if strike_range1 == strike_range2:
                        spread = 'SHORT_UNBALANCE_PUT_CONDOR'
                    else:
                        spread = 'SHORT_UNBALANCE_BROKEN_WING_PUT_CONDOR'

        elif sum([True for f in fs if f.spread == 'IRON CONDOR']) == 4:
            if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                if strike_range1 == strike_range2:
                    spread = 'LONG_IRON_CONDOR'
                else:
                    spread = 'LONG_BROKEN_WING_IRON_CONDOR'
            else:
                if strike_range1 == strike_range2:
                    spread = 'SHORT_IRON_CONDOR'
                else:
                    spread = 'SHORT_BROKEN_WING_IRON_CONDOR'

        elif sum([True for f in fs if f.spread == '~IRON CONDOR']) == 4:
            if fs[max_strike_index].side == fs[min_strike_index].side == 'BUY':
                if strike_range1 == strike_range2:
                    spread = 'LONG_UNBALANCE_IRON_CONDOR'
                else:
                    spread = 'LONG_UNBALANCE_BROKEN_WING_IRON_CONDOR'
            else:
                if strike_range1 == strike_range2:
                    spread = 'SHORT_UNBALANCE_IRON_CONDOR'
                else:
                    spread = 'SHORT_UNBALANCE_BROKEN_WING_IRON_CONDOR'

        # todo: double calendar, diagonal, strangle/straddle swap
        return spread

    def get_spread(self):
        """
        get spread type using filled orders
        :rtype : str
        """
        if self.name == '':
            raise ValueError('Set spread name before run get_spread method.')

        # start analyses spread
        spread = 'CUSTOM'
        if self.name == 'EQUITY':
            spread = self.get_equity_spread()
        elif self.name == 'HEDGE':
            spread = self.get_hedge_spread()
        elif self.name == 'OPTION':
            spread = self.get_option_spread()
        elif self.name == 'FUTURE':
            spread = self.get_future_spread()
        elif self.name == 'FOREX':
            spread = self.get_forex_spread()
        else:
            # the hard part, spread type
            option_legs = len(self.filled_orders)
            if option_legs == 2:
                spread = self.get_two_leg_options_spread()
            elif option_legs == 3:
                spread = self.get_three_leg_options_spread()
            elif option_legs == 4:
                spread = self.get_four_leg_options_spread()

        # set class spread variable
        self.spread = spread

        # return spread str
        return spread

    def get_spread_module(self):
        """
        Test get spread module name
        :rtype : str
        """
        if self.spread == '':
            self.get_spread()

        return ''.join(map(
            lambda s: s.lower().capitalize(), self.spread.split('_')
        ))