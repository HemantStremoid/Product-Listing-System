from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import MarketplaceTemplate
from app.schemas import MarketplaceTemplateCreate, MarketplaceTemplateResponse

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


@router.post("/templates", response_model=MarketplaceTemplateResponse)
async def create_marketplace_template(
    template_data: MarketplaceTemplateCreate, db: Session = Depends(get_db)
):
    """Create a new marketplace template"""

    # Check if template with same name already exists
    existing_template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.name == template_data.name)
        .first()
    )

    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists",
        )

    # Create new template
    # `template_data.template` is declared as a Dict in the schema so it may
    # already be a plain dict (coming from JSON). If it's a pydantic model
    # instance, call .dict(), otherwise use it directly.
    # Normalize template: ensure nested AttributeDefinition Pydantic objects
    # are converted into plain dicts so they can be JSON-serialized by SQLAlchemy.
    raw_template = (
        template_data.template.dict()
        if hasattr(template_data.template, "dict")
        else template_data.template
    )

    template_value = {}
    for key, val in raw_template.items():
        # If val is a pydantic model-like object, convert to dict
        template_value[key] = val.dict() if hasattr(val, "dict") else val

    db_template = MarketplaceTemplate(
        name=template_data.name,
        description=template_data.description,
        template=template_value,
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.get("/templates", response_model=List[MarketplaceTemplateResponse])
async def get_marketplace_templates(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all marketplace templates"""

    templates = db.query(MarketplaceTemplate).offset(skip).limit(limit).all()
    return templates


@router.get("/templates/{template_id}", response_model=MarketplaceTemplateResponse)
async def get_marketplace_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific marketplace template by ID"""

    template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return template


@router.put("/templates/{template_id}", response_model=MarketplaceTemplateResponse)
async def update_marketplace_template(
    template_id: int,
    template_data: MarketplaceTemplateCreate,
    db: Session = Depends(get_db),
):
    """Update a marketplace template"""

    template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if name is being changed and if new name already exists
    if template.name != template_data.name:
        existing_template = (
            db.query(MarketplaceTemplate)
            .filter(
                MarketplaceTemplate.name == template_data.name,
                MarketplaceTemplate.id != template_id,
            )
            .first()
        )

        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this name already exists",
            )

    # Update template
    template.name = template_data.name
    template.description = template_data.description
    # Normalize update payload as well
    raw_update = (
        template_data.template.dict()
        if hasattr(template_data.template, "dict")
        else template_data.template
    )
    updated_template = {}
    for key, val in raw_update.items():
        updated_template[key] = val.dict() if hasattr(val, "dict") else val

    template.template = updated_template

    db.commit()
    db.refresh(template)

    return template


@router.delete("/templates/{template_id}")
async def delete_marketplace_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a marketplace template"""

    template = (
        db.query(MarketplaceTemplate)
        .filter(MarketplaceTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if template is being used in any mappings
    if template.mappings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete template that is being used in mappings",
        )

    db.delete(template)
    db.commit()

    return {"message": "Template deleted successfully"}
