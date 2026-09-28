"""Deal entity - Immutable execution record (IMTDeal)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # forward references in annotations only (no runtime import cycle)
    from core.domains.oms.entities.order import Order
import uuid

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.enums import (
    OrderType, DealType, DealEntry, DealReason
)


@dataclass
class Deal:
    """
    Deal Entity - Immutable Execution Record (IMTDeal).
    
    A Deal is a HISTORICAL FACT. Once created, it is NEVER modified.
    Corrections are handled via Trade Modification (Reversal + Correction).
    
    MT5 Deal Entry Types:
    - IN: Opens a position
    - OUT: Closes a position
    - INOUT: Reverses a position
    - OUT_BY: Closes by opposite position
    """
    # Identity
    deal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = None  # Link to originating order
    position_id: Optional[str] = None  # Link to position
    
    # Account
    account_login: int = 0
    dealer_login: Optional[int] = None
    
    # Symbol & trade
    symbol: str = ""
    deal_type: DealType = DealType.BUY
    entry: DealEntry = DealEntry.IN  # How it affects position
    reason: DealReason = DealReason.CLIENT
    
    # Volume & price
    volume: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    price: Price = field(default_factory=lambda: Price(Decimal('0')))
    
    # External references
    external_id: Optional[str] = None  # Exchange/ECN deal ID
    order_ticket: Optional[str] = None  # Original order ticket
    
    # Financial
    profit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    swap: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    commission: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    
    # Symbol metadata
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Comment
    comment: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create_from_order(
        cls,
        order: "Order",
        fill_volume: Volume,
        fill_price: Price,
        entry: DealEntry = DealEntry.IN,
        reason: DealReason = DealReason.CLIENT,
        profit: Optional[Money] = None,
    ) -> "Deal":
        """Create a Deal from an Order fill."""
        from core.domains.oms.entities.order import Order
        
        # Map OrderType to DealType
        deal_type = cls._order_type_to_deal_type(order.order_type)
        
        return cls(
            order_id=order.ticket_id,
            account_login=order.account_login,
            symbol=order.symbol,
            deal_type=deal_type,
            entry=entry,
            reason=reason,
            volume=fill_volume,
            price=fill_price,
            order_ticket=order.ticket_id,
            digits=order.digits,
            digits_currency=order.digits_currency,
            contract_size=order.contract_size,
            profit=profit or Money(Decimal('0'), "USD"),
        )
    
    @staticmethod
    def _order_type_to_deal_type(order_type: OrderType) -> DealType:
        """Map OrderType to DealType."""
        if order_type in [OrderType.BUY, OrderType.BUY_LIMIT,
                          OrderType.BUY_STOP, OrderType.BUY_STOP_LIMIT]:
            return DealType.BUY
        return DealType.SELL
    
    # =========================================================================
    # TRADE MODIFICATION (MT5 Pattern)
    # =========================================================================
    
    def create_reversal(self, reason: str = "Trade modification") -> "Deal":
        """
        Create a REVERSAL deal - exact opposite of this deal.
        
        Used in MT5 Trade Modification to undo a deal before applying correction.
        The reversal deal has:
        - Opposite deal_type (BUY -> SELL, SELL -> BUY)
        - Negated profit, swap, commission
        - Link to original deal_id
        """
        reversed_type = DealType.SELL if self.deal_type == DealType.BUY else DealType.BUY
        
        return Deal(
            deal_id=str(uuid.uuid4()),
            order_id=self.order_id,
            position_id=self.position_id,
            account_login=self.account_login,
            symbol=self.symbol,
            deal_type=reversed_type,
            entry=self.entry,
            reason=DealReason.DEALER,
            volume=self.volume,
            price=self.price,
            order_ticket=self.order_ticket,
            digits=self.digits,
            digits_currency=self.digits_currency,
            contract_size=self.contract_size,
            # Negate financials
            profit=Money(-self.profit.amount, self.profit.currency),
            swap=Money(-self.swap.amount, self.swap.currency),
            commission=Money(-self.commission.amount, self.commission.currency),
            comment=f"[REVERSAL of {self.deal_id}] {reason}",
            created_at=datetime.now(timezone.utc),
        )
    
    def create_correction(
        self,
        new_volume: Optional[Volume] = None,
        new_price: Optional[Price] = None,
        new_profit: Optional[Money] = None,
        reason: str = "Trade modification",
    ) -> "Deal":
        """
        Create a CORRECTION deal - new deal with corrected parameters.
        
        Used after a reversal to apply the corrected values.
        """
        return Deal(
            deal_id=str(uuid.uuid4()),
            order_id=self.order_id,
            position_id=self.position_id,
            account_login=self.account_login,
            symbol=self.symbol,
            deal_type=self.deal_type,
            entry=self.entry,
            reason=DealReason.DEALER,
            volume=new_volume or self.volume,
            price=new_price or self.price,
            order_ticket=self.order_ticket,
            digits=self.digits,
            digits_currency=self.digits_currency,
            contract_size=self.contract_size,
            profit=new_profit or self.profit,
            swap=self.swap,
            commission=self.commission,
            comment=f"[CORRECTION of {self.deal_id}] {reason}",
            created_at=datetime.now(timezone.utc),
        )
    
    # =========================================================================
    # PnL CALCULATION
    # =========================================================================
    
    def calculate_realized_pnl(
        self,
        open_price: Price,
        close_price: Price,
        account_currency: str,
        conversion_rate: Decimal = Decimal('1.0'),
    ) -> Money:
        """
        Calculate realized PnL for a closing deal.
        
        Formula (for BUY close):
        pnl = (close_price - open_price) * volume * contract_size * conversion_rate
        
        Formula (for SELL close):
        pnl = (open_price - close_price) * volume * contract_size * conversion_rate
        """
        if self.deal_type == DealType.BUY:
            price_diff = close_price.value - open_price.value
        else:
            price_diff = open_price.value - close_price.value
        
        pnl = price_diff * self.volume.value * self.contract_size * conversion_rate
        
        return Money(pnl, account_currency)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "deal_id": self.deal_id,
            "order_id": self.order_id,
            "position_id": self.position_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "deal_type": self.deal_type.value,
            "entry": self.entry.value,
            "reason": self.reason.value,
            "volume": str(self.volume.value),
            "price": str(self.price.value),
            "profit": str(self.profit.amount),
            "swap": str(self.swap.amount),
            "commission": str(self.commission.amount),
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }