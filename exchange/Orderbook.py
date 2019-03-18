import functools

from pkg.common.Trade import Trade
from pkg.common.Order import *
from typing import List, Optional

# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_Half:

    def __init__(self, side: Side, worst_price):
        # booktype: bids or asks?
        # dictionary of orders received, indexed by Quote ID
        self.orders = []
        # limit order book, dictionary indexed by price, with order info
        self.lob = {}

        # summary stats
        self.side = side
        self.__worst_price = worst_price
        self.lob_depth = 0  # how many different prices on lob?

    def get_order(self, id: int) -> Optional[Order]:
        for i, order in enumerate(self.orders):
            if order.id == id:
                return self.orders[i]

        return None

    def get_orders(self) -> List[str]:
        return list(map(str, self.orders))

    def add_order(self, order: Order):
        def compare(item1, item2):
            if item1.price < item2.price:
                return -1
            elif item1.price > item2.price:
                return 1
            else:
                return 0

        temp = self.orders
        temp.append(order)
        self.orders = sorted(temp, key=functools.cmp_to_key(compare), reverse=(self.side == Side.BID))
        self._build_lob()

    def delete_order(self, order: Order):
        i = self.orders.index(order)
        if i is not None:
            del self.orders[i]
            self._build_lob()
        return True

    def get_best_price(self):
        if len(self.orders) > 0:
            return self.orders[0].price
        else:
            return None

    def get_worst_price(self):
        if len(self.orders) > 0:
            return self.orders[-1].price
        else:
            return None

    def get_best_order(self) -> Order:
        if len(self.orders) > 0:
            return self.orders[0]

    def get_order_n(self):
        return len(self.orders)

    def get_qty(self):
        qty = 0
        for order in self.orders:
            qty += order.remaining
        return qty

    def is_empty(self):
        return len(self.orders) == 0

    # anonymize a lob, strip out order details, format as a sorted list
    # NB for asks, the sorting should be reversed
    def get_anonymize_lob(self):
        lob_anon = []
        for price in sorted(self.lob, reverse=True) if (self.side == Side.BID) else sorted(self.lob):

            qty = 0
            for order in self.lob[price]:
                qty += order.remaining

            lob_anon.append([price, qty])

        return lob_anon

    # take a list of orders and build a limit-order-book (lob) from it
    # NB the exchange needs to know arrival times and trader-id associated with each order
    # returns lob as a dictionary (i.e., unsorted)
    # also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
    def _build_lob(self):
        self.lob = {}
        for order in self.orders:

            if order.price in self.lob:
                self.lob[order.price].append(order)
            else:
                self.lob[order.price] = [order]

        self.lob_depth = len(self.lob)


# Orderbook for a single instrument: list of bids and list of asks
class Orderbook:

    def __init__(self, symbol):
        bse_sys_min_price = 1  # minimum price in the system, in cents/pennies
        bse_sys_max_price = 1000  # maximum price in the system, in cents/pennies

        self.symbol = symbol
        self.bids = Orderbook_Half(Side.BID, bse_sys_min_price)
        self.asks = Orderbook_Half(Side.ASK, bse_sys_max_price)
        self.tape = []

    def get(self, id: int):
        bid = self.bids.get_order(id)
        ask = self.asks.get_order(id)

        if bid is not None:
            return bid
        elif ask is not None:
            return ask
        else:
            return None

    def add(self, order: Order):
        order.order_state = OrderState.Booked
        if order.side == Side.BID:
            self.bids.add_order(order)
        else:
            self.asks.add_order(order)

        trades = self.__match_trades()

        if order.order_type == OrderType.MARKET and order.is_active():
            order.OrderState = OrderState.Cancelled
            self.delete(order.id)

        return trades

    def __match_trades(self):
        trades = []
        timestamp = time.time()
        best_bid = self.bids.get_best_order()
        best_ask = self.asks.get_best_order()

        while best_bid is not None and best_ask is not None and best_bid.price >= best_ask.price:

            # use resting order
            if best_bid.timestamp < best_ask.timestamp:
                price = best_bid.price
            else:
                price = best_ask.price

            qty = min(best_bid.remaining, best_ask.remaining)

            trade = Trade(timestamp, best_bid, best_ask, price, qty)

            self.__fill(best_bid, qty)
            self.__fill(best_ask, qty)

            trade.bid_remaining = best_bid.remaining
            trade.ask_remaining = best_ask.remaining

            trades.append(trade)
            self.tape.append(trade)

            if best_bid.remaining == 0:
                self.delete(best_bid.id)
                best_bid = self.bids.get_best_order()

            if best_ask.remaining == 0:
                self.delete(best_ask.id)
                best_ask = self.asks.get_best_order()

        return trades

    def __fill(self, order: Order, qty: float):
        order.remaining = order.remaining - qty
        if order.remaining == 0:
            order.order_state = OrderState.Filled
        else:
            order.order_state = OrderState.PartialFill

    def delete(self, id: int):
        order = self.get(id)

        if order.side == Side.BID:
            removed = self.bids.delete_order(order)
        else:
            removed = self.asks.delete_order(order)

        if not removed:
            return "OrderNotFound"