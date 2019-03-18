import quickfix as fix
from typing import List

from exchange.Exchange import Exchange
from pkg.common.Order import *
from pkg.common.Trade import Trade
from pkg.qf_map import *


class FixApplication(fix.Application):

    exchange = Exchange(True)

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

    def toApp(self, message, sessionID):
        print("Sending [%s]: %s" % (sessionID, message.toString()))
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
            so = SessionOrder(session_id, LimitOrder(
                clOrdID.getValue(),
                symbol.getValue(),
                Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                price.getValue(),
                orderQty.getValue()
            ))
        else:
            so = SessionOrder(session_id, MarketOrder(
                clOrdID.getValue(),
                symbol.getValue(),
                Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                orderQty.getValue()
            ))

        trades, lob = self.exchange.create_order(so.order)

        # Execution Reports
        if len(trades) > 0:
            self.send_trade_reports(session_id, trades)
        elif len(trades) == 0 or so.order.order_state == OrderState.Cancelled:
            self.send_execution_report(so)

    def on_order_cancel_request(self, message: fix.Message, session_id: fix.SessionID):
        return 1

    def on_order_cancel_replace_request(self, message: fix.Message, session_id: fix.SessionID):
        return 1

    # REPORTING ###############################t#########################################################################
    def send_trade_reports(self, session_id: fix.SessionID, trades: List[Trade]):
        for t in trades:
            print(t)
            # self.send_trade_execution_report(t.buyer, t.price, t.qty, t.bid_remaining)
            # self.send_trade_execution_report(t.seller, t.price, t.qty, t.ask_remaining)

    # report on trade execution
    def send_trade_execution_report(self, so: SessionOrder, price, qty, remaining):
        self.send_execution_report(so)

    # report on order execution
    def send_execution_report(self, so: SessionOrder):
        report = fix.Message()
        report.getHeader().setField(fix.MsgType(fix.MsgType_ExecutionReport))

        report.setField(fix.OrderID(str(so.order.id)))
        report.setField(fix.ExecID(str(so.order.id)))
        report.setField(fix.ExecType(fix.ExecType_ORDER_STATUS))
        report.setField(fix.OrdStatus(order_status_to_fix(so.order.order_state)))

        report.setField(fix.Symbol(so.order.symbol))
        report.setField(fix.Side(side_to_fix(so.order.side)))
        report.setField(fix.OrderQty(so.order.qty))
        report.setField(fix.LeavesQty(so.order.remaining))
        report.setField(fix.CumQty(so.order.qty - so.order.remaining))
        report.setField(fix.AvgPx(0))

        report.setField(fix.ClOrdID(so.order.ClOrdID))
        report.setField(fix.Price(so.order.price))

        fix.Session.sendToTarget(report, so.session_id)

