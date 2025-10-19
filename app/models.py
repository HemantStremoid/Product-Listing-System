from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MarketplaceTemplate(Base):
    __tablename__ = "marketplace_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    template = Column(JSON)  # Store the template schema as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to mappings
    mappings = relationship("Mapping", back_populates="marketplace_template")


class SellerFile(Base):
    __tablename__ = "seller_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(10))  # csv, xlsx
    columns = Column(JSON)  # Store discovered columns
    sample_rows = Column(JSON)  # Store sample data
    row_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to mappings
    mappings = relationship("Mapping", back_populates="seller_file")


class Mapping(Base):
    __tablename__ = "mappings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    marketplace_template_id = Column(Integer, ForeignKey("marketplace_templates.id"))
    seller_file_id = Column(Integer, ForeignKey("seller_files.id"))
    column_mapping = Column(JSON)  # Store the mapping configuration
    validation_results = Column(JSON)  # Store validation results
    transformed_data = Column(JSON)  # Store the transformed data
    is_valid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    marketplace_template = relationship(
        "MarketplaceTemplate", back_populates="mappings"
    )
    seller_file = relationship("SellerFile", back_populates="mappings")

