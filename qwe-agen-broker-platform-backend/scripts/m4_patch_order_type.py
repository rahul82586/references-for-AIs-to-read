import io

# --- 1. the request schema validates the enum, not a free string -------------
p = "api/schemas/trade.py"
s = io.open(p, encoding="utf-8").read()

old = '''from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    """Client request schema to place a new order."""
    symbol: str = Field(..., min_length=1, max_length=32)
    order_type: str = Field(..., description="BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP")'''
assert old in s
new = '''from pydantic import BaseModel, Field

from core.domains.oms.enums import OrderType


class OrderRequest(BaseModel):
    """Client request schema to place a new order."""
    symbol: str = Field(..., min_length=1, max_length=32)
    #: OrderType, not str. The client trade router passed this straight into
    #: CreateOrderCommand, so the Order entity carried the STRING "BUY". `is_market()`
    #: compares against OrderType members and returned False, the order was treated as a
    #: pending one with no price, and the matching engine rejected it with "cannot price
    #: order type BUY". Typing it here also means an unknown side is a 422 at the edge
    #: instead of an error somewhere in the execution path.
    order_type: OrderType = Field(..., description="BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP")'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("schema: OrderType")

# --- 2. the command coerces too, so no caller can repeat the mistake ---------
p = "application/commands/create_order.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


old = N('''    comment: str = ""
    reason: OrderReason = OrderReason.CLIENT
''')
assert old in s
new = N('''    comment: str = ""
    reason: OrderReason = OrderReason.CLIENT

    def __post_init__(self) -> None:
        """Coerce the enums a caller may have passed as strings.

        The HTTP boundary handed `order_type` through as the raw request string, and an
        Order built with `order_type="BUY"` fails every enum comparison silently:
        `is_market()` said False, so a market order was priced as a pending one and the
        matching engine could not price it at all. Coercing here means a string is a
        convenience rather than a way to build an order that cannot execute.
        """
        if not isinstance(self.order_type, OrderType):
            self.order_type = OrderType(str(self.order_type).upper())
        if not isinstance(self.reason, OrderReason):
            self.reason = OrderReason(str(self.reason).upper())
''')
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("command: enum coercion")
