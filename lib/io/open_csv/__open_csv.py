class OpenCSV(object):
    """
    All class methods in here
    """
    def __init__(self, fname):
        self.fname = fname

        self.lines = self.read_lines_from_file()

    def read_lines_from_file(self):
        """
        Read line from position file and
        remove new line at end of line
        :rtype : list
        """
        return map(lambda l: l.rstrip(), open(self.fname).readlines())

    @classmethod
    def replace_dash_inside_quote(cls, line):
        """
        Replace dash inside double quotes
        :rtype : str
        """
        if '"' in line:
            line = line.split('"')
            for k, i in enumerate(line):
                if k % 2 and ',' in i:
                    line[k] = i.replace(',', '')

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












