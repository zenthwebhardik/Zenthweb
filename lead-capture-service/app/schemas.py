import uuid
from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import WebsiteType, BudgetRange, Timeline, LeadStatus


class LeadInquiryCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=150)

    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

    industry: Optional[str] = Field(None, max_length=100)
    has_existing_website: bool = False
    existing_website_url: Optional[str] = Field(None, max_length=300)
    business_description: Optional[str] = None

    website_type: WebsiteType
    features_needed: Optional[list[str]] = None
    budget_range: BudgetRange = BudgetRange.not_sure
    timeline: Timeline = Timeline.flexible
    additional_requirements: Optional[str] = None
    reference_links: Optional[list[str]] = None

    preferred_date: date
    preferred_time_slot_start: time
    preferred_time_slot_end: Optional[time] = None

    source: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=150)


class LeadInquiryUpdate(BaseModel):
    """Same fields, all optional — user only sends what they're changing."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=150)

    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

    industry: Optional[str] = Field(None, max_length=100)
    has_existing_website: Optional[bool] = None
    existing_website_url: Optional[str] = Field(None, max_length=300)
    business_description: Optional[str] = None

    website_type: Optional[WebsiteType] = None
    features_needed: Optional[list[str]] = None
    budget_range: Optional[BudgetRange] = None
    timeline: Optional[Timeline] = None
    additional_requirements: Optional[str] = None
    reference_links: Optional[list[str]] = None

    preferred_date: Optional[date] = None
    preferred_time_slot_start: Optional[time] = None
    preferred_time_slot_end: Optional[time] = None

    source: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=150)


class LeadInquiryResponse(LeadInquiryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: LeadStatus
    exported_to_excel: bool
    created_at: datetime
    updated_at: datetime


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class MarkExportedRequest(BaseModel):
    lead_ids: list[uuid.UUID]