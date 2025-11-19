"""
Partner Management System

Handles partner onboarding, authentication, and account management
for the white-label platform.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
import hashlib
import json
from pathlib import Path


class PartnerTier(Enum):
    """Partner tier levels"""
    SECURITY_ESSENTIALS = "security-essentials"
    DOMAIN_INTELLIGENCE = "domain-intelligence"
    FULL_DISCOVERY = "full-discovery"


class PartnerStatus(Enum):
    """Partner account status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


@dataclass
class PartnerBilling:
    """Billing information"""
    tier: str
    monthly_fee: float
    revenue_share_percent: float
    billing_email: str
    payment_method: Optional[str] = None
    billing_address: Optional[Dict[str, str]] = None
    next_billing_date: Optional[datetime] = None

    # Usage-based metrics
    total_deployments: int = 0
    active_deployments: int = 0
    total_api_calls: int = 0
    total_widget_impressions: int = 0


@dataclass
class PartnerCredentials:
    """API credentials and keys"""
    api_key: str
    api_secret: str
    webhook_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_rotated: Optional[datetime] = None


@dataclass
class PartnerContact:
    """Partner contact information"""
    name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = None  # technical, billing, executive, etc.


@dataclass
class Partner:
    """Partner account"""
    partner_id: str
    company_name: str
    status: str  # PartnerStatus value
    tier: str  # PartnerTier value

    # Contacts
    primary_contact: PartnerContact
    technical_contact: Optional[PartnerContact] = None
    billing_contact: Optional[PartnerContact] = None

    # Credentials
    credentials: PartnerCredentials = None

    # Billing
    billing: PartnerBilling = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    onboarded_at: Optional[datetime] = None

    # Settings
    allowed_domains: List[str] = field(default_factory=list)
    webhook_url: Optional[str] = None
    custom_branding: Dict[str, Any] = field(default_factory=dict)

    # Features
    enabled_features: Dict[str, bool] = field(default_factory=dict)

    # Metrics
    total_dacs: int = 0
    total_users: int = 0

    def is_active(self) -> bool:
        """Check if partner is active"""
        return self.status == PartnerStatus.ACTIVE.value

    def can_deploy(self) -> bool:
        """Check if partner can deploy new DACs"""
        return self.is_active() and self.credentials and not self._is_credentials_expired()

    def _is_credentials_expired(self) -> bool:
        """Check if credentials are expired"""
        if not self.credentials or not self.credentials.expires_at:
            return False
        return datetime.now() > self.credentials.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'partner_id': self.partner_id,
            'company_name': self.company_name,
            'status': self.status,
            'tier': self.tier,
            'primary_contact': {
                'name': self.primary_contact.name,
                'email': self.primary_contact.email,
                'phone': self.primary_contact.phone,
                'role': self.primary_contact.role,
            },
            'technical_contact': {
                'name': self.technical_contact.name,
                'email': self.technical_contact.email,
                'phone': self.technical_contact.phone,
                'role': self.technical_contact.role,
            } if self.technical_contact else None,
            'billing_contact': {
                'name': self.billing_contact.name,
                'email': self.billing_contact.email,
                'phone': self.billing_contact.phone,
                'role': self.billing_contact.role,
            } if self.billing_contact else None,
            'credentials': {
                'api_key': self.credentials.api_key,
                'client_id': self.credentials.client_id,
                'created_at': self.credentials.created_at.isoformat(),
                'expires_at': self.credentials.expires_at.isoformat() if self.credentials.expires_at else None,
                'last_rotated': self.credentials.last_rotated.isoformat() if self.credentials.last_rotated else None,
            } if self.credentials else None,
            'billing': {
                'tier': self.billing.tier,
                'monthly_fee': self.billing.monthly_fee,
                'revenue_share_percent': self.billing.revenue_share_percent,
                'billing_email': self.billing.billing_email,
                'next_billing_date': self.billing.next_billing_date.isoformat() if self.billing.next_billing_date else None,
                'total_deployments': self.billing.total_deployments,
                'active_deployments': self.billing.active_deployments,
                'total_api_calls': self.billing.total_api_calls,
                'total_widget_impressions': self.billing.total_widget_impressions,
            } if self.billing else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'onboarded_at': self.onboarded_at.isoformat() if self.onboarded_at else None,
            'allowed_domains': self.allowed_domains,
            'webhook_url': self.webhook_url,
            'custom_branding': self.custom_branding,
            'enabled_features': self.enabled_features,
            'total_dacs': self.total_dacs,
            'total_users': self.total_users,
        }


class PartnerManager:
    """
    Partner account management system

    Responsibilities:
    - Partner onboarding
    - Credential management
    - Tier management
    - Usage tracking
    - Billing integration
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.partners: Dict[str, Partner] = {}
        self.api_key_index: Dict[str, str] = {}  # api_key -> partner_id
        self.storage_path = storage_path or Path("./partner_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_partner(
        self,
        company_name: str,
        tier: PartnerTier,
        primary_contact: PartnerContact,
        allowed_domains: List[str] = None
    ) -> Partner:
        """
        Create new partner account

        Returns:
            Partner with generated credentials
        """
        # Generate partner ID
        partner_id = self._generate_partner_id(company_name)

        # Generate credentials
        credentials = self._generate_credentials()

        # Setup billing based on tier
        billing = self._setup_billing(tier, primary_contact.email)

        # Create partner
        partner = Partner(
            partner_id=partner_id,
            company_name=company_name,
            status=PartnerStatus.PENDING.value,
            tier=tier.value,
            primary_contact=primary_contact,
            credentials=credentials,
            billing=billing,
            allowed_domains=allowed_domains or [],
            enabled_features=self._get_tier_features(tier)
        )

        self.partners[partner_id] = partner
        self.api_key_index[credentials.api_key] = partner_id

        self._save_partner(partner)
        return partner

    def activate_partner(self, partner_id: str) -> Partner:
        """Activate partner after onboarding complete"""
        partner = self.get_partner(partner_id)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        partner.status = PartnerStatus.ACTIVE.value
        partner.onboarded_at = datetime.now()
        partner.updated_at = datetime.now()

        self._save_partner(partner)
        return partner

    def suspend_partner(self, partner_id: str, reason: str = None) -> Partner:
        """Suspend partner account"""
        partner = self.get_partner(partner_id)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        partner.status = PartnerStatus.SUSPENDED.value
        partner.updated_at = datetime.now()

        # Log suspension reason
        if reason:
            partner.custom_branding['suspension_reason'] = reason

        self._save_partner(partner)
        return partner

    def get_partner(self, partner_id: str) -> Optional[Partner]:
        """Get partner by ID"""
        return self.partners.get(partner_id)

    def get_partner_by_api_key(self, api_key: str) -> Optional[Partner]:
        """Get partner by API key"""
        partner_id = self.api_key_index.get(api_key)
        if partner_id:
            return self.partners.get(partner_id)
        return None

    def list_partners(
        self,
        tier: Optional[PartnerTier] = None,
        status: Optional[PartnerStatus] = None
    ) -> List[Partner]:
        """List partners with optional filtering"""
        partners = list(self.partners.values())

        if tier:
            partners = [p for p in partners if p.tier == tier.value]

        if status:
            partners = [p for p in partners if p.status == status.value]

        return partners

    def rotate_credentials(self, partner_id: str) -> PartnerCredentials:
        """Rotate partner API credentials"""
        partner = self.get_partner(partner_id)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        # Remove old API key from index
        if partner.credentials:
            self.api_key_index.pop(partner.credentials.api_key, None)

        # Generate new credentials
        new_credentials = self._generate_credentials()
        new_credentials.last_rotated = datetime.now()

        partner.credentials = new_credentials
        partner.updated_at = datetime.now()

        # Update index
        self.api_key_index[new_credentials.api_key] = partner_id

        self._save_partner(partner)
        return new_credentials

    def upgrade_tier(self, partner_id: str, new_tier: PartnerTier) -> Partner:
        """Upgrade partner to higher tier"""
        partner = self.get_partner(partner_id)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        partner.tier = new_tier.value
        partner.billing = self._setup_billing(new_tier, partner.billing.billing_email)
        partner.enabled_features = self._get_tier_features(new_tier)
        partner.updated_at = datetime.now()

        self._save_partner(partner)
        return partner

    def record_deployment(self, partner_id: str):
        """Record a new deployment for billing"""
        partner = self.get_partner(partner_id)
        if partner and partner.billing:
            partner.billing.total_deployments += 1
            partner.billing.active_deployments += 1
            partner.total_dacs += 1
            self._save_partner(partner)

    def record_api_call(self, partner_id: str, count: int = 1):
        """Record API calls for billing"""
        partner = self.get_partner(partner_id)
        if partner and partner.billing:
            partner.billing.total_api_calls += count
            self._save_partner(partner)

    def record_widget_impression(self, partner_id: str, count: int = 1):
        """Record widget impressions for analytics"""
        partner = self.get_partner(partner_id)
        if partner and partner.billing:
            partner.billing.total_widget_impressions += count
            self._save_partner(partner)

    def _generate_partner_id(self, company_name: str) -> str:
        """Generate unique partner ID"""
        # Clean company name
        clean_name = ''.join(c for c in company_name.lower() if c.isalnum() or c == '-')
        clean_name = clean_name[:20]

        # Add random suffix to ensure uniqueness
        suffix = secrets.token_hex(4)
        return f"{clean_name}-{suffix}"

    def _generate_credentials(self) -> PartnerCredentials:
        """Generate API credentials"""
        api_key = f"iv_{secrets.token_urlsafe(32)}"
        api_secret = secrets.token_urlsafe(64)
        webhook_secret = secrets.token_urlsafe(32)
        client_id = f"client_{secrets.token_hex(16)}"
        client_secret = secrets.token_urlsafe(48)

        # Credentials expire in 1 year
        expires_at = datetime.now() + timedelta(days=365)

        return PartnerCredentials(
            api_key=api_key,
            api_secret=api_secret,
            webhook_secret=webhook_secret,
            client_id=client_id,
            client_secret=client_secret,
            expires_at=expires_at
        )

    def _setup_billing(self, tier: PartnerTier, billing_email: str) -> PartnerBilling:
        """Setup billing based on tier"""
        tier_pricing = {
            PartnerTier.SECURITY_ESSENTIALS: (10000, 30),  # $10K/mo, 30% share
            PartnerTier.DOMAIN_INTELLIGENCE: (37500, 35),  # $37.5K/mo, 35% share
            PartnerTier.FULL_DISCOVERY: (300000, 40),  # $300K/mo, 40% share
        }

        monthly_fee, revenue_share = tier_pricing[tier]

        return PartnerBilling(
            tier=tier.value,
            monthly_fee=monthly_fee,
            revenue_share_percent=revenue_share,
            billing_email=billing_email,
            next_billing_date=datetime.now() + timedelta(days=30)
        )

    def _get_tier_features(self, tier: PartnerTier) -> Dict[str, bool]:
        """Get enabled features for tier"""
        base_features = {
            'ai_shield': True,
            'compliance_monitoring': True,
            'threat_detection': True,
        }

        domain_features = {
            **base_features,
            'predictive_maintenance': True,
            'energy_monitoring': True,
            'grid_validation': True,
            'swarm_monitoring': True,
        }

        discovery_features = {
            **domain_features,
            'shadow_twin': True,
            'research_explorer': True,
            'i3_integration': True,
            'rdr_engine': True,
            'msep_integration': True,
            'quantum_monitoring': True,
            'proof_of_insight': True,
        }

        if tier == PartnerTier.SECURITY_ESSENTIALS:
            return base_features
        elif tier == PartnerTier.DOMAIN_INTELLIGENCE:
            return domain_features
        else:
            return discovery_features

    def _save_partner(self, partner: Partner):
        """Save partner to storage"""
        partner_dir = self.storage_path / partner.partner_id
        partner_dir.mkdir(parents=True, exist_ok=True)

        partner_file = partner_dir / 'partner.json'
        with open(partner_file, 'w') as f:
            json.dump(partner.to_dict(), f, indent=2)

    def _load_partner(self, partner_id: str) -> Optional[Partner]:
        """Load partner from storage"""
        partner_file = self.storage_path / partner_id / 'partner.json'

        if not partner_file.exists():
            return None

        with open(partner_file, 'r') as f:
            data = json.load(f)

        # Reconstruct partner object
        primary_contact = PartnerContact(**data['primary_contact'])
        technical_contact = PartnerContact(**data['technical_contact']) if data.get('technical_contact') else None
        billing_contact = PartnerContact(**data['billing_contact']) if data.get('billing_contact') else None

        credentials = None
        if data.get('credentials'):
            cred_data = data['credentials']
            credentials = PartnerCredentials(
                api_key=cred_data['api_key'],
                api_secret='***',  # Don't store in JSON
                webhook_secret='***',
                client_id=cred_data.get('client_id'),
                client_secret='***',
                created_at=datetime.fromisoformat(cred_data['created_at']),
                expires_at=datetime.fromisoformat(cred_data['expires_at']) if cred_data.get('expires_at') else None,
                last_rotated=datetime.fromisoformat(cred_data['last_rotated']) if cred_data.get('last_rotated') else None,
            )

        billing = None
        if data.get('billing'):
            bill_data = data['billing']
            billing = PartnerBilling(
                tier=bill_data['tier'],
                monthly_fee=bill_data['monthly_fee'],
                revenue_share_percent=bill_data['revenue_share_percent'],
                billing_email=bill_data['billing_email'],
                next_billing_date=datetime.fromisoformat(bill_data['next_billing_date']) if bill_data.get('next_billing_date') else None,
                total_deployments=bill_data.get('total_deployments', 0),
                active_deployments=bill_data.get('active_deployments', 0),
                total_api_calls=bill_data.get('total_api_calls', 0),
                total_widget_impressions=bill_data.get('total_widget_impressions', 0),
            )

        partner = Partner(
            partner_id=data['partner_id'],
            company_name=data['company_name'],
            status=data['status'],
            tier=data['tier'],
            primary_contact=primary_contact,
            technical_contact=technical_contact,
            billing_contact=billing_contact,
            credentials=credentials,
            billing=billing,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            onboarded_at=datetime.fromisoformat(data['onboarded_at']) if data.get('onboarded_at') else None,
            allowed_domains=data.get('allowed_domains', []),
            webhook_url=data.get('webhook_url'),
            custom_branding=data.get('custom_branding', {}),
            enabled_features=data.get('enabled_features', {}),
            total_dacs=data.get('total_dacs', 0),
            total_users=data.get('total_users', 0),
        )

        return partner

    def load_all_partners(self):
        """Load all partners from storage"""
        if not self.storage_path.exists():
            return

        for partner_dir in self.storage_path.iterdir():
            if partner_dir.is_dir():
                partner = self._load_partner(partner_dir.name)
                if partner:
                    self.partners[partner.partner_id] = partner
                    if partner.credentials:
                        self.api_key_index[partner.credentials.api_key] = partner.partner_id

    def get_stats(self) -> Dict[str, Any]:
        """Get partner statistics"""
        total_partners = len(self.partners)
        active_partners = sum(1 for p in self.partners.values() if p.status == PartnerStatus.ACTIVE.value)

        tier_distribution = {}
        for partner in self.partners.values():
            tier_distribution[partner.tier] = tier_distribution.get(partner.tier, 0) + 1

        total_deployments = sum(p.billing.total_deployments for p in self.partners.values() if p.billing)
        total_api_calls = sum(p.billing.total_api_calls for p in self.partners.values() if p.billing)

        monthly_revenue = sum(p.billing.monthly_fee for p in self.partners.values()
                             if p.billing and p.status == PartnerStatus.ACTIVE.value)

        return {
            'total_partners': total_partners,
            'active_partners': active_partners,
            'tier_distribution': tier_distribution,
            'total_deployments': total_deployments,
            'total_api_calls': total_api_calls,
            'monthly_recurring_revenue': monthly_revenue,
        }


# Global partner manager instance
_partner_manager: Optional[PartnerManager] = None


def get_partner_manager(storage_path: Optional[Path] = None) -> PartnerManager:
    """Get or create global partner manager"""
    global _partner_manager
    if _partner_manager is None:
        _partner_manager = PartnerManager(storage_path)
        _partner_manager.load_all_partners()
    return _partner_manager
