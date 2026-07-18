import uuid

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import engine, get_db, Base
from app.config import settings
from app.auth import build_google_login_url, exchange_code_for_user, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Captures client website inquiries — one entry per person, editable, not duplicable.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zenthweb.dev", "https://www.zenthweb.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Global exception handlers (consistent error shape for frontend) ----------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Har HTTPException (403, 404, 409, 401, etc.) yahan se guzregi —
    frontend ko hamesha same shape milega: success, message, data."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Jab request body me galat field/type/enum aaye (422 errors) —
    field-by-field detail frontend ko milta hai 'errors' array me."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed — check the fields you sent",
            "errors": exc.errors(),
            "data": None,
        },
    )


# ---------- Health ----------

@app.get("/", tags=["health"])
def root():
    return {"service": settings.APP_NAME, "status": "running", "env": settings.ENV}


@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok", "database": "connected"}


# ---------- Auth ----------

@app.get("/auth/google/login", tags=["auth"])
def google_login():
    return RedirectResponse(build_google_login_url())


@app.get("/auth/google/callback", tags=["auth"])
def google_callback(code: str):
    user_info = exchange_code_for_user(code)
    token = create_access_token(user_info["email"])
    return {"access_token": token, "token_type": "bearer", "email": user_info["email"]}


# ---------- User-facing: their own single entry ----------

@app.get("/leads/me", response_model=schemas.LeadInquiryResponse | None, tags=["my-inquiry"])
def get_my_lead(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """Frontend calls this right after login. None = naya user, khaali form dikhao.
    Value mila = purana user, form pre-filled dikhao, edit karne do."""
    return crud.get_lead_by_email(db, user)


@app.post("/leads", response_model=schemas.LeadInquiryResponse, status_code=status.HTTP_201_CREATED, tags=["my-inquiry"])
def submit_lead_form(lead: schemas.LeadInquiryCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """Sirf pehli baar chalega. Agar iss email ki entry pehle se hai, 409 milega —
    frontend ko chahiye ki PUT /leads/me use kare uss case mein."""
    if lead.email != user:
        raise HTTPException(status_code=403, detail="You can only submit an inquiry for your own logged-in email")

    try:
        return crud.create_lead(db, lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an inquiry on file. Use the update endpoint to edit it.",
        )


@app.put("/leads/me", response_model=schemas.LeadInquiryResponse, tags=["my-inquiry"])
def update_my_lead(updates: schemas.LeadInquiryUpdate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """Purana user apni entry edit karega yahan se."""
    updated = crud.update_own_lead(db, user, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="No existing inquiry found — submit one first via POST /leads")
    return updated


# ---------- Internal / sales team endpoints ----------

@app.get("/leads", response_model=list[schemas.LeadInquiryResponse], tags=["internal"])
def get_all_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.list_leads(db, skip=skip, limit=limit)


@app.get("/leads/pending-export", response_model=list[schemas.LeadInquiryResponse], tags=["internal"])
def get_pending_export(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.get_pending_export_leads(db)


@app.post("/leads/mark-exported", tags=["internal"])
def mark_exported(payload: schemas.MarkExportedRequest, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    crud.mark_leads_exported(db, payload.lead_ids)
    return {"updated": len(payload.lead_ids)}


@app.get("/leads/{lead_id}", response_model=schemas.LeadInquiryResponse, tags=["internal"])
def get_single_lead(lead_id: uuid.UUID, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.patch("/leads/{lead_id}/status", response_model=schemas.LeadInquiryResponse, tags=["internal"])
def update_lead_status(lead_id: uuid.UUID, update: schemas.LeadStatusUpdate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    updated = crud.update_status(db, lead_id, update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated