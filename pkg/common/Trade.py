
class Trade:
    def __init__(self, timestamp, buyer, seller, price, qty, trade_id):
        self.timestamp = timestamp
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.qty = qty
        self.trade_id = trade_id

    def __str__(self):
        return 'TRADE (%5.2f): [Q=%s P=%.2f]' % \
               (self.timestamp, self.qty, self.price)
