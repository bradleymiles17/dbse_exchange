import quickfix as fix
from pkg.common.Order import OrderState, Side


def order_status_to_fix(order_state: OrderState) -> fix.OrdStatus:
    map = {
        OrderState.New: fix.OrdStatus_NEW,
        OrderState.Booked: fix.OrdStatus_ACCEPTED_FOR_BIDDING,
        OrderState.PartialFill: fix.OrdStatus_PARTIALLY_FILLED,
        OrderState.Filled: fix.OrdStatus_FILLED,
        OrderState.Cancelled: fix.OrdStatus_CANCELED,
        OrderState.Rejected: fix.OrdStatus_REJECTED
    }
    return map[order_state]


def fix_to_order_status(order_state: fix.OrdStatus) -> OrderState:
    map = {
        fix.OrdStatus_NEW: OrderState.New,
        fix.OrdStatus_ACCEPTED_FOR_BIDDING: OrderState.Booked,
        fix.OrdStatus_PARTIALLY_FILLED: OrderState.PartialFill,
        fix.OrdStatus_FILLED: OrderState.Filled,
        fix.OrdStatus_CANCELED: OrderState.Cancelled,
        fix.OrdStatus_REJECTED: OrderState.Rejected
    }
    return map[order_state]


def side_to_fix(order_side: Side) -> fix.Side:
    map = {
        Side.BID: fix.Side_BUY,
        Side.ASK: fix.Side_SELL
    }
    return map[order_side]


def fix_to_side(order_side: fix.Side) -> Side:
    map = {
        fix.Side_BUY: Side.BID,
        fix.Side_SELL: Side.ASK
    }
    return map[order_side]
