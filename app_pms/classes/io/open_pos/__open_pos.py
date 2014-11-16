from app_pms.classes.io.open_csv import OpenCSV


class OpenPos(OpenCSV):
    def __init__(self, data):
        OpenCSV.__init__(self, data=data)

        self.equity_option_keys = [
            'name', 'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'delta',
            'gamma', 'theta', 'vega', 'pct_change', 'pl_open', 'pl_day', 'bp_effect'
        ]

        self.position_summary_keys = [
            'cash_sweep', 'pl_ytd', 'bp_adjustment', 'futures_bp', 'available'
        ]

        self.option_key = [
            'right', 'special', 'ex_month', 'ex_year', 'strike', 'contract'
        ]

        self.future_position_keys = [
            'symbol', 'quantity', 'days', 'trade_price', 'mark', 'mark_change',
            'pct_change', 'pl_open', 'pl_day', 'bp_effect'
        ]

        self.forex_position_keys = [
            'symbol', 'quantity', 'trade_price', 'mark', 'mark_change',
            'pct_change', 'pl_open', 'pl_day', 'bp_effect'
        ]

        self.equity_option_position = list()
        self.position_summary = list()
        self.future_position = list()
        self.forex_position = list()

    def format_positions(self, items):
        """
        Format positions dict that ready for insert db
        """
        for key, item in enumerate(items):
            if len(item):
                item = self.remove_bracket_then_add_negative(item)
                item = self.remove_dollar_symbols(item)
                item = self.remove_percent_symbols(item)

                if key == 0:
                    # first item is name
                    item = str(item)
                else:
                    # other is float value
                    try:
                        item = float(item)
                    except ValueError:
                        item = 0.00
            else:
                # empty, so assign 0
                item = 0.0

            # assign back into items
            items[key] = item

        return items

    @staticmethod
    def is_instrument(item):
        """
        Check first item is instrument or not
        :rtype : bool
        """
        if item:
            words = item.split(' ')
            result = bool(len(words) == 1)
        else:
            result = False

        return result

    @staticmethod
    def is_equity(item):
        """
        Check first item is stock or not
        :rtype : bool
        """
        if item:
            words = item.split(' ')

            result = False
            if words[0] not in ('100', '10'):
                if words[-1] not in ('CALL', 'PUT'):
                    if len(words) > 1:
                        result = True
        else:
            result = True

        return result

    @staticmethod
    def is_option(item):
        """
        Check first item is options or not
        :rtype : bool
        """
        words = item.split(' ')

        result = False
        if words[0].isdigit():
            if words[-1] in ('CALL', 'PUT'):
                result = True

        return result

    def format_option_contract(self, item):
        """
        Get first item and split it into option contract
        :return: list
        """
        items = self.split_str_with_space(item)

        if len(items) == 5:
            items.insert(1, 'Normal')

        items[0] = int(items[0])  # right
        items[3] = int(items[3])  # year
        items[4] = float(items[4])  # strike

        return {key: value for key, value in zip(self.option_key, items)}

    @staticmethod
    def reset_position_set():
        """
        Return a blank dict
        :rtype : dict
        """
        return dict(
            symbol='',
            company='',
            instrument=None,
            equity=None,
            options=list()
        )

    def append_equity_option_position(self, position_set):
        """
        Append data into equity option position class property
        """
        position_set['symbol'] = position_set['instrument']['name']
        position_set['company'] = position_set['equity']['name']

        self.equity_option_position.append(position_set)

    def set_future_position(self):
        """
        Get future and future option from line
        and save it into class property
        """
        self.set_values(
            start_phrase='Futures and Futures Options',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.future_position_keys,
            prop_name='future_position'
        )

        future_position = list()
        for instrument, future in zip(self.future_position[0::2], self.future_position[1::2]):
            future_position.append(dict(
                symbol=instrument['symbol'],
                quantity=instrument['quantity'],
                days=future['days'],
                trade_price=future['trade_price'],
                mark=instrument['mark'],
                mark_change=instrument['mark_change'],
                pct_change=instrument['pct_change'],
                pl_open=future['pl_open'],
                pl_day=future['pl_day'],
                bp_effect=instrument['bp_effect']
            ))

        self.future_position = future_position

        self.convert_specific_type(self.future_position, 'quantity', int, 0)
        self.convert_specific_type(self.future_position, 'days', int, 0)

    def set_forex_position(self):
        """
        Get forex from line
        and save it into class property
        """
        self.set_values(
            start_phrase='Forex',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.forex_position_keys,
            prop_name='forex_position'
        )

        forex_position = list()
        for instrument, future in zip(self.forex_position[0::2], self.forex_position[1::2]):
            forex_position.append(dict(
                symbol=instrument['symbol'],
                quantity=instrument['quantity'],
                trade_price=future['trade_price'],
                mark=instrument['mark'],
                mark_change=instrument['mark_change'],
                pct_change=instrument['pct_change'],
                pl_open=future['pl_open'],
                pl_day=future['pl_day'],
                bp_effect=instrument['bp_effect']
            ))

        self.forex_position = forex_position

        self.convert_specific_type(self.forex_position, 'quantity', int, 0)

    def set_position_summary(self):
        """
        Get position summary from line
        and save it into class property
        """
        lines = self.get_lines(
            start_phrase='Cash & Sweep Vehicle',
            end_phrase='AVAILABLE DOLLARS'
        )

        position_summary = list()
        for line in lines:
            line = self.replace_dash_inside_quote(line)
            item = self.split_lines_with_dash(line)[1]

            item = self.format_item(item)

            position_summary.append(item)

        self.position_summary = {
            key: value for key, value in zip(self.position_summary_keys, position_summary)
        }

    def set_equity_option_position(self):
        """
        Get instrument, stock, option from line
        and save it into class property
        """
        # new format
        lines = self.get_lines(
            start_phrase='Equities and Equity Options',
            end_phrase=None
        )

        position_set = self.reset_position_set()
        equity_exist = False
        options_exist = False

        for line in lines[2:-1]:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            if len(items) == 14:  # is position
                items = self.format_positions(items)
                first_item = items[0]

                # check is next instrument
                if self.is_instrument(first_item) and (equity_exist or options_exist):
                    #print 'next...\n'

                    self.append_equity_option_position(position_set)
                    position_set = self.reset_position_set()
                    equity_exist = False
                    options_exist = False

                if self.is_instrument(first_item):
                    position_set['instrument'] = {
                        key: value for key, value in zip(self.equity_option_keys, items)
                    }
                    #print 'instrument', position_set['instrument']
                elif self.is_equity(first_item):
                    position_set['equity'] = {
                        key: value for key, value in zip(self.equity_option_keys, items)
                    }
                    equity_exist = True
                    #print 'equity', position_set['equity']
                elif self.is_option(first_item):
                    option = {
                        key: value for key, value in zip(self.equity_option_keys, items)
                    }

                    option['name'] = self.format_option_contract(option['name'])

                    position_set['options'].append(option)
                    options_exist = True
                    #print 'options', position_set['options']
        else:
            # last position set
            self.append_equity_option_position(position_set)

    def read(self):
        """
        Most important, read files and return positions and overall
        :rtype : dict
        """
        self.set_equity_option_position()
        self.set_future_position()
        self.set_position_summary()
        self.set_forex_position()

        return dict(
            equity_option_position=self.equity_option_position,
            future_position=self.future_position,
            forex_position=self.forex_position,
            position_summary=self.position_summary
        )

# todo: save pos




















