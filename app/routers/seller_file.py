from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
from app.database import get_db
from app.models import SellerFile
from app.schemas import SellerFileResponse
from app.services.file_parser import FileParser
from fastapi.concurrency import run_in_threadpool
from types import SimpleNamespace
import io

router = APIRouter(prefix="/api/seller-file", tags=["seller-file"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=SellerFileResponse)
async def upload_seller_file(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload and parse a seller file (CSV/Excel)"""

    # Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["csv", "xlsx", "xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and Excel files are supported",
        )

    try:
        # Read uploaded file bytes in the async context to avoid passing
        # coroutine objects into threadpool worker where they can't be
        # awaited. Then wrap bytes in a simple sync object for parsing.
        content = await file.read()

        sync_file = SimpleNamespace(
            filename=file.filename,
            read=lambda content=content: content,
            file=io.BytesIO(content),
        )

        # Parse the file using a threadpool to avoid blocking the event loop
        columns, sample_rows, row_count = await run_in_threadpool(
            FileParser.parse_file, sync_file
        )

        # Save file to disk (write bytes directly)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Save to database
        db_file = SellerFile(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension,
            columns=columns,
            sample_rows=sample_rows,
            row_count=row_count,
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return db_file

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}",
        )


@router.get("/files", response_model=List[SellerFileResponse])
async def get_seller_files(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all uploaded seller files"""

    files = db.query(SellerFile).offset(skip).limit(limit).all()
    return files


@router.get("/files/{file_id}", response_model=SellerFileResponse)
async def get_seller_file(file_id: int, db: Session = Depends(get_db)):
    """Get a specific seller file by ID"""

    file = db.query(SellerFile).filter(SellerFile.id == file_id).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return file


@router.delete("/files/{file_id}")
async def delete_seller_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a seller file"""

    file = db.query(SellerFile).filter(SellerFile.id == file_id).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    # Check if file is being used in any mappings
    if file.mappings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete file that is being used in mappings",
        )

    # Delete physical file
    if os.path.exists(file.file_path):
        os.remove(file.file_path)

    # Delete from database
    db.delete(file)
    db.commit()

    return {"message": "File deleted successfully"}
