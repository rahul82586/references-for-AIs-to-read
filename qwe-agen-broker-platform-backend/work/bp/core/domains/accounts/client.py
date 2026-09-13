"""Client entity - Personal information & authentication (IMTUser)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from .enums import ClientStatus


@dataclass
class Client:
    """
    Client Entity - Personal Information & Authentication (IMTUser)
    
    Represents the person/company. One Client can have multiple Accounts.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""  # External KYC ID
    mqid: str = ""  # MetaQuotes ID (for push notifications)
    
    # Personal info
    full_name: str = ""
    company: str = ""
    country: str = ""
    #: IMTClient::AddressState - migration 009 column `state`.
    state: str = ""
    city: str = ""
    zip_code: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    language: str = "en"
    #: IMTClient::PersonMiddleName. MT5 stores first/middle/last separately on
    #: IMTUser; the person record carries the middle name too.
    middle_name: str = ""
    #: IMTClient::PersonDocumentNumber - passport / national id / TIN.
    id_number: str = ""
    #: IMTClient::LeadSource / LeadCampaign. Present on BOTH the client and the
    #: account in MT5 (IMTUser has them too); the account's copy is what a
    #: per-login attribution report reads, the client's is the person-level one.
    lead_source: str = ""
    lead_campaign: str = ""
    
    # Authentication
    #
    # DEPRECATED LOCATION (step 5). MT5 puts per-ACCOUNT password material on
    # IMTUser - PasswordHash(type), PhonePassword, OTPSecret - not on the person:
    # one client holding a demo and a real account has TWO investor passwords.
    # The authoritative copies now live on Account (investor_password_hash,
    # phone_password_hash, webapi_password_hash, otp_secret). These four are kept
    # declared and still round-tripped so no existing row loses data, but
    # nothing NEW writes them: CreateClientHandler leaves them empty and
    # CreateAccountHandler provisions the account side. Two writers for one
    # number is the defect class this project keeps paying for.
    password_hash: str = ""
    investor_password_hash: str = ""
    phone_password_hash: str = ""
    otp_secret: Optional[str] = None
    certificate_fingerprint: Optional[str] = None
    
    # Status
    status: ClientStatus = ClientStatus.REGISTERED
    comments: str = ""
    external_id: str = ""
    
    # Agent (IB)
    agent_login: Optional[int] = None
    
    # Dates
    registration_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_visit: Optional[datetime] = None
    last_pass_change: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_active(self) -> bool:
        """Check if client is active."""
        return self.status in [
            ClientStatus.REGISTERED,
            ClientStatus.FUNDED,
            ClientStatus.ACTIVE
        ]
    
    def can_trade(self) -> bool:
        """Check if client can trade (not suspended/closed)."""
        return self.status not in [
            ClientStatus.SUSPENDED,
            ClientStatus.CLOSED,
            ClientStatus.TERMINATED
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert client to dictionary."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "mqid": self.mqid,
            "full_name": self.full_name,
            "company": self.company,
            "country": self.country,
            "city": self.city,
            "email": self.email,
            "phone": self.phone,
            "language": self.language,
            "middle_name": self.middle_name,
            "state": self.state,
            "id_number": self.id_number,
            "lead_source": self.lead_source,
            "lead_campaign": self.lead_campaign,
            "address": self.address,
            "zip_code": self.zip_code,
            "status": self.status.name,
            "registration_date": self.registration_date.isoformat(),
            "last_visit": self.last_visit.isoformat() if self.last_visit else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }