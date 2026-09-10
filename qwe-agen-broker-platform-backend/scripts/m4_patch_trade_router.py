import io

p = "api/routers/trade.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


old = N('''        order = await handler.handle(command)
        ticket_id = getattr(order, 'ticket_id', getattr(order, 'id', ''))
        symbol = getattr(order, 'symbol', '')
        order_type_str = order.order_type.value if hasattr(order.order_type, 'value') else str(order.order_type)
        vol_val = order.volume.value if hasattr(order.volume, 'value') else Decimal(str(order.volume))
        filled_vol = order.filled_volume.value if hasattr(order, 'filled_volume') and hasattr(order.filled_volume, 'value') else Decimal('0')
        price_val = order.price.value if getattr(order, 'price', None) and hasattr(order.price, 'value') else None
        state_str = order.state.value if hasattr(order.state, 'value') else str(order.state)
        created_at = getattr(order, 'created_at', datetime.now(timezone.utc))
''')
assert old in s, "response mapping block not found"

new = N('''        order = await handler.handle(command)
        ticket_id = getattr(order, 'ticket_id', getattr(order, 'id', ''))
        symbol = getattr(order, 'symbol', '')
        order_type_str = order.order_type.value if hasattr(order.order_type, 'value') else str(order.order_type)
        vol_val = order.volume_initial.value if hasattr(order.volume_initial, 'value') else Decimal(str(order.volume_initial))
        state_str = order.state.value if hasattr(order.state, 'value') else str(order.state)
        created_at = getattr(order, 'created_at', datetime.now(timezone.utc))

        # Order carries volume_initial / volume_current and price_order - MT5's own field
        # names. This response read `order.filled_volume` and `order.price`, neither of
        # which exists, so the two guard expressions quietly took their else branch and
        # EVERY response reported filled_volume 0 and price null, including for orders
        # that had genuinely filled. A client reading this endpoint could not tell what
        # it had been filled at, or whether it had been filled at all.
        remaining = order.volume_current.value if hasattr(order.volume_current, 'value') else Decimal('0')
        filled_vol = vol_val - remaining

        # For a market order price_order is the execution price: CreateOrderHandler sets
        # it from the live quote (ask for a buy, bid for a sell) before the fill, and the
        # matching engine fills at that same price. For a resting pending order it is the
        # requested limit/stop, which is the only price there is so far.
        price_val = order.price_order.value if getattr(order, 'price_order', None) else None
''')
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("trade router: response mapping; crlf =", crlf)
