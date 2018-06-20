Coding Exercise 
===============

Write a simple exchange app with a REST API that trades a single stock.
Create three endpoints:
- Submit a limit order, buy and sell
- Retrieve order details
- Return a summary of the open order book

Docker
======

# Docker build
# Adjust path as appropriate
sudo docker build -t chattaway-exchange:latest /home/john/PycharmProjects/LendingBlock

# Docker run
sudo docker run -d chattaway-exchange

# Get IP address
sudo docker ps
sudo docker inspect <container_id> | grep IPAddress



API usage example
=================
# I used postman, submitting the POST body as raw JSON(application/json)

# Submit sell order
POST: http://172.17.0.2:5000/order
BODY:
{
	"price":20,
	"size":200,
	"order_type":"SELL"
}
RESPONSE:
{
    "order_id": "b626e72c4da44e118388297a39a644d9"
}

# Submit buy order
POST: http://172.17.0.2:5000/order
BODY:
{
	"price":30,
	"size":20,
	"order_type":"BUY"
}
RESPONSE:
{
    "order_id": "7aca862e34d749bfba6ecf8eecec83db"
}

# Show the sell order
GET: http://172.17.0.2:5000/order/6b1b0713ff40424698590352148eb310
RESPONSE:
{
    "matches": [
        {
            "buy_order_id": "7aca862e34d749bfba6ecf8eecec83db",
            "price": 20,
            "sell_order_id": "b626e72c4da44e118388297a39a644d9",
            "size": 20
        }
    ],
    "order_type": "SELL",
    "price": 20,
    "size": 200,
    "unmatched_size": 180
}

# Show exchange summary
GET: http://172.17.0.2:5000/orderBook
RESPONSE:
{
    "BUY": {},
    "SELL": {
        "20": 180
    }
}


