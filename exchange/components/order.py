import uuid
from enum import Enum


class Order:
    """
    Class to keep track of each order
    """
    def __init__(self, price, size, order_type):
        if not isinstance(price, int):
            raise ValueError('Price must be an int in pence')

        if not isinstance(size, int):
            raise ValueError('Size must be an int')

        if price <= 0:
            raise ValueError('Price {0} must be greater than 0'.format(price))

        if size <= 0:
            raise ValueError('Size {0} must be greater than 0'.format(size))

        self.order_type = order_type
        self.price = price
        self._size = size

        # One large Order can be matched against several smaller orders at different prices.
        self._matches = []

        # Uniquely identify the order with a long random uuid.
        # The probability of collision is 10^-37
        # Generating true random numbers is hard and collisions can be observed in sets of 1 million uuids
        # uuids prevent end users guessing the ID of other objects in the REST API
        self.id = uuid.uuid4().hex

    def get_unmatched_size(self):
        """
        One order can be matched against n other orders.
        The Order is responsible for keeping track of it's own matches
        :return: int
        """
        if not self._matches:
            return self._size

        unmatched_size = self._size

        for match in self._matches:
            unmatched_size = unmatched_size - match.size

        return unmatched_size

    def add_match(self, match):
        self._matches.append(match)

    def get_summary(self):
        summary = dict()

        summary['size'] = self._size
        summary['price'] = self.price
        summary['order_type'] = self.order_type.value
        summary['unmatched_size'] = self.get_unmatched_size()

        matches = list()

        for match in self._matches:
            matches.append(match.get_summary())

        summary['matches'] = matches

        return summary


class OrderType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
