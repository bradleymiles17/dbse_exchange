from pkg.common.Order import Order, SessionOrder

id = 0


def gen_trade_id():
    global id
    id = id + 1
    return id


class Trade:
    def __init__(self, timestamp, buyer: Order, seller: Order, price, qty):
        self.id = gen_trade_id()
        self.timestamp = timestamp
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.qty = qty

        self.bid_remaining = 0
        self.ask_remaining = 0

    def __str__(self):
        return 'TRADE (%5.2f): [Q=%s P=%.2f]' % \
               (self.timestamp, self.qty, self.price)
