import quickfix as fix


class FixApplication(fix.Application):
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
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, sessionID, message):
        return

    def fromAdmin(self, sessionID, message):
        return

    def toApp(self, sessionID, message):
        return

    def fromApp(self, message, sessionID):
        beginString = fix.BeginString()
        msgType = fix.MsgType()
        message.getHeader().getField(beginString)
        message.getHeader().getField(msgType)

        symbol = fix.Symbol()
        side = fix.Side()
        ordType = fix.OrdType()
        orderQty = fix.OrderQty()
        price = fix.Price()
        clOrdID = fix.ClOrdID()

        message.getField(ordType)
        print(ordType)
        if ordType.getValue() != fix.OrdType_LIMIT:
            raise fix.IncorrectTagValue(ordType.getField())

        message.getField(symbol)
        message.getField(side)
        message.getField(orderQty)
        message.getField(price)
        message.getField(clOrdID)

        executionReport = fix.Message()
        executionReport.getHeader().setField(beginString)
        executionReport.getHeader().setField(fix.MsgType(fix.MsgType_ExecutionReport))

        executionReport.setField(fix.OrderID(self.genOrderID()))
        executionReport.setField(fix.ExecID(self.genExecID()))
        executionReport.setField(fix.OrdStatus(fix.OrdStatus_FILLED))
        executionReport.setField(symbol)
        executionReport.setField(side)
        executionReport.setField(fix.CumQty(orderQty.getValue()))
        executionReport.setField(fix.AvgPx(price.getValue()))
        executionReport.setField(fix.LastShares(orderQty.getValue()))
        executionReport.setField(fix.LastPx(price.getValue()))
        executionReport.setField(clOrdID)
        executionReport.setField(orderQty)

        if beginString.getValue() >= fix.BeginString_FIX41:
            executionReport.setField(fix.ExecType(fix.ExecType_FILL))
            executionReport.setField(fix.LeavesQty(0))

        try:
            fix.Session.sendToTarget(executionReport, sessionID)
        except fix.SessionNotFound as e:
            return e
