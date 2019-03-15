from pkg.common.Trade import Trade
from .Order import *
from typing import List

# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_Half:

    def __init__(self, side: Side, worst_price):
        # booktype: bids or asks?
        # dictionary of orders received, indexed by Quote ID
        self.orders = {}
        # limit order book, dictionary indexed by price, with order info
        self.lob = {}

        # summary stats
        self.side = side
        self.__worst_price = worst_price
        self.lob_depth = 0  # how many different prices on lob?

    def get_order(self, exchange_id: int) -> Order:
        return self.orders.get(exchange_id)

    def get_orders(self) -> List[str]:
        orders = []
        for exchange_id in self.orders:
            orders.append(str(self.orders[exchange_id]))

        return orders

    def add_order(self, order: Order) -> bool:
        self.orders[order.exchange_id] = order
        self._build_lob()
        return True

    def delete_order(self, exchange_id: int) -> bool:
        if self.orders.get(exchange_id) is not None:
            del self.orders[exchange_id]
            self._build_lob()
            return True
        return False


    def get_best_price(self):
        if len(self.lob) > 0:
            prices = sorted(self.lob, reverse=True) if (self.side == Side.BID) else sorted(self.lob)
            return prices[0]
        else:
            return None

    def get_worst_price(self):
        if len(self.lob) > 0:
            prices = sorted(self.lob) if (self.side == Side.BID) else sorted(self.lob, reverse=True)
            return prices[0]
        else:
            return None

    def get_best_order(self) -> Order:
        if len(self.lob) > 0:
            return self.lob[self.get_best_price()][0]

    def get_order_n(self):
        return len(self.orders)

    def get_qty(self):
        qty = 0
        for qid in self.orders:
            order = self.orders.get(qid)
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
        for qid in self.orders:
            order = self.orders.get(qid)

            if order.price in self.lob:
                self.lob[order.price].append(order)
            else:
                self.lob[order.price] = [order]


# Orderbook for a single instrument: list of bids and list of asks
class Orderbook:

    def __init__(self, symbol):
        bse_sys_min_price = 1  # minimum price in the system, in cents/pennies
        bse_sys_max_price = 1000  # maximum price in the system, in cents/pennies

        self.symbol = symbol
        self.bids = Orderbook_Half(Side.BID, bse_sys_min_price)
        self.asks = Orderbook_Half(Side.ASK, bse_sys_max_price)
        self.tape = []
        self.exchange_id = 0  # unique ID code for each quote accepted onto the book
        self.trade_id = 0

    def get_next_exchange_id(self):
        id = self.exchange_id
        self.exchange_id = self.exchange_id + 1
        return id

    def get_next_trade_id(self):
        id = self.trade_id
        self.trade_id = self.trade_id + 1
        return id

    def get(self, exchange_id: int):
        bid = self.bids.get_order(exchange_id)
        ask = self.asks.get_order(exchange_id)

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
            self.delete(order.exchange_id)

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

            trade = Trade(timestamp, best_bid, best_ask, price, qty, self.get_next_trade_id())

            self.__fill(best_bid, qty)
            self.__fill(best_ask, qty)

            trades.append(trade)

            if best_bid.remaining == 0:
                self.delete(best_bid.exchange_id)
                best_bid = self.bids.get_best_order()

            if best_ask.remaining == 0:
                self.delete(best_ask.exchange_id)
                best_ask = self.asks.get_best_order()

        return trades

    def __fill(self, order: Order, qty: float):
        order.remaining = order.remaining - qty
        if order.remaining == 0:
            order.order_state = OrderState.Filled
        else:
            order.order_state = OrderState.PartialFill

    def delete(self, exchange_id: int):
        order = self.get(exchange_id)

        if order.side == Side.BID:
            removed = self.bids.delete_order(exchange_id)
        else:
            removed = self.asks.delete_order(exchange_id)

        if not removed:
            return "OrderNotFound"