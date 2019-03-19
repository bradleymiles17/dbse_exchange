import time

orderID = 0


def gen_order_id() -> int:
    global orderID
    orderID = orderID + 1
    return orderID


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
    id: int = None
    ClOrdID: str = None
    timestamp = None
    price: float = None
    order_type: OrderType = None

    def __init__(self, symbol: str, side: Side, qty: float):
        self.id = gen_order_id()
        self.timestamp = time.time()
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.remaining = qty
        self.order_state = OrderState.New

    def __str__(self):
        return '%s (%5.2f): [%s %s P=%.2f Q=%s]' % \
               (self.order_type, self.timestamp, self.symbol, self.side, self.price, self.qty)

    def is_active(self) -> bool:
        return self.order_state != OrderState.Filled and self.order_state != OrderState.Cancelled and self.order_state != OrderState.Rejected


class MarketOrder(Order):

    def __init__(self, symbol: str, side: Side, qty: float):
        super().__init__(symbol, side, qty)
        self.price = 0
        self.order_type = OrderType.MARKET


class LimitOrder(Order):

    def __init__(self, symbol: str, side: Side, qty: float, price: float):
        super().__init__(symbol, side, qty)
        self.price = price
        self.order_type = OrderType.LIMIT


class SessionOrder:

    def __init__(self, session_id, order: Order):
        self.session_id = session_id
        self.order = order
