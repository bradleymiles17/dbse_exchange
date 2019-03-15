import time

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
    exchange_id: int = None
    price: float = None
    order_type: OrderType = None
    timestamp = time.time()

    def __init__(self, ClOrdID: str, symbol: str, side: Side, qty: float):
        self.ClOrdID = ClOrdID
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.remaining = qty
        self.order_state = OrderState.New

    def is_active(self) -> bool:
        return self.order_state != OrderState.Filled and self.order_state != OrderState.Cancelled and self.order_state != OrderState.Rejected


class MarketOrder(Order):

    def __init__(self, ClOrdID: str, symbol: str, side: Side, qty: float):
        super().__init__(ClOrdID, symbol, side, qty)
        self.price = 0
        self.order_type = OrderType.MARKET


class LimitOrder(Order):

    def __init__(self, ClOrdID: str, symbol: str, side: Side, price: float, qty: float):
        super().__init__(ClOrdID, symbol, side, qty)
        self.price = price
        self.order_type = OrderType.LIMIT




