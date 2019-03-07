from collections import Counter

from cats_sqlalhemy import Cats


ATTRIBUTES = Cats.__table__.columns.keys()
ORDERS = ("asc", "desc")


def moda(data: list) -> list:
    moda_dict = Counter(data)
    number_repeats = list(moda_dict.values())
    count_max = number_repeats.count(max(number_repeats))
    return [elem[0] for elem in moda_dict.most_common(count_max)]


def is_positive(num):
    if num is None:
        return None
    if int(num) < 0:
        raise ValueError
    else:
        return num


def validate_attribute(attribute: str, data: dict, func=None):
    attr = None
    if attribute in data:
        if len(data[attribute]) > 1:
            raise ValueError

        attr = data[attribute][0]

        if func:
            if not func(attr):
                raise ValueError

    return attr


def validate_cats_params(data: dict):

    attribute = validate_attribute("attribute", data, func=lambda x: x in ATTRIBUTES)
    order = validate_attribute("order", data, func=lambda x: x in ORDERS)

    offset = validate_attribute("offset", data, func=is_positive)
    limit = validate_attribute("limit", data, func=is_positive)

    return attribute, order, offset, limit
