from datetime import datetime

market_offdays = (
    '01/21/11',
    '05/04/11',
    '08/12/11',
    '10/19/12',
    '02/28/14',
    '07/18/14',
    '10/10/14',
    '01/19/15',
    '02/16/15',
    '03/09/15',
    '04/03/15',
)


def is_offdays(date):
    """
    Check date is market non trading day
    :param date: str
    :return: boolean
    """
    if type(date) == datetime:
        date = date.strftime('%m/%d/%y')

    return True if date in market_offdays else False


def is_not_offdays(date):
    """
    Check date is market trading day
    :param date: str
    :return: boolean
    """
    if type(date) == datetime:
        date = date.strftime('%m/%d/%y')

    return True if date not in market_offdays else False
