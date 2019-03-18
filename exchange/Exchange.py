from exchange.Orderbook import Orderbook
from pkg.common.Order import *
from pkg.common.OrderBookResponse import *

import time

# Exchange's internal orderbook
class Exchange:
    lob = Orderbook("BAM")

    def __init__(self, debug):
        super().__init__()
        self.verbose = debug

    def create_order(self, order: Order):
        print(Acknowledged(time.time(), order.id))

        trades = self.lob.add(order)
        lob = self.publish_lob()

        print(lob)

        return trades, lob

    def modify_order(self, order_id, price, qty):
        print("Amend Request")

    def cancel_order(self, exchange_id: int):
        print("Cancel Request")

        removed = self.lob.delete(exchange_id)

        if removed:
            print(Acknowledged(time.time(), exchange_id))
        else:
            print(Rejected(time.time(), "Order not found", exchange_id))

    def publish_orders(self):
        public_data = {
            'bids': self.lob.bids.get_orders(),
            'asks': self.lob.asks.get_orders()
        }

        return public_data

    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self):
        public_data = {
            'time': time.time(),
            'bids': {
                'best': self.lob.bids.get_best_price(),
                'worst': self.lob.bids.get_worst_price(),
                'order_n': self.lob.bids.get_order_n(),
                'qty': self.lob.bids.get_qty(),
                'lob': self.lob.bids.get_anonymize_lob()
            },
            'asks': {
                'best': self.lob.asks.get_best_price(),
                'worst': self.lob.asks.get_worst_price(),
                'order_n': self.lob.asks.get_order_n(),
                'qty': self.lob.asks.get_qty(),
                'lob': self.lob.asks.get_anonymize_lob()
            },
            # 'tape': self.lob.tape
        }

        return public_data
