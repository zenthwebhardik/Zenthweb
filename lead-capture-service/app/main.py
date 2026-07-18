from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.config import settings
from app.routers import lead_router, auth_router

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


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed — check the fields you sent",
            "errors": exc.errors(),
            "data": None,
        },
    )


@app.get("/", tags=["health"])
def root():
    return {"service": settings.APP_NAME, "status": "running", "env": settings.ENV}


@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok", "database": "connected"}


app.include_router(auth_router.router)
app.include_router(lead_router.router)