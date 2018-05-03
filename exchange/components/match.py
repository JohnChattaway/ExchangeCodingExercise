import json


class Match:
    """
    One Order can be matched against many smaller Orders at differing prices.
    Match keeps track of a single Match between two orders at a single price.
    """
    def __init__(self, buy_order, sell_order, size, price):
        self.buy_order = buy_order
        self.sell_order = sell_order
        self.size = size
        self.price = price

    def get_summary(self):
        summary = dict()

        summary['buy_order_id'] = self.buy_order.id
        summary['sell_order_id'] = self.sell_order.id
        summary['size'] = self.size
        summary['price'] = self.price

        return summary
