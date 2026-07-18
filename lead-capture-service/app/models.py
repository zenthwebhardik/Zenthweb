import uuid
import enum

from sqlalchemy import Column, String, Text, Date, Time, DateTime, Enum, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class WebsiteType(str, enum.Enum):
    business = "business"
    ecommerce = "ecommerce"
    portfolio = "portfolio"
    blog = "blog"
    web_app = "web_app"
    landing_page = "landing_page"
    other = "other"


class BudgetRange(str, enum.Enum):
    under_10k = "under_10k"
    ten_to_30k = "10k_30k"
    thirty_to_75k = "30k_75k"
    seventyfive_to_150k = "75k_150k"
    above_150k = "above_150k"
    not_sure = "not_sure"


class Timeline(str, enum.Enum):
    asap = "asap"
    within_1_month = "within_1_month"
    one_to_3_months = "1_3_months"
    three_to_6_months = "3_6_months"
    flexible = "flexible"


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    converted = "converted"
    lost = "lost"


class LeadInquiry(Base):
    __tablename__ = "lead_inquiries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Contact details — email is the unique identity, one entry per email
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    phone = Column(String(30), nullable=True)
    company_name = Column(String(150), nullable=True)

    # Location
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Business info
    industry = Column(String(100), nullable=True)
    has_existing_website = Column(Boolean, default=False)
    existing_website_url = Column(String(300), nullable=True)
    business_description = Column(Text, nullable=True)

    # Project requirement
    website_type = Column(Enum(WebsiteType), nullable=False)
    features_needed = Column(JSONB, nullable=True)
    budget_range = Column(Enum(BudgetRange), nullable=False, default=BudgetRange.not_sure)
    timeline = Column(Enum(Timeline), nullable=False, default=Timeline.flexible)
    additional_requirements = Column(Text, nullable=True)
    reference_links = Column(JSONB, nullable=True)

    # Availability for call
    preferred_date = Column(Date, nullable=False)
    preferred_time_slot_start = Column(Time, nullable=False)
    preferred_time_slot_end = Column(Time, nullable=True)

    # Marketing attribution
    source = Column(String(100), nullable=True)
    utm_campaign = Column(String(150), nullable=True)

    # Internal tracking
    status = Column(Enum(LeadStatus), nullable=False, default=LeadStatus.new)
    exported_to_excel = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())