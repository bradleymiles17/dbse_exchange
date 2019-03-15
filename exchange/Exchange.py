from pkg.common.Orderbook import Orderbook
from pkg.common.Order import *
from pkg.common.OrderBookResponse import *
from pkg.common.MarketDataEvent import *

import time

# Exchange's internal orderbook
class Exchange:
    lob = Orderbook("BAM")

    # REFACTOR INTO UDP BROADCAST
    def transaction_observer(self, response: OrderBookResponse):
        print(response)

    def marketdata_observer(self, market_data: MarketDataEvent):
        print(market_data)

    def __init__(self, debug):
        super().__init__()
        self.verbose = debug

    def __is_limit_order_executable(self, order: Order, opposite_order: Order):
        if order.side == Side.BID:
            return order.price >= opposite_order.price
        else:
            return order.price <= opposite_order.price

    def CreateOrder(self, order: Order):
        order.exchange_id = self.lob.get_next_exchange_id()
        self.transaction_observer(Acknowledged(time.time(), order.exchange_id))

        trades = self.lob.add(order)
        lob = self.publish_lob()

        for t in trades:
            print(t)

        print(lob)

        # report on trades

    def ModifyOrder(self, order_id, price, qty):
        print("Amend Request")

    def CancelOrder(self, exchange_id: int):
        print("Cancel Request")

        removed = self.lob.delete(exchange_id)

        if removed:
            self.transaction_observer(Acknowledged(time.time(), exchange_id))
        else:
            self.transaction_observer(Rejected(time.time(), "Order not found", exchange_id))


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
            'QID': self.lob.exchange_id
            # 'tape': self.transactionObserver
        }

        return public_data
