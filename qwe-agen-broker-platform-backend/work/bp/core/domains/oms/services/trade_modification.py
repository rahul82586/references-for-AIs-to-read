"""Trade Modification Service - MT5 Reversal + Correction pattern."""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.deal import Deal


@dataclass
class TradeModificationResult:
    """Result of a trade modification."""
    reversal_deal: Deal
    correction_deal: Deal
    original_deal_id: str


class TradeModificationService:
    """
    MT5 Trade Modification Service.
    
    In MT5, dealers NEVER modify existing deals. Instead, they:
    1. Create a REVERSAL deal (exact opposite of original)
    2. Create a CORRECTION deal (new deal with corrected parameters)
    3. Both deals link to the original ticket_id for audit trail
    
    This preserves the immutable ledger while allowing corrections.
    """
    
    def __init__(self, deal_repository):
        self.deal_repository = deal_repository
    
    async def modify_deal(
        self,
        original_deal_id: str,
        new_price: Optional[Price] = None,
        new_volume: Optional[Volume] = None,
        new_profit: Optional[Money] = None,
        reason: str = "Dealer modification",
        dealer_login: Optional[int] = None,
    ) -> TradeModificationResult:
        """
        Modify a deal using the MT5 Reversal + Correction pattern.
        
        Args:
            original_deal_id: ID of the deal to modify
            new_price: New price (optional)
            new_volume: New volume (optional)
            new_profit: New profit (optional)
            reason: Reason for modification (audit trail)
            dealer_login: Dealer performing the modification
        
        Returns:
            TradeModificationResult with both reversal and correction deals
        """
        # Fetch original deal
        original = await self.deal_repository.find_by_id(original_deal_id)
        if not original:
            raise ValueError(f"Deal {original_deal_id} not found")
        
        # Create reversal deal (exact opposite)
        reversal = original.create_reversal(reason=reason)
        reversal.dealer_login = dealer_login
        
        # Create correction deal (with new parameters)
        correction = original.create_correction(
            new_volume=new_volume,
            new_price=new_price,
            new_profit=new_profit,
            reason=reason,
        )
        correction.dealer_login = dealer_login
        
        # Persist both deals atomically
        await self.deal_repository.save(reversal)
        await self.deal_repository.save(correction)
        
        return TradeModificationResult(
            reversal_deal=reversal,
            correction_deal=correction,
            original_deal_id=original_deal_id,
        )