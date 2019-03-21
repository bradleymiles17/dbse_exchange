from pkg.common.Order import SessionOrder

id = 0


def gen_trade_id():
    global id
    id = id + 1
    return id


class Trade:
    def __init__(self, timestamp, buyer: SessionOrder, seller: SessionOrder, price, qty):
        self.id = gen_trade_id()
        self.timestamp = timestamp
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.qty = qty

    def __str__(self):
        return 'TRADE (%5.2f): [Q=%s P=%.2f]' % \
               (self.timestamp, self.qty, self.price)
