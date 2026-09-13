"""CreateClientHandler — the person/company record (MT5 IMTClient).

Administrator guide, *Creating Accounts*: the dialog's "Preferred Client" box
searches an EXISTING client by ID, name or contact and links the new account to
it. That is why this handler exists separately from CreateAccountHandler: one
client owns many accounts (demo + real + contest) without duplicating their
passport or address, and MT5 keeps the two objects apart for exactly that reason.

Rules encoded here:

* The client is OPTIONAL from the account's point of view. CreateAccountHandler
  links an existing client, creates one, or creates none - all three are legal.
* NO PASSWORD MATERIAL. MT5 puts PasswordHash / PhonePassword / OTPSecret on
  IMTUser (the account), not on IMTClient (the person): one client holding a demo
  and a real account has two investor passwords. The Client entity still declares
  those fields because migration 009 left the legacy columns in place, but this
  handler refuses to populate them - two writers for one number is the defect
  class this project keeps paying for (D1, D8b, D13, D16, D18).
* Duplicate detection is by the external KYC id, not by name: two people may
  share a name, and a passport number is the thing that identifies one.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.domains.accounts.client import Client
from core.domains.accounts.enums import ClientStatus
from core.events.domain_events import ClientCreated
from core.ports.interfaces import IClientRepository, IEventBus

logger = logging.getLogger(__name__)


class ClientRefusedError(ValueError):
    """The domain refused the client; the message is the reason (400 at the edge)."""


class ClientNotFoundError(ValueError):
    """No client with that id (404 at the edge)."""


@dataclass
class CreateClientCommand:
    """The KYC fields MT5's client record carries.

    Every field is optional except that at least one identifying field must be
    present - an anonymous client record is indistinguishable from a failed
    create, and the guide's own "Preferred Client" search works on ID, name or
    contact.
    """

    full_name: str = ""
    middle_name: str = ""
    company: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    zip_code: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    language: str = "en"
    #: IMTClient::PersonDocumentNumber - passport / TIN / national id.
    id_number: str = ""
    #: IMTClient::ClientExternalID - the back-office/KYC system's own key.
    external_id: str = ""
    #: MetaQuotes ID, for push notifications.
    mqid: str = ""
    lead_source: str = ""
    lead_campaign: str = ""
    comments: str = ""
    #: IMTClient::AssignedManager - the staff login that owns this relationship.
    agent_login: Optional[int] = None
    status: ClientStatus = ClientStatus.REGISTERED


class CreateClientHandler:
    """Handler for CreateClientCommand."""

    def __init__(self, client_repo: IClientRepository, event_bus: IEventBus) -> None:
        self.client_repo = client_repo
        self.event_bus = event_bus

    async def handle(
        self, command: CreateClientCommand, session: Any = None
    ) -> Client:
        """Create the client. Pass `session` to join the account-creation transaction."""
        if not any(
            str(getattr(command, f, "") or "").strip()
            for f in ("full_name", "company", "email", "phone", "id_number", "external_id")
        ):
            raise ClientRefusedError(
                "a client needs at least one identifying field (full_name, company, "
                "email, phone, id_number or external_id); an anonymous client record "
                "is indistinguishable from a failed create"
            )

        if command.id_number:
            for existing in await self.client_repo.find_all():
                if existing.id_number and existing.id_number == command.id_number:
                    raise ClientRefusedError(
                        f"a client with ID number {command.id_number!r} already exists "
                        f"({existing.id}); a passport number identifies one person"
                    )
        if command.external_id:
            clash = await self.client_repo.find_by_client_id(command.external_id)
            if clash is not None:
                raise ClientRefusedError(
                    f"external_id {command.external_id!r} is already client {clash.id}"
                )

        client = Client(
            full_name=command.full_name.strip(),
            middle_name=command.middle_name.strip(),
            company=command.company.strip(),
            country=command.country.strip(),
            state=command.state.strip(),
            city=command.city.strip(),
            zip_code=command.zip_code.strip(),
            address=command.address.strip(),
            phone=command.phone.strip(),
            email=command.email.strip(),
            language=(command.language or "en").strip(),
            id_number=command.id_number.strip(),
            external_id=command.external_id.strip(),
            # client_id is the external KYC id when one was supplied, so the
            # "Preferred Client" search can find this record by it.
            client_id=command.external_id.strip(),
            mqid=command.mqid.strip(),
            lead_source=command.lead_source.strip(),
            lead_campaign=command.lead_campaign.strip(),
            comments=command.comments,
            agent_login=command.agent_login,
            status=command.status,
            # password_hash / investor_password_hash / phone_password_hash /
            # otp_secret deliberately NOT set: see the module docstring.
        )

        saved = await self.client_repo.save(client, session=session)
        await self._publish(saved)
        logger.info("client %s created (%s)", saved.id, saved.full_name or saved.company or "unnamed")
        return saved

    async def _publish(self, client: Client) -> None:
        if self.event_bus is None:
            return
        await self.event_bus.publish(
            ClientCreated(
                aggregate_id=client.id,
                payload={
                    "client_id": client.id,
                    "external_id": client.external_id,
                    "status": client.status.name if hasattr(client.status, "name") else str(client.status),
                },
            )
        )
