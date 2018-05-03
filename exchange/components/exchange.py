"""
This is the core exchange class

Orders are matched at the price on the exchange. 
   - If we have a sell order at 200 and a buy order comes in at 1000 we will sell at 200
   - If we have a buy order at 200 and a sell order comes in at 50 we will sell at 200
"""
from exchange.components.match import Match
from exchange.components.order import Order, OrderType
from exchange.components.unmatched_order_book import UnmatchedOrderBook


class Exchange:
    def __init__(self):
        self._unmatched_order_book = UnmatchedOrderBook()

        # Need to store pointers to all orders, including those in the order book and those that have been executed
        self._all_orders = dict()

    def submit_buy(self, size, price):
        buy_order = Order(
            price=price,
            size=size,
            order_type=OrderType.BUY
        )

        # Store the buy order forever in the data store
        self._all_orders[buy_order.id] = buy_order

        self._execute_and_or_store_buy_order(buy_order)

        return buy_order.id

    def submit_sell(self, size, price):
        sell_order = Order(
            price=price,
            size=size,
            order_type=OrderType.SELL
        )

        self._all_orders[sell_order.id] = sell_order

        self._execute_and_or_store_sell_order(sell_order)

        return sell_order.id

    def find_order(self, order_id):
        """find will return the object or None"""
        if order_id not in self._all_orders:
            return None

        return self.get_order(order_id)

    def get_order(self, order_id):
        """get will return the object or error (Don't worry about None in downstream code)"""
        return self._all_orders[order_id]

    def get_exchange_summary(self):
        return self._unmatched_order_book.get_summary()

    def _execute_and_or_store_buy_order(self, buy_order):
        """
        Execute and or store a buy order in the unmatched_order_book

        This is not atomic. If it fails then stop everything because the order book and map of orders will be in an
        inconsistent state.

        In the real world I would use the persistent data store (database) to ensure atomicity, either transactions if
        using SQL or eventually consistent systems if using MongoDB.

        :param size: int number of units
        :param price: int in pence
        """
        best_sell = self._unmatched_order_book.peek_best_sell_order()

        # If buy_order has unmatched size of 0 then it was fully executed and never has to go onto the order book.
        while buy_order.get_unmatched_size() > 0:
            # Can't match because no sell orders
            if best_sell is None:
                self._unmatched_order_book.add_buy_order(buy_order)
                return

            # Can't match because sell price greater than buy price
            if best_sell.price > buy_order.price:
                self._unmatched_order_book.add_buy_order(buy_order)
                return

            # We can start executing the order immediately
            if best_sell.price <= buy_order.price:
                match = Match(
                    buy_order=buy_order,
                    sell_order=best_sell,
                    price=best_sell.price,
                    size=min([buy_order.get_unmatched_size(), best_sell.get_unmatched_size()])
                )
                buy_order.add_match(match)
                best_sell.add_match(match)

                # If the sell order was fully executed then pop it off the order book and get the new best
                # unmatched sell order
                if best_sell.get_unmatched_size() <= 0:
                    self._unmatched_order_book.pop_best_sell_order()
                    best_sell = self._unmatched_order_book.peek_best_sell_order()

    def _execute_and_or_store_sell_order(self, sell_order):
        """
        Execute and or store a sell order in the unmatched_order_book

        This is not atomic. If it fails then stop everything because the order book and map of orders will be in an
        inconsistent state.

        In the real world I would use the persistent data store (database) to ensure atomicity, either transactions if
        using SQL or eventually consistent systems if using MongoDB.

        :param size: int number of units
        :param price: int in pence
        """
        best_buy = self._unmatched_order_book.peek_best_buy_order()

        # If buy_order has unmatched size of 0 then it was fully executed and never has to go onto the order book.
        while sell_order.get_unmatched_size() > 0:
            # Can't match because no sell orders
            if best_buy is None:
                self._unmatched_order_book.add_sell_order(sell_order)
                return

            # Can't match because sell price greater than buy price
            if best_buy.price < sell_order.price:
                self._unmatched_order_book.add_sell_order(sell_order)
                return

            # We can start executing the order immediately
            if best_buy.price >= sell_order.price:
                match = Match(
                    buy_order=best_buy,
                    sell_order=sell_order,
                    price=best_buy.price,
                    size=min([best_buy.get_unmatched_size(), sell_order.get_unmatched_size()])
                )
                best_buy.add_match(match)
                sell_order.add_match(match)

                # If the buy order was fully executed then pop it off the order book and get the new best
                # unmatched buy order
                if best_buy.get_unmatched_size() <= 0:
                    self._unmatched_order_book.pop_best_buy_order()
                    best_buy = self._unmatched_order_book.peek_best_buy_order()



