class SavePosition(object):
    """
    A position come with
    1. a position start
    1.1 filled order 'to open'
    1.2 position statement record
    1.3 account statement record

    1.* either can be a equity, option, or spread
        (future and forex skip, build later)



    end. with or without filled order 'to close'

    a. it can search a position using symbol or date or both


    structure, single position contain:
    1 filled order 'to open' cannot be null
    * many position instrument
    * many profit loss
    1 filled order 'to close' can be null

    """
    def __init__(self,):
        pass

    def save_all(self):
        """

        :return:
        """
        pass