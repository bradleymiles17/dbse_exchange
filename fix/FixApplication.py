import quickfix as fix
import datetime
from typing import List

from exchange.Exchange import Exchange
from pkg.common.Order import *
from pkg.common.Trade import Trade
from pkg.qf_map import *


class FixApplication(fix.Application):
    exchange = Exchange()

    def onCreate(self, sessionID):
        return

    def onLogon(self, sessionID):
        print("New session logon '%s'." % sessionID.toString())
        self.exchange.market_publisher.broadcast(self.exchange.lob.publish())
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

        client_id = fix.ClientID()
        message.getField(client_id)

        if ordType.getValue() == fix.OrdType_LIMIT:
            so = SessionOrder(
                session_id,
                LimitOrder(
                    self.exchange.gen_order_id(),
                    client_id.getValue(),
                    symbol.getValue(),
                    Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                    orderQty.getValue(),
                    price.getValue())
            )
        else:
            so = SessionOrder(
                session_id, MarketOrder(
                    self.exchange.gen_order_id(),
                    client_id.getValue(),
                    symbol.getValue(),
                    Side.BID if (side.getValue() == fix.Side_BUY) else Side.ASK,
                    orderQty.getValue()
                ))

        so.order.ClOrdID = int(clOrdID.getValue())

        ack_order, trades = self.exchange.create_order(so)

        # Execution Reports
        self.send_order_status(ack_order)

        if len(trades) > 0:
            self.send_trade_reports(trades)

    def on_order_cancel_request(self, message: fix.Message, session_id: fix.SessionID):

        clOrdID = fix.ClOrdID()
        message.getField(clOrdID)

        self.exchange.cancel_order(session_id.toString(), int(clOrdID.getValue()))


    def on_order_cancel_replace_request(self, message: fix.Message, session_id: fix.SessionID):
        return NotImplementedError

    # REPORTING ###############################t########################################################################
    execId = 0

    def gen_exec_id(self) -> str:
        self.execId = self.execId + 1
        return str(self.execId)

    def create_execution_report(self, so: SessionOrder, exec_type: fix.ExecType):
        report = fix.Message()
        report.getHeader().setField(fix.MsgType(fix.MsgType_ExecutionReport))

        report.setField(fix.OrderID(str(so.order.id)))
        report.setField(fix.ClOrdID(str(so.order.ClOrdID)))
        report.setField(fix.ClientID(so.order.client_id))
        report.setField(fix.ExecID(self.gen_exec_id()))
        report.setField(fix.ExecType(exec_type))
        report.setField(fix.OrdStatus(order_status_to_fix(so.order.order_state)))

        report.setField(fix.LeavesQty(so.order.remaining))
        report.setField(fix.CumQty(so.order.qty - so.order.remaining))
        report.setField(fix.AvgPx(0))

        report.setField(fix.Symbol(so.order.symbol))
        report.setField(fix.Side(side_to_fix(so.order.side)))
        report.setField(fix.OrderQty(so.order.qty))
        report.setField(fix.Price(so.order.price))
        return report

    def send_trade_reports(self, trades: List[Trade]):
        def send_trade_report(so: SessionOrder, price, qty):
            report = self.create_execution_report(so, fix.ExecType_FILL)
            report.setField(fix.LastPx(price))
            report.setField(fix.LastQty(qty))

            fix.Session.sendToTarget(report, so.session_id)

        for t in trades:
            print(t)
            send_trade_report(t.buyer, t.price, t.qty)
            send_trade_report(t.seller, t.price, t.qty)

    def send_order_status(self, so: SessionOrder):
        report = self.create_execution_report(so, fix.ExecType_ORDER_STATUS)

        fix.Session.sendToTarget(report, so.session_id)
