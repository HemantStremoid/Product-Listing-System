from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.database import engine
from app.models import Base
from app.routers import marketplace, seller_file, mapping


# Create database tables on startup. Doing this at import time can crash the
# process in container environments if the DB file or directory is not
# available or writable (causes sqlite OperationalError). Perform the
# create_all in a startup handler and catch OperationalError so the app can
# start and expose logs to help diagnose environment/volume issues.
def create_tables_on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        # Log a helpful message; avoid importing logging to keep this small.
        print(
            "WARNING: could not create database tables on startup:",
            str(exc),
        )


app = FastAPI(
    title="Product Listing System API",
    description="A backend system for managing marketplace templates, seller files, and data mapping",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(marketplace.router)
app.include_router(seller_file.router)
app.include_router(mapping.router)


@app.on_event("startup")
async def startup_event():
    # Attempt to create tables on startup (non-blocking). This will print a
    # warning if the database file isn't writable or available; the app will
    # still start so operators can inspect logs and fix volumes/env.
    create_tables_on_startup()


@app.get("/")
async def root():
    return {"message": "Product Listing System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
