import numpy
from pandas import DataFrame


class OpenCSV(object):
    """
    All class methods in here
    """
    def __init__(self, data):
        #self.fname = fname
        #self.lines = self.read_lines_from_file()

        self.lines = map(lambda l: l.rstrip(), data.split('\n'))
        if not len(self.lines[-1]):
            self.lines = self.lines[:-1]

    def read_lines_from_file(self, fname):
        """
        Read line from position file and
        remove new line at end of line
        :rtype : list
        """
        self.lines = map(lambda l: l.rstrip(), open(fname).readlines())

    @classmethod
    def replace_dash_inside_quote(cls, line, replace_with=''):
        """
        Replace dash inside double quotes
        :param line: str
        :param replace_with: str
        :rtype : str
        """
        if '"' in line:
            line = line.split('"')
            for k, i in enumerate(line):
                if k % 2 and ',' in i:
                    line[k] = i.replace(',', replace_with)

            line = ''.join(line)

        return line

    @classmethod
    def split_lines_with_dash(cls, line):
        """
        Split a str line into list items
        :rtype : list
        """
        return map(lambda x: x.rstrip(), line.split(','))

    @classmethod
    def remove_bracket_then_add_negative(cls, item):
        """
        Using input item return no brackets str
        :param item: str
        :return: str
        """
        try:
            if item[0] == '(' and item[-1] == ')':
                item = '-' + item[1:-1]
        except IndexError:
            item = item

        return item

    @classmethod
    def remove_dollar_symbols(cls, item):
        """
        Using input item return  a no dollar symbol str
        :type item: str
        :rtype : str
        """
        return item.replace('$', '')

    @classmethod
    def remove_percent_symbols(cls, item):
        """
        Using input item return a no percent str
        :param item: str
        :return: str
        """
        return item.replace('%', '')

    @classmethod
    def remove_brackets_only(cls, items):
        """
        Remove brackets on first item of a list
        :param items: str
        :return: str
        """
        return items.replace('(', '').replace(')', '')

    @classmethod
    def split_str_with_space(cls, item):
        """
        Split str item into list
        :param item: str
        :return: list
        """
        return item.split(' ')

    @classmethod
    def last_five_lines(cls, lines):
        """
        Return the last 5 lines on a lines list
        :rtype : list
        """
        return lines[-5:]

    @classmethod
    def convert_float_or_str(cls, item):
        """
        Make item into str or float
        :param item: str
        :return: str, float
        """
        try:
            result = float(item)
        except ValueError:
            result = str(item)

        return result

    def format_item(self, item):
        """
        Format single item that
        remove open close bracket then replace negative
        remove dollar sign
        remove percentage sign
        convert into float or string
        :param item: str
        :return: str, float
        """
        result = self.remove_bracket_then_add_negative(item)
        result = self.remove_dollar_symbols(result)
        result = self.remove_percent_symbols(result)
        result = self.convert_float_or_str(result)

        return result

    def get_lines(self, start_phrase, end_phrase=None):
        """
        Get lines from list using start phrase and end phrase
        :param start_phrase:
        :param end_phrase:
        :return: list
        """
        start = 0
        try:
            start = [key for key, line in enumerate(self.lines)
                     if start_phrase in line].pop(0)

            if end_phrase:
                end = [key for key, line in enumerate(self.lines[start:])
                       if end_phrase in line].pop(0)
            else:
                # using blank line
                end = [key for key, line in enumerate(self.lines[start:])
                       if len(line) == 0].pop(0)

            lines = self.lines[start:start+end+1]
        except IndexError:
            if start:
                lines = self.lines[start:]
            else:
                lines = list()

        return lines

    @classmethod
    def make_dict(cls, keys, values):
        """
        Make a dict from columns and values
        :param keys: list
        :param values: list
        """
        return {key: value for key, value in zip(keys, values)}

    @classmethod
    def del_empty_keys(cls, x):
        """
        Delete empty key '' in a dict
        :param x: dict
        :return: dict
        """
        return {key: value for key, value in x.items() if key != ''}

    @classmethod
    def fillna_dict(cls, prop):
        """
        Use trade history then fill empty with value row above
        """
        df = DataFrame(prop)
        df = df.replace(['', 'DEBIT', 'CREDIT'], numpy.nan)
        df = df.fillna(method='ffill')

        return [r.to_dict() for k, r in df.iterrows()]

    @classmethod
    def fillna_dict_with_exists(cls, prop_obj, key_exists, columns):
        """
        Fill none values if key not exists for column names
        :param prop_obj: list of dict
        :param key_exists: str
        :param columns: str
        :return: None
        """
        for key, item in enumerate(prop_obj):
            if not item[key_exists]:
                for column in columns:
                    prop_obj[key][column] = prop_obj[key - 1][column]

            for sub_key, sub_value in item.items():
                if sub_value == 'DEBIT' or sub_value == 'CREDIT':
                    item[sub_key] = 0.0

    @classmethod
    def convert_specific_type(cls, prop_obj, column_name, specific_type, empty_value):
        """
        Convert item for dict in list into specific type
        :param prop_obj: list
        :param column_name: str
        :param specific_type: type
        :return: None
        """
        for key, item in enumerate(prop_obj):
            if item[column_name]:
                prop_obj[key][column_name] = specific_type(item[column_name])
            else:
                prop_obj[key][column_name] = empty_value

    def set_values(self, start_phrase, end_phrase, start_with, end_until, prop_keys, prop_name):
        """
        Make a dict from file lines for single section
        then save it into class property
        :param start_phrase: str
        :param end_phrase: str
        :param start_with: int
        :param end_until: int
        :param prop_keys: list
        :param prop_name: str
        :return: None
        """
        prop_list = list()

        lines = self.get_lines(start_phrase, end_phrase)

        for line in lines[start_with:end_until]:
            line = self.replace_dash_inside_quote(line)
            items = self.split_lines_with_dash(line)

            items = map(self.format_item, items)

            prop_list.append(self.make_dict(prop_keys, items))

        setattr(self, prop_name, prop_list)
