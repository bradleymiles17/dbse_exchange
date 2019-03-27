from exchange.OrderBook import OrderBook
from market_data.MarketDataPublisher import MarketDataPublisher
from pkg.common.Order import *


# Exchange's internal orderbook
class Exchange:

    orderID = 0

    def __init__(self):
        print("Initialising Exchange")
        self.lob = OrderBook("SMBL")
        self.market_publisher = MarketDataPublisher()

    def gen_order_id(self) -> int:
        self.orderID = self.orderID + 1
        return self.orderID

    def create_order(self, so: SessionOrder):
        print('\nORDER REQUEST (T=%5.2f): %s' % (so.timestamp, so.order))

        ack_order, trades = self.lob.add(so)

        # publish market data
        self.market_publisher.add_lob_update_event(self.lob.publish())

        return ack_order, trades

    def modify_order(self, order_id, price, qty):
        print("Amend Request")

    def cancel_order(self, id: int):
        print("Cancel Request")
        removed = self.lob.delete(id)
