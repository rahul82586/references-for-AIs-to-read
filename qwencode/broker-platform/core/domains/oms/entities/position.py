"""Position entity - Aggregate open state (IMTPosition)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import uuid

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.enums import (
    OrderType, DealType, DealEntry, PositionAction, PositionReason
)


@dataclass
class Position:
    """
    Position Entity - Aggregate Open State (IMTPosition).
    
    A Position represents the trader's current exposure to a symbol.
    
    MT5 Position Modes:
    - HEDGING: Every deal creates a new position (retail default)
    - NETTING: All deals for a symbol aggregate into one position (institutional)
    
    MT5 Position Actions:
    - BUY: Long position
    - SELL: Short position
    """
    # Identity
    position_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None  # Exchange/ECN position ID
    identifier: Optional[str] = None   # For netting: groups positions by identifier
    
    # Account
    account_login: int = 0
    
    # Symbol & side
    symbol: str = ""
    action: PositionAction = PositionAction.BUY
    reason: PositionReason = PositionReason.CLIENT
    
    # Volume
    volume: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    
    # Pricing
    price_open: Price = field(default_factory=lambda: Price(Decimal('0')))
    price_current: Price = field(default_factory=lambda: Price(Decimal('0')))
    price_sl: Optional[Price] = None
    price_tp: Optional[Price] = None
    
    # Financial
    profit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))  # Unrealized PnL
    swap: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    commission: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    
    # Symbol metadata
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Links
    deal_open: Optional[str] = None  # Opening deal ID
    deal_close: Optional[str] = None  # Closing deal ID (if closed)
    position_by_id: Optional[str] = None  # For close-by operations
    
    # Timestamps
    time_create: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_done: Optional[datetime] = None  # When position was closed
    
    # Metadata
    comment: str = ""
    magic_number: int = 0  # EA magic number
    
    # =========================================================================
    # APPLY DEAL (Core Logic)
    # =========================================================================
    
    def apply_deal(
        self,
        deal: "Deal",
        position_mode: str = "HEDGING",
    ) -> Optional["Position"]:
        """
        Apply a deal to this position.
        
        Returns:
            - In HEDGING mode with opposite side: Returns NEW position (reversal)
            - In NETTING mode: Updates self, returns None
            - If closed fully: Sets volume to 0, caller should archive
        """
        from core.domains.oms.entities.deal import Deal
        
        if deal.deal_type not in [DealType.BUY, DealType.SELL]:
            return None  # Ignore non-trading deals
        
        deal_side = PositionAction.BUY if deal.deal_type == DealType.BUY else PositionAction.SELL
        
        # HEDGING MODE: Every deal creates a new position or adds to same-direction only
        if position_mode == "HEDGING":
            if deal_side != self.action:
                # Opposite direction in Hedging = Create NEW position (reversal)
                return self._create_opposite_position(deal)
            else:
                # Same direction = Add to existing position
                self._add_to_position(deal)
                return None
        # NETTING MODE: Aggregate all deals
        else:
            if deal_side == self.action:
                # Adding to position
                self._add_to_position(deal)
                return None
            else:
                # Closing or Reversing
                return self._close_or_reverse(deal)
    
    def _add_to_position(self, deal: "Deal") -> None:
        """Add a same-direction deal to the position (averaging price)."""
        old_notional = self.volume.value * self.price_open.value
        new_notional = deal.volume.value * deal.price.value
        
        new_volume = self.volume.value + deal.volume.value
        if new_volume > 0:
            new_price = (old_notional + new_notional) / new_volume
            self.price_open = Price(new_price)
        
        self.volume = Volume(new_volume)
        self.swap = Money(self.swap.amount + deal.swap.amount, self.swap.currency)
        self.commission = Money(
            self.commission.amount + deal.commission.amount,
            self.commission.currency
        )
        self.time_update = datetime.now(timezone.utc)
    
    def _close_or_reverse(self, deal: "Deal") -> Optional["Position"]:
        """Close or reverse a position (netting mode)."""
        if deal.volume.value >= self.volume.value:
            # Full close or reversal
            close_volume = self.volume.value
            remaining_volume = deal.volume.value - close_volume
            
            # Mark as closed
            self.volume = Volume(Decimal('0'))
            self.deal_close = deal.deal_id
            self.time_done = datetime.now(timezone.utc)
            self.time_update = datetime.now(timezone.utc)
            
            # If there's remaining volume, create new position in opposite direction
            if remaining_volume > 0:
                return self._create_opposite_position_with_remaining(deal, remaining_volume)
            return None
        else:
            # Partial close
            self.volume = Volume(self.volume.value - deal.volume.value)
            self.time_update = datetime.now(timezone.utc)
            return None
    
    def _create_opposite_position(self, deal: "Deal") -> "Position":
        """Create a new position in the opposite direction (hedging reversal)."""
        new_action = PositionAction.SELL if self.action == PositionAction.BUY else PositionAction.BUY
        
        return Position(
            position_id=str(uuid.uuid4()),
            account_login=deal.account_login,
            symbol=deal.symbol,
            action=new_action,
            reason=PositionReason(deal.reason.value) if deal.reason.value in [
                r.value for r in PositionReason
            ] else PositionReason.CLIENT,
            volume=deal.volume,
            price_open=deal.price,
            price_current=deal.price,
            digits=deal.digits,
            digits_currency=deal.digits_currency,
            contract_size=deal.contract_size,
            deal_open=deal.deal_id,
            time_create=deal.created_at,
            time_update=deal.created_at,
            comment=deal.comment,
        )
    
    def _create_opposite_position_with_remaining(
        self, deal: "Deal", remaining_volume: Decimal
    ) -> "Position":
        """Create new position with remaining volume after reversal."""
        new_action = PositionAction.SELL if self.action == PositionAction.BUY else PositionAction.BUY
        
        return Position(
            position_id=str(uuid.uuid4()),
            account_login=deal.account_login,
            symbol=deal.symbol,
            action=new_action,
            reason=PositionReason.CLIENT,
            volume=Volume(remaining_volume),
            price_open=deal.price,
            price_current=deal.price,
            digits=deal.digits,
            digits_currency=deal.digits_currency,
            contract_size=deal.contract_size,
            deal_open=deal.deal_id,
            time_create=deal.created_at,
            time_update=deal.created_at,
            comment=f"[REVERSED from {self.position_id}] {deal.comment}",
        )
    
    # =========================================================================
    # PnL & MARGIN
    # =========================================================================
    
    def update_unrealized_pnl(
        self,
        current_price: Price,
        conversion_rate: Decimal = Decimal('1.0'),
    ) -> Money:
        """
        Update unrealized PnL based on current market price.
        
        Formula:
        - BUY: (current - open) * volume * contract_size * conversion_rate
        - SELL: (open - current) * volume * contract_size * conversion_rate
        """
        if self.action == PositionAction.BUY:
            price_diff = current_price.value - self.price_open.value
        else:
            price_diff = self.price_open.value - current_price.value
        
        pnl = price_diff * self.volume.value * self.contract_size * conversion_rate
        self.profit = Money(pnl, self.profit.currency)
        self.price_current = current_price
        self.time_update = datetime.now(timezone.utc)
        
        return self.profit
    
    def calculate_margin_required(
        self,
        margin_rate: Decimal = Decimal('1.0'),
        leverage: int = 100,
    ) -> Decimal:
        """
        Calculate margin required for this position.
        
        Formula: (volume * contract_size * price_open * margin_rate) / leverage
        """
        if leverage <= 0:
            leverage = 1
        
        notional = self.volume.value * self.contract_size * self.price_open.value
        return (notional * margin_rate) / Decimal(str(leverage))
    
    # =========================================================================
    # CLOSE-BY (MT5 Feature)
    # =========================================================================
    
    def close_by(self, opposite_position: "Position") -> None:
        """
        Close this position by an opposite position (MT5 Close-By).
        
        Both positions are closed against each other, with net PnL.
        """
        if opposite_position.symbol != self.symbol:
            raise ValueError("Close-by requires same symbol")
        if opposite_position.action == self.action:
            raise ValueError("Close-by requires opposite positions")
        
        # Determine close volume (minimum of both)
        close_volume = min(self.volume.value, opposite_position.volume.value)
        
        # Mark both as closed
        self.volume = Volume(self.volume.value - close_volume)
        opposite_position.volume = Volume(opposite_position.volume.value - close_volume)
        
        self.position_by_id = opposite_position.position_id
        opposite_position.position_by_id = self.position_id
        
        if self.volume.value == 0:
            self.time_done = datetime.now(timezone.utc)
        if opposite_position.volume.value == 0:
            opposite_position.time_done = datetime.now(timezone.utc)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "position_id": self.position_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "action": self.action.value,
            "volume": str(self.volume.value),
            "price_open": str(self.price_open.value),
            "price_current": str(self.price_current.value),
            "price_sl": str(self.price_sl.value) if self.price_sl else None,
            "price_tp": str(self.price_tp.value) if self.price_tp else None,
            "profit": str(self.profit.amount),
            "swap": str(self.swap.amount),
            "commission": str(self.commission.amount),
            "deal_open": self.deal_open,
            "deal_close": self.deal_close,
            "time_create": self.time_create.isoformat(),
            "time_update": self.time_update.isoformat(),
            "time_done": self.time_done.isoformat() if self.time_done else None,
            "comment": self.comment,
        }