import uuid
from sqlalchemy.orm import Session

from app import models, schemas


class LeadRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, lead: schemas.LeadInquiryCreate) -> models.LeadInquiry:
        db_lead = models.LeadInquiry(**lead.model_dump())
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def get_by_id(self, lead_id: uuid.UUID) -> models.LeadInquiry | None:
        return self.db.query(models.LeadInquiry).filter(models.LeadInquiry.id == lead_id).first()

    def get_by_email(self, email: str) -> models.LeadInquiry | None:
        return self.db.query(models.LeadInquiry).filter(models.LeadInquiry.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[models.LeadInquiry]:
        return (
            self.db.query(models.LeadInquiry)
            .order_by(models.LeadInquiry.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_pending_export(self) -> list[models.LeadInquiry]:
        return self.db.query(models.LeadInquiry).filter(
            models.LeadInquiry.exported_to_excel == False  # noqa: E712
        ).all()

    def save(self, lead: models.LeadInquiry) -> models.LeadInquiry:
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def mark_exported(self, lead_ids: list[uuid.UUID]) -> None:
        self.db.query(models.LeadInquiry).filter(
            models.LeadInquiry.id.in_(lead_ids)
        ).update({models.LeadInquiry.exported_to_excel: True}, synchronize_session=False)
        self.db.commit()