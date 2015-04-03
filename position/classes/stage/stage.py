from position.models import PositionStage


# noinspection PyPep8Naming
class Stage(object):
    # down
    lt_price = '{current_price} < {price_a}'
    lt_price_lower = '{new_price} < {old_price} < {price_a}'
    lt_price_higher = '{old_price} < {new_price} < {price_a}'

    # down equal
    lte_price = '{current_price} <= {price_a}'
    lte_price_higher = '{old_price} < {new_price} <= {price_a}'
    lte_price_lower = '{new_price} < {old_price} <= {price_a}'

    # up
    gt_price = '{price_a} < {current_price}'
    gt_price_higher = '{price_a} < {old_price} < {new_price}'
    gt_price_lower = '{price_a} < {new_price} < {old_price}'

    # up equal
    gte_price = '{price_a} <= {current_price}'
    gte_price_higher = '{price_a} <= {old_price} < {new_price}'
    gte_price_lower = '{price_a} <= {new_price} < {old_price}'

    # even
    e_price = '{price_a} == {current_price}'

    # down range
    price_range = '{price_a} < {current_price} < {price_b}'
    price_range_higher = '{price_a} < {old_price} < {new_price} < {price_b}'
    price_range_lower = '{price_a} < {new_price} < {old_price} < {price_b}'

    e_price_range = '{price_a} <= {current_price} <= {price_b}'
    e_price_range_higher = '{price_a} <= {old_price} < {new_price} <= {price_b}'
    e_price_range_lower = '{price_a} <= {new_price} < {old_price} <= {price_b}'

    @staticmethod
    def EvenStage():
        """
        Create a max loss PositionStage
        :return: PositionStage
        """
        return PositionStage(
            stage_name='EVEN',
            left_status='',
            right_status=''
        )

    @staticmethod
    def ProfitStage():
        """
        Create a max loss PositionStage
        :return: PositionStage
        """
        return PositionStage(
            stage_name='PROFIT',
            left_status='DECREASING',
            right_status='PROFITING'
        )

    @staticmethod
    def LossStage():
        """
        Create a max loss PositionStage
        :return: PositionStage
        """
        return PositionStage(
            stage_name='LOSS',
            left_status='RECOVERING',
            right_status='LOSING'
        )

    @staticmethod
    def MaxProfitStage():
        """
        Create a max loss PositionStage
        :return: PositionStage
        """
        return PositionStage(
            stage_name='MAX_PROFIT',
            left_status='VANISHING',
            right_status='GUARANTEEING'
        )

    @staticmethod
    def MaxLossStage():
        """
        Create a max loss PositionStage
        :return: PositionStage
        """
        return PositionStage(
            stage_name='MAX_LOSS',
            left_status='EASING',
            right_status='WORST'
        )



