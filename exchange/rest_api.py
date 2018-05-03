from flask import Flask, jsonify, request, abort

from exchange.components.exchange import Exchange
from exchange.components.order import OrderType

app = Flask(__name__)

exchange = Exchange()


@app.route('/order', methods=['POST'])
def submit_limit_order():
    if not request.json or 'price' not in request.json or 'size' not in request.json or 'order_type' not in request.json:
        abort(400)

    if request.json['order_type'] == OrderType.BUY.value:
        order_id = exchange.submit_buy(
            size=int(request.json['size']),
            price=int(request.json['price'])
        )

        return jsonify({'order_id': order_id})

    if request.json['order_type'] == OrderType.SELL.value:
        order_id = exchange.submit_sell(
            size=int(request.json['size']),
            price=int(request.json['price'])
        )

        return jsonify({'order_id': order_id})

    # We only support buy or sell orders
    abort(400)


@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    order = exchange.find_order(order_id)

    if not order:
        abort(404)

    return jsonify(order.get_summary())


@app.route('/orderBook', methods=['GET'])
def get_order_book():
    summary = exchange.get_exchange_summary()

    for_json = dict()

    for_json['BUY'] = summary.buy_dict
    for_json['SELL'] = summary.sell_dict

    return jsonify(for_json)


if __name__ == '__main__':
    # Exchange is not thread safe, ensure single thread
    # host 0.0.0.0 for docker
    app.run(debug=True, threaded=False, host='0.0.0.0')
