class Expression(object):
    # down
    less_than_price = '{current_price} < {price_a}'
    less_than_price_good = '{new_price} < {old_price} < {price_a}'
    lower_than_price_bad = '{old_price} < {new_price} < {price_a}'

    # down equal
    less_or_equal_than_price = '{current_price} <= {price_a}'
    less_or_equal_than_price_good = '{new_price} < {old_price} <= {price_a}'
    lower_or_equal_than_price_bad = '{old_price} < {new_price} <= {price_a}'

    # up
    greater_than_price = '{price_a} < {current_price}'
    greater_than_price_good = '{price_a} < {old_price} < {new_price}'
    greater_than_price_bad = '{price_a} < {new_price} < {old_price}'

    # up equal
    greater_or_equal_than_price = '{price_a} <= {current_price}'
    greater_or_equal_than_price_good = '{price_a} <= {old_price} < {new_price}'
    greater_or_equal_than_price_bad = '{price_a} <= {new_price} < {old_price}'

    # even
    equal_as_price = '{price_a} == {current_price}'
    equal_as_price_good = ''
    equal_as_price_bad = ''

    # down range
    less_than_price_range = '{price_a} < {current_price} < {price_b}'
    less_than_price_range_good = '{price_a} < {new_price} < {old_price} < {price_b}'
    less_than_price_range_bad = '{price_a} < {old_price} < {new_price} < {price_b}'

    # up range
    greater_than_price_range = '{price_a} > {current_price} > {price_b}'
    greater_than_price_range_good = '{price_a} > {old_price} > {new_price} > {price_b}'
    greater_than_price_range_bad = '{price_a} > {new_price} > {old_price} > {price_b}'










