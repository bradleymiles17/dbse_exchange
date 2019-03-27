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

    def get_order(self, id: int) -> Optional[SessionOrder]:
        for i, so in enumerate(self.orders):
            if so.order.id == id:
                return self.orders[i]

        return None

    def get_orders(self) -> List[str]:
        return list(map(str, self.orders))

    def add_order(self, so: SessionOrder):
        def compare(item1, item2):
            if item1.order.price < item2.order.price:
                return -1
            elif item1.order.price > item2.order.price:
                return 1
            else:
                return 0

        temp = self.orders
        temp.append(so)
        self.orders = sorted(temp, key=functools.cmp_to_key(compare), reverse=(self.side == Side.BID))
        self._build_lob()

    def delete_order(self, so: SessionOrder):
        i = self.orders.index(so)
        if i is not None:
            del self.orders[i]
            self._build_lob()
        return True

    def get_best_price(self):
        if len(self.orders) > 0:
            return self.orders[0].order.price
        else:
            return None

    def get_worst_price(self):
        if len(self.orders) > 0:
            return self.orders[-1].order.price
        else:
            return None

    def get_best_order(self) -> SessionOrder:
        if len(self.orders) > 0:
            return self.orders[0]

    def get_order_n(self) -> int:
        return len(self.orders)

    def get_qty(self) -> int:
        qty = 0
        for so in self.orders:
            qty += so.order.remaining
        return int(qty)

    def is_empty(self) -> bool:
        return len(self.orders) == 0

    # anonymize a lob, strip out order details, format as a sorted list
    # NB for asks, the sorting should be reversed
    def get_anonymize_lob(self) -> List:
        lob_anon = []
        for price in sorted(self.lob, reverse=(self.side == Side.BID)):

            qty = 0
            for order in self.lob[price]:
                qty += order.remaining

            lob_anon.append([price, int(qty)])

        return lob_anon

    # take a list of orders and build a limit-order-book (lob) from it
    # NB the exchange needs to know arrival times and trader-id associated with each order
    # returns lob as a dictionary (i.e., unsorted)
    # also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
    def _build_lob(self):
        self.lob = {}
        for so in self.orders:
            order = so.order

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

    def add(self, so: SessionOrder):
        so.order.order_state = OrderState.Booked
        ack_so = deepcopy(so)

        if so.order.side == Side.BID:
            self.bids.add_order(so)
        else:
            self.asks.add_order(so)

        trades = self.__match_trades()

        if so.order.order_type == OrderType.MARKET and so.order.is_active():
            so.order.OrderState = OrderState.Cancelled
            ack_so.order.OrderState = OrderState.Cancelled
            self.delete(so.order.id)

        return ack_so, trades

    def __match_trades(self):
        trades = []
        timestamp = time.time()
        best_bid = self.bids.get_best_order()
        best_ask = self.asks.get_best_order()

        while best_bid is not None and best_ask is not None and best_bid.order.price >= best_ask.order.price:

            # use resting order
            if best_bid.timestamp < best_ask.timestamp:
                price = best_bid.order.price
            else:
                price = best_ask.order.price

            qty = min(best_bid.order.remaining, best_ask.order.remaining)

            self.__fill(best_bid.order, qty)
            self.__fill(best_ask.order, qty)

            trade = Trade(timestamp, deepcopy(best_bid), deepcopy(best_ask), price, qty)

            trades.append(trade)
            self.tape.append(trade)

            if best_bid.order.remaining == 0:
                self.delete(best_bid.order.id)
                best_bid = self.bids.get_best_order()

            if best_ask.order.remaining == 0:
                self.delete(best_ask.order.id)
                best_ask = self.asks.get_best_order()

        return trades

    def __fill(self, order: Order, qty: float):
        order.remaining = order.remaining - qty
        if order.remaining == 0:
            order.order_state = OrderState.Filled
        else:
            order.order_state = OrderState.PartialFill

    def delete(self, id: int):
        so = self.get(id)

        if so.order.side == Side.BID:
            removed = self.bids.delete_order(so)
        else:
            removed = self.asks.delete_order(so)

        if not removed:
            return "OrderNotFound"
