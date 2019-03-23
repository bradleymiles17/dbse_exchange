from typing import List

from pkg.common import Order


class OrderBookResponse:
    timestamp = None


class Filled(OrderBookResponse):
    def __init__(self, timestamp, price, qty, exchange_ids: List[int]):
        self.timestamp = timestamp
        self.price = price
        self.qty = qty
        self.exchange_ids = exchange_ids

    def __str__(self):
        return 'FILLED (%5.2f): [P=%.2f Q=%s]' % \
               (self.timestamp, self.price, self.qty)


class Acknowledged(OrderBookResponse):
    def __init__(self, timestamp, order: Order):
        self.timestamp = timestamp
        self.order = order

    def __str__(self):
        return 'ACKNOWLEDGED (T=%5.2f): [%s %s %s]' % \
               (self.timestamp, self.order.id, self.order.ClOrdID, self.order)


class Rejected(OrderBookResponse):
    def __init__(self, timestamp, error, exchange_id: int):
        self.timestamp = timestamp
        self.error = error
        self.exchange_id = exchange_id

    def __str__(self):
        return 'REJECTED (T=%5.2f) %s: [%s]' % \
               (self.timestamp, self.error, self.exchange_id)


class Canceled(OrderBookResponse):
    def __init__(self, timestamp, reason, exchange_id: int):
        self.timestamp = timestamp
        self.reason = reason
        self.exchange_id = exchange_id

    def __str__(self):
        return 'CANCELED (T=%5.2f) %s: [%s]' % \
               (self.timestamp, self.reason, self.exchange_id)

