from exchange.OrderBook import OrderBook
from market_data.MarketDataPublisherUDP_Unicast import MarketDataPublisher
from pkg.common.Order import *
import asyncore

# Exchange's internal orderbook
class Exchange:

    orderID = 0

    def __init__(self):
        print("Initialising Exchange")
        self.lob = OrderBook("SMBL")
        self.market_publisher = MarketDataPublisher(True)

    def gen_order_id(self) -> int:
        self.orderID = self.orderID + 1
        return self.orderID

    def create_order(self, so: SessionOrder):
        print('\nORDER REQUEST (T=%5.2f): %s' % (so.timestamp, so.order))

        ack_order, trades = self.lob.add(so)

        # publish market data
        self.market_publisher.broadcast(self.lob.publish())

        return ack_order, trades

    def cancel_order(self, ClOrdID: int):
        print('\nCANCEL REQUEST: %d' % ClOrdID)

        so = self.lob.get_by_ClOrdID(ClOrdID)
        if so is not None:
            ack = self.lob.delete(so)

            # publish market data
            self.market_publisher.broadcast(self.lob.publish())

        self.lob.publish()
