from apscheduler.schedulers.background import BackgroundScheduler

from exchange.OrderBook import OrderBook
from market_data.MarketDataPublisherUDP_Unicast import MarketDataPublisher
from pkg.common.Order import *


# Exchange's internal orderbook
class Exchange:

    orderID = 0

    def __init__(self):
        print("Initialising Exchange")
        self.lob = OrderBook("SMBL")
        self.previous_lob = self.lob.publish()
        self.market_publisher = MarketDataPublisher(True)

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=self.__override,
            name="Time Scheduler",
            trigger='interval',
            seconds=5,
        )
        scheduler.start()

    def gen_order_id(self) -> int:
        self.orderID = self.orderID + 1
        return self.orderID

    def create_order(self, so: SessionOrder):
        print('\nORDER REQUEST (T=%5.2f): %s' % (so.timestamp, so.order))

        ack_order, trades = self.lob.add(so)

        # publish market data
        lob = self.lob.publish()
        if self.__lob_change(lob):
            self.market_publisher.broadcast(lob)

        return ack_order, trades

    def cancel_order(self, session_id: str, ClOrdID: int):
        print('\nCANCEL REQUEST: %s %d' % (session_id, ClOrdID))

        so = self.lob.get_by_ClOrdID(session_id, ClOrdID)
        if so is not None:
            ack = self.lob.delete(so)

            # publish market data
            lob = self.lob.publish()
            if self.__lob_change(lob):
                self.market_publisher.broadcast(lob)
        else:
            print("WARNING: FAILED TO FIND ORDER")

    def __override(self):
        self.market_publisher.broadcast(self.lob.publish())

    def __lob_change(self, lob):
        change = lob["bids"]["best"] != self.previous_lob["bids"]["best"] or \
            lob["bids"]["worst"] != self.previous_lob["bids"]["worst"] or \
            lob["asks"]["best"] != self.previous_lob["asks"]["best"] or \
            lob["asks"]["worst"] != self.previous_lob["asks"]["worst"]

        if change:
            self.previous_lob = lob

        return change
