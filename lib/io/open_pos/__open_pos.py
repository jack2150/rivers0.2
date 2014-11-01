from lib.io.open_csv import OpenCSV


class OpenPos(OpenCSV):
    """
    Open a positions csv file from tos
    format then read positions data
    """
    def __init__(self, data):
        """
        :param data: str
        """
        # file name
        OpenCSV.__init__(self, data)

        # position columns
        self.position_columns = [
            'name',
            'quantity',
            'days',
            'trade_price',
            'mark',
            'mark_change',
            'delta',
            'gamma',
            'theta',
            'vega',
            'pct_change',
            'pl_open',
            'pl_day',
            'bp_effect'
        ]

        # positions
        self.positions = list()

        # overall columns
        self.overall_columns = [
            'cash_sweep',
            'pl_ytd',
            'bp_adjustment',
            'futures_bp',
            'available'
        ]

        # overall
        self.overall = dict()

        # options name
        self.options_name_columns = [
            'right',
            'special',
            'ex_month',
            'ex_year',
            'strike_price',
            'contract'
        ]

    @classmethod
    def is_positions(cls, items):
        """
        Check line is positions data or not
        :rtype : bool
        """
        return len(items) == 14 and items[0] != 'Instrument'

    @classmethod
    def get_first_items(cls, items):
        """
        Get first item from a list
        :rtype : str
        """
        return items[0]

    @classmethod
    def is_instrument(cls, item):
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

    @classmethod
    def is_stock(cls, item):
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

    @classmethod
    def is_options(cls, item):
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

    @classmethod
    def options_is_normal_contract(cls, items):
        """
        Check options only have 5 items
        :param items: str
        :return: bool
        """
        return len(items) == 5

    @classmethod
    def add_normal_to_options_name(cls, items):
        """
        Add item into first key of a list
        :param items: list
        """
        items.insert(1, 'Normal')

    def make_options_name_dict(self, items):
        """
        Make a dict using options list with column names
        :type items: object
        :return: dict
        """
        return {c: o for c, o in zip(self.options_name_columns, items)}

    def format_option_contract(self, item):
        """
        Get first item and split it into option contract
        :return: list
        """
        item = self.remove_brackets_only(item)
        items = self.split_str_with_space(item)

        if self.options_is_normal_contract(items):
            self.add_normal_to_options_name(items)

        options = self.make_options_name_dict(items)

        return options

    def set_options_name_in_items(self, items):
        """
        Set first item in list into options name list
        :param items: list
        """
        items[0] = self.format_option_contract(items[0])

    def make_pos_dict(self, items):
        """
        Input a list of position items and make a new dict with column names
        :rtype : dict
        """
        return {c: i for c, i in zip(self.position_columns, items)}

    @classmethod
    def reset_stock_and_options(cls):
        """
        Return two empty dict
        :rtype : dict, dict
        """
        return dict(), list()

    @classmethod
    def reset_symbol_and_instrument(cls):
        """
        Return a empty str and empty dict
        :rtype : str, dict
        """
        return str(), dict()

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

    @classmethod
    def get_company_name(cls, stock):
        """
        Get company name from stock list
        :param stock: dict
        :return: str
        """
        return stock['name']

    def set_pos(self, symbol, instrument, stock, options):
        """
        Save instrument, stock and options into class positions property
        :param instrument: dict
        :param options: list
        :param stock: dict
        :param symbol: str
        """
        self.positions.append({
            'symbol': symbol,
            'company': self.get_company_name(stock),
            'instrument': instrument,
            'stock': stock,
            'options': options
        })

    def set_pos_from_lines(self):
        """
        split lines into each symbol group
        each symbol group got 3 parts
        summary, underlying and options

        make sure ordered columns on csv files:
        Instrument,Qty,Days,Trade Price,Mark,Mrk Chng,Delta,
        Gamma,Theta,Vega,% Change,P/L Open,P/L Day,BP Effect

        :rtype: None
        """
        #lines = self.read_lines_from_file()
        lines = self.lines

        symbol, instrument = self.reset_symbol_and_instrument()
        stock, options = self.reset_stock_and_options()

        for line in lines:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            if self.is_positions(items):
                items = self.format_positions(items)

                first_item = self.get_first_items(items)

                # in order, instrument stock options
                if self.is_instrument(first_item):
                    # append position into positions
                    if symbol is not first_item and len(symbol):
                        self.set_pos(symbol, instrument, stock, options)

                    # set symbol for this position
                    symbol = first_item

                    # set instrument for positions
                    instrument = self.make_pos_dict(items)

                    # reset stock and options
                    stock, options = self.reset_stock_and_options()

                elif self.is_stock(first_item):
                    # set stock for positions
                    stock = self.make_pos_dict(items)

                elif self.is_options(first_item):
                    # set options for positions
                    self.set_options_name_in_items(items)

                    options.append(self.make_pos_dict(items))
        else:
            if len(symbol):
                self.set_pos(symbol, instrument, stock, options)

        return self.positions

    @classmethod
    def is_overall(cls, items):
        """
        Check the list items is overall lines
        :rtype : bool
        """
        return len(items) == 2

    @classmethod
    def get_overall_data_only(cls, items):
        """
        Input a list and return first item of the list
        :rtype : str
        """
        return items[1]

    def format_overall_item(self, item):
        """
        Format overall items that ready for insert db
        :type item : str
        :rtype : float
        """
        item = self.remove_bracket_then_add_negative(item)
        item = self.remove_dollar_symbols(item)

        return float(item)

    def make_overall_dict(self, overall):
        """
        Input a list of overall data and use overall columns
        make a new overall dict
        :rtype : dict
        """
        return {c: o for c, o in zip(self.overall_columns, overall)}

    def set_overall(self, overall):
        """
        Using overall list data and make dict with columns name
        then save it into class property overall
        :rtype : None
        """
        self.overall = self.make_overall_dict(overall)

    def set_overall_from_lines(self):
        """
        Read lines from csv positions files
        use the last 5 lines in files
        and create overall dict then save into class
        :rtype : None
        """
        #lines = self.read_lines_from_file()
        lines = self.lines

        # reset the overall variable
        overall = list()

        for line in self.last_five_lines(lines):
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            if self.is_overall(items):
                item = self.get_overall_data_only(items)
                item = self.format_overall_item(item)

                overall.append(item)

        self.set_overall(overall)

    def read(self):
        """
        Most important, read files and return positions and overall
        :rtype : list of dict, dict
        """
        self.set_pos_from_lines()
        self.set_overall_from_lines()

        return self.positions, self.overall