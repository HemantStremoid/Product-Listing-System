from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Mapping, MarketplaceTemplate, SellerFile
from app.schemas import MappingCreate, MappingResponse, TransformedDataResponse
from app.services.transformation import DataTransformer
from app.services.validation import DataValidator

router = APIRouter(prefix="/api/mapping", tags=["mapping"])


@router.post("/", response_model=MappingResponse)
async def create_mapping(mapping_data: MappingCreate, db: Session = Depends(get_db)):
    """Create a new column mapping"""

    # Validate marketplace template exists
    marketplace_template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.id == mapping_data.marketplace_template_id)
        .first()
    )

    if not marketplace_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace template not found",
        )

    # Validate seller file exists
    seller_file = (
        db.query(SellerFile)
        .filter(SellerFile.id == mapping_data.seller_file_id)
        .first()
    )

    if not seller_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller file not found"
        )

    # Transform data
    transformed_data = DataTransformer.transform_data(
        seller_file.file_path,
        seller_file.file_type,
        [mapping.dict() for mapping in mapping_data.column_mapping],
    )

    # Validate transformed data
    validation_result = DataValidator.validate_data(
        transformed_data,
        marketplace_template.template,
        [mapping.dict() for mapping in mapping_data.column_mapping],
    )

    # Create mapping record
    db_mapping = Mapping(
        name=mapping_data.name,
        marketplace_template_id=mapping_data.marketplace_template_id,
        seller_file_id=mapping_data.seller_file_id,
        column_mapping=[mapping.dict() for mapping in mapping_data.column_mapping],
        validation_results=validation_result.dict(),
        transformed_data=transformed_data,
        is_valid=validation_result.is_valid,
    )

    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)

    return db_mapping


@router.get("/", response_model=List[MappingResponse])
async def get_mappings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all mappings"""

    mappings = db.query(Mapping).offset(skip).limit(limit).all()
    return mappings


@router.get("/{mapping_id}", response_model=MappingResponse)
async def get_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Get a specific mapping by ID"""

    mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found"
        )

    return mapping


@router.get("/{mapping_id}/transformed-data", response_model=TransformedDataResponse)
async def get_transformed_data(mapping_id: int, db: Session = Depends(get_db)):
    """Get transformed data for a mapping"""

    mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found"
        )

    transformed_data = mapping.transformed_data or []
    validation_result = mapping.validation_results or {}

    # Calculate statistics
    total_rows = len(transformed_data)
    valid_rows = total_rows - len(validation_result.get("errors", []))
    invalid_rows = len(validation_result.get("errors", []))

    return TransformedDataResponse(
        mapping_id=mapping_id,
        data=transformed_data,
        validation_result=validation_result,
        total_rows=total_rows,
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
    )


@router.put("/{mapping_id}", response_model=MappingResponse)
async def update_mapping(
    mapping_id: int, mapping_data: MappingCreate, db: Session = Depends(get_db)
):
    """Update a mapping"""

    mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found"
        )

    # Validate marketplace template exists
    marketplace_template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.id == mapping_data.marketplace_template_id)
        .first()
    )

    if not marketplace_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace template not found",
        )

    # Validate seller file exists
    seller_file = (
        db.query(SellerFile)
        .filter(SellerFile.id == mapping_data.seller_file_id)
        .first()
    )

    if not seller_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller file not found"
        )

    # Transform data
    transformed_data = DataTransformer.transform_data(
        seller_file.file_path,
        seller_file.file_type,
        [mapping.dict() for mapping in mapping_data.column_mapping],
    )

    # Validate transformed data
    validation_result = DataValidator.validate_data(
        transformed_data,
        marketplace_template.template,
        [mapping.dict() for mapping in mapping_data.column_mapping],
    )

    # Update mapping
    mapping.name = mapping_data.name
    mapping.marketplace_template_id = mapping_data.marketplace_template_id
    mapping.seller_file_id = mapping_data.seller_file_id
    mapping.column_mapping = [mapping.dict() for mapping in mapping_data.column_mapping]
    mapping.validation_results = validation_result.dict()
    mapping.transformed_data = transformed_data
    mapping.is_valid = validation_result.is_valid

    db.commit()
    db.refresh(mapping)

    return mapping


@router.delete("/{mapping_id}")
async def delete_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Delete a mapping"""

    mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found"
        )

    db.delete(mapping)
    db.commit()

    return {"message": "Mapping deleted successfully"}

