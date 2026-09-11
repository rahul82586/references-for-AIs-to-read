"""Order entity - Client intent (IMTOrder)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from core.domains.common.value_objects import Price, Volume
from core.domains.oms.enums import (
    OrderType, OrderState, OrderReason, TimeInForce,
    ActivationMode, OrderFlags
)


@dataclass
class Order:
    """
    Order Entity - Client Intent (IMTOrder).
    
    An Order represents a REQUEST to trade. It is MUTABLE and has a state machine.
    It may result in zero, one, or multiple Deals (for partial fills).
    
    MT5 Order Types:
    - Market: BUY, SELL
    - Pending: BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP,
               BUY_STOP_LIMIT, SELL_STOP_LIMIT
    """
    # Identity
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None  # Exchange/ECN order ID
    gateway_id: Optional[str] = None   # Gateway execution order ID
    
    # Account & Symbol
    account_login: int = 0
    dealer_login: Optional[int] = None  # Dealer who processed (0 = auto)
    symbol: str = ""
    
    # Order details
    order_type: OrderType = OrderType.BUY
    reason: OrderReason = OrderReason.CLIENT
    #: Margin held against the account's free margin while this order is in
    #: flight (M6). Set at approval by PreTradeRiskService, zeroed by the fill
    #: (RecordDealHandler) or the rejection (ExecutionOrchestrator).
    reserved_margin: Decimal = Decimal('0')
    state: OrderState = OrderState.STARTED
    
    # Volume
    volume_initial: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    volume_current: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    
    # Pricing
    #: Limit/Stop price; None means "not yet priced" (a market order before the
    #: fill, or the fill price after). The old default_factory built
    #: Price(Decimal('0')), which Price's own positivity guard rejects - so ANY
    #: Order(...) constructed without an explicit price_order raised ValueError
    #: (M10). Callers already treat None as "no price".
    price_order: Optional[Price] = None
    price_sl: Optional[Price] = None  # Stop loss
    price_tp: Optional[Price] = None  # Take profit
    price_trigger: Optional[Price] = None  # For STOP_LIMIT orders
    
    # Time
    time_setup: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_setup_msc: int = 0  # Milliseconds since epoch
    time_expiration: Optional[datetime] = None
    time_done: Optional[datetime] = None
    
    # Time in force
    time_in_force: TimeInForce = TimeInForce.GTC
    
    # ATM Activation (time/price triggered orders)
    activation_mode: ActivationMode = ActivationMode.NONE
    activation_time: Optional[datetime] = None
    activation_price: Optional[Price] = None
    activation_flags: OrderFlags = OrderFlags.NONE
    
    # Symbol metadata (snapshot at order time)
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Expert/Plugin info
    expert_id: str = ""  # Filled by EA
    expert_name: str = ""
    comment: str = ""
    
    # Matching
    order_matching: Optional[str] = None  # Opposite order ticket (for ECN)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def volume(self) -> Volume:
        """The volume this order still has to fill - MT5's VolumeCurrent.

        Nine call sites read `order.volume`: the pre-trade volume filter, the margin
        calculation, the NOP exposure ratio, the routing rule min/max filters, the dealer
        queue event and the trade API response. Order declares `volume_initial` and
        `volume_current` (MT5's own two fields) and no `volume`, so every one of them
        raised AttributeError - including `_check_volume_limits` and `basic_margin`,
        which is to say no order could be risk-checked at all.

        Reading VolumeCurrent is the correct semantic, not just the convenient one: MT5
        margins and routes the REMAINING volume, and after a partial fill that is not
        what the client originally asked for.
        """
        return self.volume_current

    @property
    def is_fully_filled(self) -> bool:
        return self.volume_current.value == Decimal("0") and self.volume_initial.value > Decimal("0")

    def __post_init__(self):
        """For a NEW order, volume_current defaults to volume_initial.

        Past entry into execution, zero is a REAL value, not a missing one: a
        fully filled order carries volume_current == 0. This default used to run
        on EVERY construction - including db_to_order(), which rebuilds the
        entity on every SQL read - so every read of a filled order resurrected
        the initial volume: the HTTP layer reported filled_volume 0 for genuinely
        filled orders and re-reads saw phantom remaining volume (caught by the
        M10 cloud gate; the in-memory harness never reconstructs entities, which
        is why the unit suite could not see it). Only STARTED orders - which have
        not been priced, approved or filled - get the default.
        """
        if (
            self.state is OrderState.STARTED
            and self.volume_current.value == Decimal('0')
            and self.volume_initial.value > 0
        ):
            self.volume_current = Volume(self.volume_initial.value)
    
    # =========================================================================
    # STATE MACHINE
    # =========================================================================
    
    _VALID_TRANSITIONS = {
        OrderState.STARTED: [OrderState.PLACED, OrderState.REJECTED, OrderState.CANCELLED],
        OrderState.PLACED: [
            OrderState.PARTIALLY_FILLED, OrderState.FILLED,
            OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED
        ],
        OrderState.PARTIALLY_FILLED: [
            OrderState.PARTIALLY_FILLED, OrderState.FILLED,
            OrderState.CANCELLED, OrderState.EXPIRED
        ],
        # Terminal states - no transitions allowed
        OrderState.FILLED: [],
        OrderState.CANCELLED: [],
        OrderState.REJECTED: [],
        OrderState.EXPIRED: [],
    }
    
    def transition_to(self, new_state: OrderState) -> None:
        """
        Transition order to a new state.
        
        Raises ValueError if transition is invalid.
        """
        if new_state not in self._VALID_TRANSITIONS.get(self.state, []):
            raise ValueError(
                f"Invalid state transition: {self.state.value} -> {new_state.value} "
                f"for order {self.ticket_id}"
            )
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)
        
        # If terminal state, mark as done
        if new_state in [OrderState.FILLED, OrderState.CANCELLED,
                         OrderState.REJECTED, OrderState.EXPIRED]:
            self.time_done = datetime.now(timezone.utc)
    
    def is_pending(self) -> bool:
        """Check if order is a pending order (not market)."""
        return self.order_type in [
            OrderType.BUY_LIMIT, OrderType.SELL_LIMIT,
            OrderType.BUY_STOP, OrderType.SELL_STOP,
            OrderType.BUY_STOP_LIMIT, OrderType.SELL_STOP_LIMIT,
        ]
    
    def is_market(self) -> bool:
        """Check if order is a market order."""
        return self.order_type in [OrderType.BUY, OrderType.SELL]
    
    def is_buy(self) -> bool:
        """Check if order is a buy-side order."""
        return self.order_type.value.startswith("BUY")
    
    def is_sell(self) -> bool:
        """Check if order is a sell-side order."""
        return self.order_type.value.startswith("SELL")
    
    def is_terminal(self) -> bool:
        """Check if order is in a terminal state."""
        return self.state in [
            OrderState.FILLED, OrderState.CANCELLED,
            OrderState.REJECTED, OrderState.EXPIRED
        ]
    
    # =========================================================================
    # FILL LOGIC
    # =========================================================================
    
    def apply_fill(self, fill_volume: Volume, fill_price: Price) -> None:
        """
        Apply a partial fill to the order.
        
        Reduces volume_current and transitions state appropriately.
        """
        if fill_volume.value <= 0:
            raise ValueError("Fill volume must be positive")
        
        if fill_volume.value > self.volume_current.value:
            raise ValueError(
                f"Fill volume {fill_volume.value} exceeds remaining "
                f"{self.volume_current.value}"
            )
        
        self.volume_current = Volume(self.volume_current.value - fill_volume.value)
        self.updated_at = datetime.now(timezone.utc)

        # M7: a MARKET order's price IS its execution price - the client asked
        # for "the market", and since client pricing the fill can differ from
        # the raw tick the request was risk-checked against (group spread
        # transforms). Stamp it, or the API response and the deal disagree.
        # A PENDING order keeps its instruction price (MT5 semantics: the deal
        # carries the execution price, the order carries what was requested).
        if self.is_market():
            self.price_order = fill_price
        
        # Transition state
        if self.volume_current.value == 0:
            self.transition_to(OrderState.FILLED)
        else:
            if self.state == OrderState.PLACED:
                self.transition_to(OrderState.PARTIALLY_FILLED)
    
    def cancel(self, reason: str = "") -> None:
        """Cancel the order."""
        if self.is_terminal():
            raise ValueError(f"Cannot cancel order in state {self.state.value}")
        self.transition_to(OrderState.CANCELLED)
        if reason:
            self.comment = f"{self.comment} [CANCELLED: {reason}]".strip()
    
    def reject(self, reason: str) -> None:
        """Reject the order."""
        if self.is_terminal():
            raise ValueError(f"Cannot reject order in state {self.state.value}")
        self.transition_to(OrderState.REJECTED)
        self.comment = f"{self.comment} [REJECTED: {reason}]".strip()
    
    def expire(self) -> None:
        """Expire the order (time-in-force expired)."""
        if self.is_terminal():
            raise ValueError(f"Cannot expire order in state {self.state.value}")
        self.transition_to(OrderState.EXPIRED)
    
    # =========================================================================
    # ATM / ACTIVATION LOGIC
    # =========================================================================
    
    def is_activated(self, current_time: datetime, current_price: Price) -> bool:
        """
        Check if an ATM order should be activated.
        
        ATM orders are triggered by time, price, or both.
        """
        if self.activation_mode == ActivationMode.NONE:
            return True  # Not an ATM order, always active
        
        time_triggered = False
        price_triggered = False
        
        if self.activation_mode in [ActivationMode.TIME, ActivationMode.TIME_PRICE]:
            if self.activation_time and current_time >= self.activation_time:
                time_triggered = True
        
        if self.activation_mode in [ActivationMode.PRICE, ActivationMode.TIME_PRICE]:
            if self.activation_price:
                # Price trigger depends on order type
                if self.is_buy():
                    price_triggered = current_price.value >= self.activation_price.value
                else:
                    price_triggered = current_price.value <= self.activation_price.value
        
        if self.activation_mode == ActivationMode.TIME:
            return time_triggered
        elif self.activation_mode == ActivationMode.PRICE:
            return price_triggered
        elif self.activation_mode == ActivationMode.TIME_PRICE:
            return time_triggered and price_triggered
        
        return True
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "external_id": self.external_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "order_type": self.order_type.value,
            "reason": self.reason.value,
            "state": self.state.value,
            "volume_initial": str(self.volume_initial.value),
            "volume_current": str(self.volume_current.value),
            "price_order": str(self.price_order.value),
            "price_sl": str(self.price_sl.value) if self.price_sl else None,
            "price_tp": str(self.price_tp.value) if self.price_tp else None,
            "time_in_force": self.time_in_force.value,
            "activation_mode": self.activation_mode.value,
            "time_setup": self.time_setup.isoformat(),
            "time_expiration": self.time_expiration.isoformat() if self.time_expiration else None,
            "time_done": self.time_done.isoformat() if self.time_done else None,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }