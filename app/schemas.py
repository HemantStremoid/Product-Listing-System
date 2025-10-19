from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
    BOYS = "Boys"
    GIRLS = "Girls"
    UNISEX = "Unisex"


class CategoryEnum(str, Enum):
    TSHIRTS = "T-Shirts"
    JEANS = "Jeans"
    DRESSES = "Dresses"
    SAREES = "Sarees"
    SHOES = "Shoes"
    BAGS = "Bags"
    ACCESSORIES = "Accessories"


class AttributeType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    ENUM = "enum"


class AttributeDefinition(BaseModel):
    name: str
    type: AttributeType
    required: bool = False
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    enum_values: Optional[List[str]] = None
    description: Optional[str] = None


class MarketplaceTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template: Dict[str, AttributeDefinition]


class MarketplaceTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SellerFileUpload(BaseModel):
    filename: str
    file_type: str
    columns: List[str]
    sample_rows: List[Dict[str, Any]]
    row_count: int


class SellerFileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    columns: List[str]
    sample_rows: List[Dict[str, Any]]
    row_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ColumnMapping(BaseModel):
    seller_column: str
    marketplace_attribute: str
    transformation: Optional[str] = None  # For data transformation rules


class MappingCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    marketplace_template_id: int
    seller_file_id: int
    column_mapping: List[ColumnMapping]


class MappingResponse(BaseModel):
    id: int
    name: str
    marketplace_template_id: int
    seller_file_id: int
    column_mapping: List[Dict[str, Any]]
    validation_results: Optional[Dict[str, Any]]
    transformed_data: Optional[List[Dict[str, Any]]]
    is_valid: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ValidationError(BaseModel):
    field: str
    message: str
    row: Optional[int] = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str] = []


class TransformedDataResponse(BaseModel):
    mapping_id: int
    data: List[Dict[str, Any]]
    validation_result: ValidationResult
    total_rows: int
    valid_rows: int
    invalid_rows: int
