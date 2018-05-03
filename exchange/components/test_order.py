from unittest import TestCase

from exchange.components.match import Match
from exchange.components.order import Order, OrderType


class TestOrder(TestCase):
    def test_get_summary(self):
        order = Order(
            price=20,
            size=20,
            order_type=OrderType.BUY
        )

        order.id = '03a13310886d4ced9a28bc947ed56202'

        order.add_match(
            Match(
                buy_order=order,
                sell_order=order,
                size=10,
                price=20
            )
        )

        order.add_match(
            Match(
                buy_order=order,
                sell_order=order,
                size=5,
                price=20
            )
        )

        expected_dict = {'order_type': 'BUY', 'price': 20, 'size': 20, 'matches': [{'sell_order_id': '03a13310886d4ced9a28bc947ed56202', 'size': 10, 'price': 20, 'buy_order_id': '03a13310886d4ced9a28bc947ed56202'}, {'sell_order_id': '03a13310886d4ced9a28bc947ed56202', 'size': 5, 'price': 20, 'buy_order_id': '03a13310886d4ced9a28bc947ed56202'}], 'unmatched_size': 5}

        self.assertEqual(order.get_summary(), expected_dict)
