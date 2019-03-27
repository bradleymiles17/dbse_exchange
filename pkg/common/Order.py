import time
from copy import deepcopy


class Side:
    BID = "BID"
    ASK = "ASK"


class OrderType:
    MARKET = "market"
    LIMIT = "limit"


class OrderState:
    New = "new"
    Booked = "booked"
    PartialFill = "partial"
    Filled = "filled"
    Cancelled = "cancelled"
    Rejected = "rejected"


class Order:
    ClOrdID: int = None
    price: float = None
    order_type: OrderType = None

    def __init__(self, id: int, client_id: str, symbol: str, side: Side, qty: float):
        self.id = id
        self.client_id = client_id
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.remaining = qty
        self.order_state = OrderState.New

    def __str__(self):
        return '[%d %s %s %s %s P=%.2f Q=%s R=%s]' % \
               (self.id, self.client_id, self.order_type, self.symbol, self.side, self.price, self.qty, self.remaining)

    def is_active(self) -> bool:
        return self.order_state != OrderState.Filled and self.order_state != OrderState.Cancelled and self.order_state != OrderState.Rejected


class MarketOrder(Order):

    def __init__(self, id: int, client_id: str, symbol: str, side: Side, qty: float):
        super().__init__(id, client_id, symbol, side, qty)
        self.price = 0
        self.order_type = OrderType.MARKET


class LimitOrder(Order):

    def __init__(self, id: int, client_id: str, symbol: str, side: Side, qty: float, price: float):
        super().__init__(id, client_id, symbol, side, qty)
        self.price = price
        self.order_type = OrderType.LIMIT


class SessionOrder:

    def __init__(self, session_id, order: Order):
        self.session_id = session_id
        self.timestamp = time.time()
        self.order = order

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        ret_val = cls.__new__(cls)

        ret_val.session_id = self.session_id
        ret_val.timestamp = self.timestamp
        ret_val.order = deepcopy(self.order)

        return ret_val
