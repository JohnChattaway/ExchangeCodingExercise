from sortedcontainers import SortedDict
from collections import deque


class UnmatchedOrderBook:
    """
    Class to hold the unmatched orders

    Never put an order that can be matched into this order book. Orders come in and they are either executed
    immediately, stored or partially executed and the remainder is stored. This is an UnmatchedOrderBook
    """
    def __init__(self):
        # orders will be stored in a SortedDict of Queues. The price will be the key to the sorted dict
        # The lowest / highest price is at the start / end of the SortedDict
        # SortedDict maintains a sorted list of the keys, sorting on insertion.
        self._buy_orders = SortedDict()
        self._sell_orders = SortedDict()

    def add_sell_order(self, order):
        self.__add_order(self._sell_orders, order)

    def add_buy_order(self, order):
        self.__add_order(self._buy_orders, order)

    def peek_best_buy_order(self):
        """
        Best buy order has the highest price and is at the front of the queue at that price.
        Keep the returned Order object in the queue
        :return: Order
        """
        # There might not be any orders
        if not self._buy_orders:
            return None

        # Get the last (highest pried) item from it's queue in the SortedDict
        price, queue = self._buy_orders.peekitem()
        return queue[0]

    def peek_best_sell_order(self):
        """
        Best sell order has the lowest price and is at the front of the queue at that price.
        Keep the returned Order object in the queue
        :return: Order
        """
        # There might not be any orders
        if not self._sell_orders:
            return None

        # Get the first (lowest pried) item from it's queue in the SortedDict
        price, queue = self._sell_orders.peekitem(0)
        return queue[0]

    def pop_best_buy_order(self):
        """
        Best buy order has the highest price and is at the front of the queue at that price.
        Delete the returned Order object from the queue
        :return: Order
        """
        # There might not be any orders
        if not self._buy_orders:
            return None

        price, queue = self._buy_orders.peekitem()

        best_price_order = queue.popleft()

        # delete the key from the orderbook if there are no more orders at that price (deque is empty)
        if not queue:
            del self._buy_orders[price]

        return best_price_order

    def pop_best_sell_order(self):
        # There might not be any orders
        if not self._sell_orders:
            return None

        price, queue = self._sell_orders.peekitem(0)

        best_price_order = queue.popleft()

        # delete the key from the orderbook if there are no more orders at that price (deque is empty)
        if not queue:
            del self._sell_orders[price]

        return best_price_order

    def get_summary(self):
        summary = UnmatchedOrderBookSummary()

        summary.buy_dict = self.__summarise_order_dict(self._buy_orders)
        summary.sell_dict = self.__summarise_order_dict(self._sell_orders)

        return summary

    @staticmethod
    def __summarise_order_dict(order_dict):
        order_dict_summary = SortedDict()

        for price in order_dict.iterkeys():

            total_size = 0
            new_queue = deque()

            for order in order_dict[price]:
                new_queue.append(order)
                total_size += order.get_unmatched_size()

                order_dict[price] = new_queue

            order_dict_summary[price] = total_size

        return order_dict_summary

    @staticmethod
    def __add_order(sorted_dict, order):
        # No current orders at this price, create a new queue at this price containing the orders
        if order.price not in sorted_dict:
            sorted_dict[order.price] = deque([order])
            return

        # Add the order to the queue at it's price
        sorted_dict[order.price].append(order)


class UnmatchedOrderBookSummary:
    """
    Summary contains two dicts, one for buy and one for sell.
    The key is the price
    The value is the size
    """
    def __init__(self):
        self.buy_dict = SortedDict()
        self.sell_dict = SortedDict()
