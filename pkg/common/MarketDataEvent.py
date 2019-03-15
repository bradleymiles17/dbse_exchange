from typing import Optional


class MarketDataEvent:
    timestamp = None


class LastSalePrice(MarketDataEvent):

    def __init__(self, timestamp, symbol: str, price: float, qty: int, volume: int):
        self.timestamp = timestamp
        self.symbol = symbol
        self.price = price
        self.qty = qty
        self.volume = volume

    def __str__(self):
        return 'LastSalePrice (T=%5.2f): [%s P=%.2f Q=%s V=%s]' % \
               (self.timestamp, self.symbol, self.price, self.qty, self.volume)


class BBOChange(MarketDataEvent):

    def __init__(self, timestamp, symbol: str, bid_price: Optional[float], bid_qty: Optional[int], offer_price: Optional[float], offer_qty: Optional[int]):
        self.timestamp = timestamp
        self.symbol = symbol
        self.bid_price = bid_price
        self.bid_qty = bid_qty
        self.offer_price = offer_price
        self.offer_qty = offer_qty

    def __str__(self):
        return 'BBOChange (T=%5.2f): [%s BP=%.2f BQ=%s OP=%.2f OQ=%s]' % \
               (self.timestamp, self.symbol, self.bid_price, self.bid_qty, self.offer_price, self.offer_qty)
