import uuid
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schemas, models
from app.repositories.lead_repository import LeadRepository
from app.services.mail_service import send_confirmation_email


class LeadService:

    def __init__(self, db: Session):
        self.repo = LeadRepository(db)

    def get_my_lead(self, user_email: str) -> models.LeadInquiry | None:
        return self.repo.get_by_email(user_email)

    def submit_lead(
        self,
        lead: schemas.LeadInquiryCreate,
        user_email: str,
        background_tasks: BackgroundTasks,
    ) -> models.LeadInquiry:
        if lead.email != user_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only submit an inquiry for your own logged-in email",
            )

        try:
            created = self.repo.create(lead)
        except IntegrityError:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an inquiry on file. Use the update endpoint to edit it.",
            )

        background_tasks.add_task(send_confirmation_email, created.email, created.full_name)
        return created

    def update_my_lead(self, user_email: str, updates: schemas.LeadInquiryUpdate) -> models.LeadInquiry:
        lead = self.repo.get_by_email(user_email)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existing inquiry found — submit one first via POST /leads",
            )

        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)

        return self.repo.save(lead)

    def list_leads(self, skip: int = 0, limit: int = 100) -> list[models.LeadInquiry]:
        return self.repo.list_all(skip=skip, limit=limit)

    def get_pending_export(self) -> list[models.LeadInquiry]:
        return self.repo.list_pending_export()

    def mark_exported(self, lead_ids: list[uuid.UUID]) -> int:
        self.repo.mark_exported(lead_ids)
        return len(lead_ids)

    def get_lead_by_id(self, lead_id: uuid.UUID) -> models.LeadInquiry:
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return lead

    def update_status(self, lead_id: uuid.UUID, new_status: models.LeadStatus) -> models.LeadInquiry:
        lead = self.get_lead_by_id(lead_id)
        lead.status = new_status
        return self.repo.save(lead)