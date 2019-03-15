import quickfix as fix

from exchange.Exchange import Exchange
from pkg.common.Order import Side, LimitOrder, MarketOrder


class FixApplication(fix.Application):

    exchange = Exchange(True)

    orderID = 0
    execID = 0

    def genOrderID(self) -> str:
        self.orderID = self.orderID + 1
        return str(self.orderID)

    def genExecID(self) -> str:
        self.execID = self.execID + 1
        return str(self.execID)

    def onCreate(self, sessionID):
        return

    def onLogon(self, sessionID):
        print("New session logon '%s'." % sessionID.toString())
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, sessionID, message):
        return

    def fromAdmin(self, sessionID, message):
        return

    def toApp(self, sessionID, message):
        return

    def fromApp(self, message: fix.Message, sessionID):
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        type = msgType.getValue()

        if type == fix.MsgType_NewOrderSingle:
            self.on_new_order_single(message, sessionID)
        elif type == fix.MsgType_OrderCancelRequest:
            self.on_order_cancel_request(message, sessionID)
        elif type == fix.MsgType_OrderCancelReplaceRequest:
            self.on_order_cancel_replace_request(message, sessionID)
        else:
            return fix.UnsupportedMessageType

    def on_new_order_single(self, message: fix.Message, session_id: fix.SessionID):
        ordType = fix.OrdType()
        message.getField(ordType)

        if ordType.getValue() != fix.OrdType_LIMIT:
            raise fix.IncorrectTagValue(ordType.getField())

        symbol = fix.Symbol()
        message.getField(symbol)

        side = fix.Side()
        message.getField(side)

        orderQty = fix.OrderQty()
        message.getField(orderQty)

        price = fix.Price()
        message.getField(price)

        clOrdID = fix.ClOrdID()
        message.getField(clOrdID)

        if ordType.getValue() == fix.OrdType_LIMIT:
            order = LimitOrder(
                clOrdID.getValue(),
                symbol.getValue(),
                Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                price.getValue(),
                orderQty.getValue()
            )
        else:
            order = MarketOrder(
                clOrdID.getValue(),
                symbol.getValue(),
                Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                orderQty.getValue()
            )

        self.exchange.CreateOrder(order)
        return 1


    def on_order_cancel_request(self, message: fix.Message, session_id: fix.SessionID):
        return 1

    def on_order_cancel_replace_request(self, message: fix.Message, session_id: fix.SessionID):
        return 1


