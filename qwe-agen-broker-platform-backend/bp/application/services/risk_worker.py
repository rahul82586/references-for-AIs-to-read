import asyncio
import logging
from typing import List, Dict
from decimal import Decimal

from core.domains.risk.engine import RiskEngine
from core.domains.risk.models import MarginSnapshot, RiskStatus
from core.domains.accounts.models import Account
from core.domains.oms.entities.position import Position
from core.ports.interfaces import (
    IAccountRepository,
    IPositionRepository,
    IEventBus
)
from core.events.domain_events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class RiskWorker:
    """
    Background worker that runs the risk check loop.

    Architectural Purpose:
    Runs asynchronously alongside the API server to continuously monitor
    all client accounts for margin violations. This is the core protection
    mechanism that prevents client losses from exceeding broker capital.

    MT5 Compliance:
    - Runs every 1-5 seconds (configurable)
    - Margin Call: Notifies client when margin_level < margin_call_level
    - Stop Out: Auto-closes positions when margin_level < stop_out_level
    - Liquidation order: Worst-loss positions first

    Fault Tolerance:
    Each account check is wrapped in try/except so one failing account
    never brings down the entire risk monitoring system.
    """

    def __init__(self,
                 risk_engine: RiskEngine,
                 account_repo: IAccountRepository,
                 position_repo: IPositionRepository,
                 event_bus: IEventBus,
                 check_interval_seconds: int = 5):
        self.risk_engine = risk_engine
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.event_bus = event_bus
        self.check_interval_seconds = check_interval_seconds
        self._running = False

    async def start(self):
        """
        Main loop: fetch all active accounts, check margin, emit events.

        This method runs indefinitely until stopped. It should be started
        as a background task alongside the main API server.
        """
        self._running = True
        logger.info(f"RiskWorker started with interval={self.check_interval_seconds}s")

        while self._running:
            try:
                await self._run_check_cycle()
            except Exception as e:
                logger.error(f"RiskWorker cycle error: {e}", exc_info=True)

            await asyncio.sleep(self.check_interval_seconds)

    def stop(self):
        """Signal the worker to stop after current cycle."""
        self._running = False
        logger.info("RiskWorker stopping...")

    async def _run_check_cycle(self):
        """
        One full check cycle:
        1. Fetch all accounts with open positions
        2. For each, calculate MarginSnapshot
        3. If margin_call → emit MarginCallEvent + notify
        4. If stop_out → select positions + emit StopOutEvent
        5. Publish RiskStatusUpdatedEvent for each account

        Robustness: Individual account errors are caught and logged,
        but do not interrupt processing of other accounts.
        """
        try:
            # Get all accounts with open positions
            all_positions = await self.position_repo.get_open_positions()

            # Group positions by account login
            positions_by_account: Dict[str, List[Position]] = {}
            for position in all_positions:
                if position.account_login not in positions_by_account:
                    positions_by_account[position.account_login] = []
                positions_by_account[position.account_login].append(position)

            logger.debug(f"Checking {len(positions_by_account)} accounts with open positions")

            # Process each account with positions
            for account_login, positions in positions_by_account.items():
                try:
                    # Fetch account details
                    account = await self.account_repo.find_by_login(account_login)
                    if not account or not account.is_enabled:
                        continue

                    # Calculate margin snapshot
                    snapshot = self.risk_engine.calculate_margin_level(account, positions)

                    # Check for margin call
                    if self.risk_engine.detect_margin_call(account, snapshot):
                        logger.warning(
                            f"Margin Call triggered for {account_login}: "
                            f"Level={snapshot.margin_level:.2f}%"
                        )

                        # Emit margin call event
                        margin_call_event = DomainEvent(
                            event_type=EventType.MARGIN_CALL_TRIGGERED,
                            aggregate_id=account_login,
                            payload={
                                'account_login': account_login,
                                'margin_level': str(snapshot.margin_level),
                                'equity': str(snapshot.equity),
                                'margin_used': str(snapshot.margin_used),
                                'balance': str(snapshot.balance)
                            }
                        )
                        await self.event_bus.publish(margin_call_event)

                    # Check for stop out
                    if self.risk_engine.detect_stop_out(account, snapshot):
                        logger.critical(
                            f"Stop Out triggered for {account_login}: "
                            f"Level={snapshot.margin_level:.2f}%"
                        )

                        # Select positions for liquidation (worst first)
                        positions_to_close = self.risk_engine.select_positions_for_liquidation(
                            positions=positions,
                            # group.margin.stop_out_level, in percent.
                            target_margin_level=Decimal(
                                str(
                                    account.group.margin.stop_out_level
                                    if account.group
                                    else '50'
                                )
                            ),
                            current_equity=snapshot.equity,
                            symbol_repo=self.risk_engine.symbol_repo,
                            market_feed=getattr(self.risk_engine, 'market_data_engine', getattr(self.risk_engine, 'market_feed', None))
                        )

                        # Emit stop out event
                        stop_out_event = DomainEvent(
                            event_type=EventType.STOP_OUT_INITIATED,
                            aggregate_id=account_login,
                            payload={
                                'account_login': account_login,
                                'margin_level': str(snapshot.margin_level),
                                'positions_to_close': [p.id for p in positions_to_close],
                                'reason': f'Margin level {snapshot.margin_level:.2f}% below stop-out threshold'
                            }
                        )
                        await self.event_bus.publish(stop_out_event)

                        # Emit force-close event for each position
                        # Note: Actual closing logic is handled by a separate command handler
                        # that listens for STOP_OUT_INITIATED events
                        for position in positions_to_close[:1]:  # Close one at a time to recheck margin
                            force_close_event = DomainEvent(
                                event_type=EventType.POSITION_FORCE_CLOSED,
                                aggregate_id=position.id,
                                payload={
                                    'account_login': account_login,
                                    'position_id': position.id,
                                    'symbol': position.symbol,
                                    'volume': str(position.volume.value),
                                    'close_reason': 'STOP_OUT',
                                    'margin_level': str(snapshot.margin_level)
                                }
                            )
                            await self.event_bus.publish(force_close_event)
                            break  # Close one, then re-evaluate in next cycle

                    # Always publish status update for UI/dashboard
                    status_update_event = DomainEvent(
                        event_type=EventType.RISK_STATUS_UPDATED,
                        aggregate_id=account_login,
                        payload={
                            'account_login': account_login,
                            'risk_status': snapshot.status.value,
                            'margin_level': str(snapshot.margin_level),
                            'equity': str(snapshot.equity),
                            'margin_used': str(snapshot.margin_used)
                        }
                    )
                    await self.event_bus.publish(status_update_event)

                except Exception as account_error:
                    logger.error(
                        f"Error processing account {account_login}: {account_error}",
                        exc_info=True
                    )
                    # Continue with next account - never let one failure stop the loop

        except Exception as e:
            logger.error(f"Error in risk check cycle: {e}", exc_info=True)
            # Don't re-raise - we want the loop to continue
