from lib.io.open_csv import OpenCSV


class OpenTA(OpenCSV):
    def __init__(self, fname):
        OpenCSV.__init__(self, fname)

        self.working_order_keys = [
            '', '', 'time_placed', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike', 'contract',
            'price', 'order', 'tif', 'mark', 'status',
        ]

        self.filled_order_keys = [
            '', 'exec_time', 'spread', 'side', 'quantity', 'pos_effect',
            'symbol', 'expire_date', 'strike', 'contract', 'price',
            'net_price', 'order'
        ]

        self.cancelled_order_keys = [
            '', '', 'time_cancelled', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike', 'contract',
            'price', 'order', 'tif', 'status'
        ]

        self.rolling_strategy_keys = [
            'position', 'new_expire_date', 'call_by', 'days_begin', 'order_price',
            'active_time', 'move_to_market_time', 'status'
        ]

        self.working_order = list()
        self.filled_order = list()
        self.cancelled_order = list()
        self.rolling_strategy = list()

    def set_working_order(self):
        """
        Set working_order into class property
        :return: None
        """
        self.set_values(
            start_phrase='Working Orders',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.working_order_keys,
            prop_name='working_order'
        )

        self.working_order = map(self.del_empty_keys, self.working_order)

    def set_filled_order(self):
        """
        Set equity into class property
        :return: None
        """
        self.set_values(
            start_phrase='Filled Orders',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.filled_order_keys,
            prop_name='filled_order'
        )

        self.filled_order = map(self.del_empty_keys, self.filled_order)
        self.filled_order = self.fillna_dict(self.filled_order)

    def set_cancelled_order(self):
        """
        Set cancelled_orders into class property
        :return: None
        """
        self.set_values(
            start_phrase='Cancelled Orders',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.cancelled_order_keys,
            prop_name='cancelled_order'
        )

        self.cancelled_order = map(self.del_empty_keys, self.cancelled_order)
        self.cancelled_order = self.fillna_dict(self.cancelled_order)

    def set_rolling_strategy(self):
        """
        Set rolling_strategy into class property
        :return: None
        """
        self.set_values(
            start_phrase='Rolling Strategies',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.rolling_strategy_keys,
            prop_name='rolling_strategy'
        )

        self.rolling_strategy = map(self.del_empty_keys, self.rolling_strategy)

    def read(self):
        """
        Most important method, read file then return data
        :return: dict
        """
        self.set_working_order()
        self.set_filled_order()
        self.set_cancelled_order()
        self.set_rolling_strategy()

        return dict(
            working_order=self.working_order,
            filled_order=self.filled_order,
            cancelled_order=self.cancelled_order,
            rolling_strategy=self.rolling_strategy
        )
















