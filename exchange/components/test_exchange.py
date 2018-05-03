from unittest import TestCase

from sortedcontainers import SortedDict

from exchange.components.exchange import Exchange


class TestExchange(TestCase):
    def test_get_order(self):
        exchange = Exchange()
        order_id = exchange.submit_sell(size=10, price=100)
        retrieved_order = exchange.get_order(order_id)

        self.assertEqual(retrieved_order.get_unmatched_size(), 10)
        self.assertEqual(retrieved_order.price, 100)

    def test_submit_buy_everything_then_store_remaining_buy_order(self):
        exchange = Exchange()

        exchange.submit_sell(size=10, price=30)
        exchange.submit_sell(size=10, price=20)
        exchange.submit_sell(size=10, price=10)

        self.assertEqual(exchange.get_exchange_summary().sell_dict, SortedDict({10: 10, 20: 10, 30: 10}))

        # Buy everything on the exchange
        buy_order_id = exchange.submit_buy(size=40, price=40)

        self.assertEqual(exchange.get_order(buy_order_id).get_unmatched_size(), 10)

        self.assertEqual(exchange.get_exchange_summary().buy_dict, SortedDict({40: 10}))
        self.assertEqual(exchange.get_exchange_summary().sell_dict, SortedDict())

    def test_sequence_buy_and_sell(self):
        exchange = Exchange()

        exchange.submit_buy(size=50, price=400)
        exchange.submit_sell(size=10, price=200)
        exchange.submit_buy(size=10, price=450)
        exchange.submit_sell(size=5, price=200)
        exchange.submit_sell(size=30, price=500)
        exchange.submit_buy(size=5, price=500)
        exchange.submit_buy(size=40, price=300)

        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({300: 40, 400: 40, 450: 5}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({500: 25}))

    def test_realistic_buy_sell(self):
        # price about 150
        exchange = Exchange()

        exchange.submit_buy(size=30, price=148)
        exchange.submit_buy(size=40, price=148)
        exchange.submit_buy(size=80, price=148)
        exchange.submit_buy(size=10, price=148)
        exchange.submit_buy(size=10, price=148)
        exchange.submit_buy(size=20, price=148)
        exchange.submit_buy(size=30, price=149)
        exchange.submit_buy(size=10, price=149)
        exchange.submit_buy(size=10, price=149)
        exchange.submit_buy(size=20, price=149)
        exchange.submit_buy(size=10, price=150)
        exchange.submit_buy(size=20, price=150)

        exchange.submit_sell(size=10, price=151)
        exchange.submit_sell(size=20, price=151)
        exchange.submit_sell(size=40, price=151)
        exchange.submit_sell(size=10, price=152)
        exchange.submit_sell(size=10, price=152)
        exchange.submit_sell(size=20, price=152)
        exchange.submit_sell(size=30, price=152)
        exchange.submit_sell(size=10, price=152)
        exchange.submit_sell(size=10, price=153)
        exchange.submit_sell(size=20, price=153)
        exchange.submit_sell(size=10, price=153)
        exchange.submit_sell(size=20, price=153)
        exchange.submit_sell(size=80, price=153)

        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70, 150: 30}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({151: 70, 152: 80, 153: 140}))

        # Buy 1 should execute completely
        buy1_id = exchange.submit_buy(size=5, price=151)
        buy1 = exchange.get_order(buy1_id)
        self.assertEquals(buy1.get_unmatched_size(), 0)
        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70, 150: 30}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({151: 65, 152: 80, 153: 140}))

        # Buy 2 should execute completely
        buy2_id = exchange.submit_buy(size=15, price=151)
        buy2 = exchange.get_order(buy2_id)
        self.assertEquals(buy2.get_unmatched_size(), 0)
        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70, 150: 30}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({151: 50, 152: 80, 153: 140}))

        # sell2 should execute completely
        sell1_id = exchange.submit_sell(size=5, price=150)
        sell1 = exchange.get_order(sell1_id)
        self.assertEquals(sell1.get_unmatched_size(), 0)
        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70, 150: 25}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({151: 50, 152: 80, 153: 140}))

        # sell2 should shift the price of the exchange and become the best sell order
        sell2_id = exchange.submit_sell(size=40, price=150)
        sell2 = exchange.get_order(sell2_id)
        self.assertEquals(sell2.get_unmatched_size(), 15)
        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({150: 15, 151: 50, 152: 80, 153: 140}))

        # buy3 should match with sell 2 and shift the exchange price
        buy3_id = exchange.submit_buy(size=25, price=150)
        buy3 = exchange.get_order(buy3_id)
        self.assertEquals(buy3._matches[0].sell_order, sell2)
        # sell2 should now be fully matched
        self.assertEquals(sell2.get_unmatched_size(), 0)

        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({148: 190, 149: 70, 150: 10}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({151: 50, 152: 80, 153: 140}))

    def test_negative_amounts_and_prices(self):
        exchange = Exchange()

        with self.assertRaises(ValueError):
            exchange.submit_buy(price=-23, size=30)
            exchange.submit_buy(price=100, size=-3330)
            exchange.submit_sell(price=-33, size=300)
            exchange.submit_sell(price=100, size=-999)
            exchange.submit_sell(price=0, size=100)
            exchange.submit_sell(price=10, size=0)

    def test_big_numbers(self):
        exchange = Exchange()

        exchange.submit_buy(price=9223372036854775808, size=10)
        exchange.submit_sell(price=9223372036854775809, size=10)

        self.assertEquals(exchange.get_exchange_summary().buy_dict, SortedDict({9223372036854775808: 10}))
        self.assertEquals(exchange.get_exchange_summary().sell_dict, SortedDict({9223372036854775809: 10}))

    def test_find_order(self):
        exchange = Exchange()
        self.assertIsNone(exchange.find_order('I dont exist'))

        order_id = exchange.submit_sell(size=10, price=30)

        self.assertIsNotNone(exchange.find_order(order_id))
