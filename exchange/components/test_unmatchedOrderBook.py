from unittest import TestCase

from exchange.components.order import Order, OrderType
from exchange.components.unmatched_order_book import UnmatchedOrderBook


class TestUnmatchedOrderBook(TestCase):
    def test_add_buy_order(self):
        buy_order = Order(111, 100, OrderType.BUY)

        unmatched_order_book = UnmatchedOrderBook()

        unmatched_order_book.add_buy_order(buy_order)

        self.assertEqual(unmatched_order_book.peek_best_buy_order().price, 111)

    def test_peek_emty(self):
        unmatched_order_book = UnmatchedOrderBook()

        self.assertIsNone(unmatched_order_book.peek_best_buy_order())

    def test_best_buy_order(self):
        # Add items in non-sequential order to ensure sorting
        unmatched_order_book = UnmatchedOrderBook()
        unmatched_order_book.add_buy_order(Order(222, 100, OrderType.BUY))
        unmatched_order_book.add_buy_order(Order(333, 100, OrderType.BUY))
        unmatched_order_book.add_buy_order(Order(111, 100, OrderType.BUY))

        # Store the id of the highest priced first in order that we expect to see first
        first_in_highest_price_buy_order = Order(555, 100, OrderType.BUY)
        expected_id = first_in_highest_price_buy_order.id
        unmatched_order_book.add_buy_order(first_in_highest_price_buy_order)

        # Put another unmatched order in at the same high price
        unmatched_order_book.add_buy_order(Order(555, 100, OrderType.BUY))

        # Add another lower price at the end
        unmatched_order_book.add_buy_order(Order(333, 100, OrderType.BUY))

        self.assertEqual(unmatched_order_book.peek_best_buy_order().id, expected_id)

        # Ensure that the same order is pulled out again
        self.assertEqual(unmatched_order_book.peek_best_buy_order().id, expected_id)

        # Ensure that popping returns a different order
        unmatched_order_book.pop_best_buy_order()
        self.assertNotEqual(unmatched_order_book.peek_best_buy_order(), expected_id)

    def test_get_summary_does_not_modify_queue_while_calculating_summary(self):
        unmatched_order_book = UnmatchedOrderBook()

        first_order = Order(100, 100, OrderType.BUY)
        unmatched_order_book.add_buy_order(first_order)

        second_order = Order(100, 100, OrderType.BUY)
        unmatched_order_book.add_buy_order(second_order)

        third_order = Order(100, 100, OrderType.BUY)
        unmatched_order_book.add_buy_order(third_order)

        fourth_low_buy_order = Order(1, 100, OrderType.BUY)
        unmatched_order_book.add_buy_order(fourth_low_buy_order)

        unmatched_order_book.get_summary()

        self.assertEqual(unmatched_order_book.pop_best_buy_order(), first_order)
        self.assertEqual(unmatched_order_book.pop_best_buy_order(), second_order)
        self.assertEqual(unmatched_order_book.pop_best_buy_order(), third_order)
        self.assertEqual(unmatched_order_book.pop_best_buy_order(), fourth_low_buy_order)
