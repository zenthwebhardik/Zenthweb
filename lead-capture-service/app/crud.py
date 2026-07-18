import uuid
from sqlalchemy.orm import Session

from app import models, schemas


def create_lead(db: Session, lead: schemas.LeadInquiryCreate) -> models.LeadInquiry:
    db_lead = models.LeadInquiry(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_lead(db: Session, lead_id: uuid.UUID) -> models.LeadInquiry | None:
    return db.query(models.LeadInquiry).filter(models.LeadInquiry.id == lead_id).first()


def get_lead_by_email(db: Session, email: str) -> models.LeadInquiry | None:
    """Ek email = ek hi entry, isliye .first() hi kaafi hai."""
    return db.query(models.LeadInquiry).filter(models.LeadInquiry.email == email).first()


def list_leads(db: Session, skip: int = 0, limit: int = 100) -> list[models.LeadInquiry]:
    return (
        db.query(models.LeadInquiry)
        .order_by(models.LeadInquiry.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_own_lead(
    db: Session, owner_email: str, updates: schemas.LeadInquiryUpdate
) -> models.LeadInquiry | None:
    """Sirf apni hi entry update kar sakta hai — email se match karke."""
    lead = get_lead_by_email(db, owner_email)
    if not lead:
        return None

    update_data = updates.model_dump(exclude_unset=True)  # sirf jo fields bheje gaye hain
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead


def update_status(db: Session, lead_id: uuid.UUID, status: models.LeadStatus) -> models.LeadInquiry | None:
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None
    db_lead.status = status
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_pending_export_leads(db: Session) -> list[models.LeadInquiry]:
    return db.query(models.LeadInquiry).filter(
        models.LeadInquiry.exported_to_excel == False  # noqa: E712
    ).all()


def mark_leads_exported(db: Session, lead_ids: list[uuid.UUID]) -> None:
    db.query(models.LeadInquiry).filter(
        models.LeadInquiry.id.in_(lead_ids)
    ).update({models.LeadInquiry.exported_to_excel: True}, synchronize_session=False)
    db.commit()