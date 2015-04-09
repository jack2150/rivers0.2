dates = (
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
    return True if date in dates else False


def is_not_offdays(date):
    """
    Check date is market trading day
    :param date: str
    :return: boolean
    """
    return False if date in dates else True
