from calendar import month_name
from tos_import.classes.io import OpenCSV


class OpenThinkBack(OpenCSV):
    STOCK_KEYS = ['date', 'last', 'net_change', 'volume', 'open', 'high', 'low']
    SEARCH_STR = 'Last,Net Chng,Volume,Open,High,Low'

    COLUMN_HEAD = r',,Last,Mark,Delta,Gamma,Theta,Vega,Theo Price,Impl Vol,Prob.ITM,Prob.OTM,' \
                  r'Prob.Touch,Volume,Open.Int,Intrinsic,Extrinsic,Option Code,Bid,Ask,Exp,' \
                  r'Strike,Bid,Ask,Last,Mark,Delta,Gamma,Theta,Vega,Theo Price,Impl Vol,Prob.ITM,' \
                  r'Prob.OTM,Prob.Touch,Volume,Open.Int,Intrinsic,Extrinsic,Option Code,,'

    CONTRACT_KEYS = ['ex_month', 'ex_year', 'right', 'special', 'amount',
                     'strike', 'side', 'option_code']

    OPTION_KEYS = ['date', 'dte',
                   'last', 'mark', 'bid', 'ask', 'delta', 'gamma', 'theta', 'vega',
                   'theo_price', 'impl_vol', 'prob_itm', 'prob_otm', 'prob_touch', 'volume',
                   'open_int', 'intrinsic', 'extrinsic']

    def __init__(self, date, data):
        OpenCSV.__init__(self, data)

        self.date = date

    def get_stock(self):
        """
        get underlying data from data
        :return: dict
        """
        values = self.split_lines_with_dash(
            self.replace_dash_inside_quote(
                self.lines[self.lines.index(self.SEARCH_STR) + 1]
            )
        )

        return {
            key: value for key, value in
            zip(self.STOCK_KEYS, [self.date] + map(float, values))
        }

    def get_cycles(self):
        """
        Get option cycle from data
        :return: list
        """
        cycles = list()
        months = [month_name[i+1][:3].upper() for i in range(12)]

        for key, line in enumerate(self.lines):
            if line[:3] in months:
                # get cycle data from line
                data = map(self.remove_brackets_only,
                           [l for l in line.split(' ') if l])

                # JAN 09  (11)  19/100 (US$ 3601.92)
                if 'US$' in data:
                    if data[4] in ['Weeklys', 'Mini']:
                        data = data[:5] + [float(data[6])]
                    else:
                        data = data[:4] + ['Standard', float(data[5])]
                else:
                    if len(data) == 4:
                        data.append('Standard')
                    data.append(0.0)

                data = [int(i) if 0 < k < 3 else i for k, i in enumerate(data)]
                dte = data.pop(2)

                # if not expire yet, add into cycle
                if dte > -1:
                    cycles.append(
                        dict(
                            line=line,
                            data=data,
                            dte=dte,
                            start=key + 1,
                            stop=0
                        )
                    )

                # previous stop
                if len(cycles) > 1:
                    cycles[len(cycles) - 2]['stop'] = key - 1
        else:
            cycles[len(cycles) - 1]['stop'] = len(self.lines) - 1

        return cycles

    def get_cycle_options(self, cycle):
        """
        Return a list of call put options data

        underlying.stock_set.add()
        underlying.

        :param cycle: dict
        :return: list of dict
        """
        calls = list()
        puts = list()

        if self.lines[cycle['start']] != self.COLUMN_HEAD:
            raise IOError('File have a invalid column format.')

        for line in self.lines[cycle['start']+1:cycle['stop']]:
            data = map(
                lambda x: 0.0 if x == '' else x,  # replace empty with zero
                map(lambda x: 0.0 if x == '--' or x == '++' else x,
                    self.split_lines_with_dash(
                        self.replace_dash_inside_quote(
                            line[2:-2].replace('%', '')
                        )
                    ))
            )

            """Bid,Ask,Exp,Strike,Bid,Ask"""
            calls.append((
                {
                    key: value for key, value in zip(
                        self.CONTRACT_KEYS,
                        cycle['data'] + [float(data[19]), 'CALL', data[15]]
                    )
                },
                {
                    key: value for key, value in zip(
                        self.OPTION_KEYS,
                        [self.date, cycle['dte']] + map(float, data[16:18] + data[:15])
                    )
                }
            ))

            puts.append((
                {
                    key: value for key, value in
                    zip(self.CONTRACT_KEYS, cycle['data'] + [float(data[19]), 'PUT', data[37]])
                },
                {
                    key: value for key, value in
                    zip(
                        self.OPTION_KEYS,
                        [self.date, cycle['dte']] + map(float, data[20:37])
                    )
                }
            ))

        return calls + puts

    def format(self):
        """
        Format the data then output dict that ready for insert
        :return: dict
        """
        stock = self.get_stock()
        options = list()

        for cycle in self.get_cycles():
            options += self.get_cycle_options(cycle)

        return stock, options
