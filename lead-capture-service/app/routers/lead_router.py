import uuid
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.services.lead_service import LeadService

router = APIRouter(tags=["leads"])


def get_lead_service(db: Session = Depends(get_db)) -> LeadService:
    return LeadService(db)


@router.get("/leads/me", response_model=schemas.LeadInquiryResponse | None, tags=["my-inquiry"])
def get_my_lead(service: LeadService = Depends(get_lead_service), user: str = Depends(get_current_user)):
    return service.get_my_lead(user)


@router.post("/leads", response_model=schemas.LeadInquiryResponse, status_code=201, tags=["my-inquiry"])
def submit_lead_form(
    lead: schemas.LeadInquiryCreate,
    background_tasks: BackgroundTasks,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    return service.submit_lead(lead, user, background_tasks)


@router.put("/leads/me", response_model=schemas.LeadInquiryResponse, tags=["my-inquiry"])
def update_my_lead(
    updates: schemas.LeadInquiryUpdate,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    return service.update_my_lead(user, updates)


@router.get("/leads", response_model=list[schemas.LeadInquiryResponse], tags=["internal"])
def get_all_leads(
    skip: int = 0,
    limit: int = 100,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    return service.list_leads(skip=skip, limit=limit)


@router.get("/leads/pending-export", response_model=list[schemas.LeadInquiryResponse], tags=["internal"])
def get_pending_export(service: LeadService = Depends(get_lead_service), user: str = Depends(get_current_user)):
    return service.get_pending_export()


@router.post("/leads/mark-exported", tags=["internal"])
def mark_exported(
    payload: schemas.MarkExportedRequest,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    updated_count = service.mark_exported(payload.lead_ids)
    return {"updated": updated_count}


@router.get("/leads/{lead_id}", response_model=schemas.LeadInquiryResponse, tags=["internal"])
def get_single_lead(
    lead_id: uuid.UUID,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    return service.get_lead_by_id(lead_id)


@router.patch("/leads/{lead_id}/status", response_model=schemas.LeadInquiryResponse, tags=["internal"])
def update_lead_status(
    lead_id: uuid.UUID,
    update: schemas.LeadStatusUpdate,
    service: LeadService = Depends(get_lead_service),
    user: str = Depends(get_current_user),
):
    return service.update_status(lead_id, update.status)