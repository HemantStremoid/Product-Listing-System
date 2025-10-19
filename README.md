# Product Listing System

A comprehensive backend system for managing marketplace templates, seller product files, and data mapping for e-commerce platforms.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Design](#system-design)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Setup Instructions](#setup-instructions)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)

## Overview

The Product Listing System is a FastAPI-based backend service that enables:

1. **Marketplace Template Management**: Define and manage templates for different marketplaces (Myntra, Flipkart, etc.)
2. **Seller File Processing**: Upload and parse CSV/Excel files containing product catalogs
3. **Data Mapping**: Map seller file columns to marketplace attributes
4. **Data Validation**: Validate transformed data against marketplace requirements
5. **Data Transformation**: Convert seller data to marketplace-specific formats

## Features

- ✅ **Marketplace Template Management**: Create, read, update, delete marketplace templates
- ✅ **File Upload & Parsing**: Support for CSV and Excel files with automatic column detection
- ✅ **Column Mapping**: Map seller columns to marketplace attributes with transformation rules
- ✅ **Data Validation**: Comprehensive validation including business rules (price ≤ MRP)
- ✅ **Data Transformation**: Convert data formats and apply transformation rules
- ✅ **RESTful APIs**: Complete CRUD operations for all entities
- ✅ **Swagger Documentation**: Interactive API documentation
- ✅ **Docker Support**: Containerized deployment
- ✅ **Unit Tests**: Comprehensive test coverage
- ✅ **Database Support**: SQLite (default) and PostgreSQL

## System Design

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Marketplace   │    │   Seller File   │    │     Mapping     │
│   Templates     │    │   Processing    │    │   & Validation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Transformed    │
                    │     Data        │
                    └─────────────────┘
```

### Data Flow

1. **Template Creation**: Define marketplace requirements
2. **File Upload**: Upload seller product catalog
3. **Column Mapping**: Map seller columns to marketplace attributes
4. **Data Transformation**: Apply transformation rules
5. **Validation**: Validate against marketplace requirements
6. **Output**: Generate marketplace-ready data

## Database Schema

### Tables

#### `marketplace_templates`
- `id`: Primary key
- `name`: Template name (unique)
- `description`: Template description
- `template`: JSON schema defining attributes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### `seller_files`
- `id`: Primary key
- `filename`: Stored filename
- `original_filename`: Original filename
- `file_path`: File storage path
- `file_type`: File type (csv, xlsx, xls)
- `columns`: Discovered columns (JSON)
- `sample_rows`: Sample data (JSON)
- `row_count`: Total row count
- `created_at`: Upload timestamp

#### `mappings`
- `id`: Primary key
- `name`: Mapping name
- `marketplace_template_id`: Foreign key to marketplace_templates
- `seller_file_id`: Foreign key to seller_files
- `column_mapping`: Column mapping configuration (JSON)
- `validation_results`: Validation results (JSON)
- `transformed_data`: Transformed data (JSON)
- `is_valid`: Validation status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Marketplace Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/marketplace/templates` | Create marketplace template |
| GET | `/api/marketplace/templates` | List all templates |
| GET | `/api/marketplace/templates/{id}` | Get specific template |
| PUT | `/api/marketplace/templates/{id}` | Update template |
| DELETE | `/api/marketplace/templates/{id}` | Delete template |

#### Seller Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/seller-file/upload` | Upload seller file |
| GET | `/api/seller-file/files` | List uploaded files |
| GET | `/api/seller-file/files/{id}` | Get specific file |
| DELETE | `/api/seller-file/files/{id}` | Delete file |

#### Mappings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mapping/` | Create mapping |
| GET | `/api/mapping/` | List all mappings |
| GET | `/api/mapping/{id}` | Get specific mapping |
| PUT | `/api/mapping/{id}` | Update mapping |
| DELETE | `/api/mapping/{id}` | Delete mapping |
| GET | `/api/mapping/{id}/transformed-data` | Get transformed data |

### Request/Response Examples

#### Create Marketplace Template

**Request:**
```json
POST /api/marketplace/templates
{
  "name": "Myntra Template",
  "description": "Template for Myntra marketplace",
  "template": {
    "productName": {
      "name": "productName",
      "type": "string",
      "required": true,
      "max_length": 150
    },
    "price": {
      "name": "price",
      "type": "number",
      "required": true,
      "min_value": 0
    },
    "gender": {
      "name": "gender",
      "type": "enum",
      "required": true,
      "enum_values": ["Men", "Women", "Boys", "Girls", "Unisex"]
    }
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Myntra Template",
  "description": "Template for Myntra marketplace",
  "template": { ... },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

#### Upload Seller File

**Request:**
```
POST /api/seller-file/upload
Content-Type: multipart/form-data

file: [CSV/Excel file]
```

**Response:**
```json
{
  "id": 1,
  "filename": "20240101_120000_products.csv",
  "original_filename": "products.csv",
  "file_type": "csv",
  "columns": ["SKU", "Name", "BrandName", "Price", "MRP"],
  "sample_rows": [
    {
      "SKU": "SKU001",
      "Name": "Test Product",
      "BrandName": "Brand A",
      "Price": 100,
      "MRP": 150
    }
  ],
  "row_count": 100,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Create Mapping

**Request:**
```json
POST /api/mapping/
{
  "name": "Myntra Mapping",
  "marketplace_template_id": 1,
  "seller_file_id": 1,
  "column_mapping": [
    {
      "seller_column": "Name",
      "marketplace_attribute": "productName"
    },
    {
      "seller_column": "Price",
      "marketplace_attribute": "price"
    },
    {
      "seller_column": "Gender",
      "marketplace_attribute": "gender"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Myntra Mapping",
  "marketplace_template_id": 1,
  "seller_file_id": 1,
  "column_mapping": [ ... ],
  "validation_results": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "transformed_data": [ ... ],
  "is_valid": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd product-listing-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize database**
   ```bash
   # Database tables are created automatically on first run
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Production Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/product_listing"
   export SECRET_KEY="your-secret-key"
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone and navigate to project**
   ```bash
   git clone <repository-url>
   cd product-listing-system
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t product-listing-system .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads product-listing-system
   ```

### Docker Compose Services

- **app**: Main application service
- **db**: PostgreSQL database (optional, can use SQLite)

## Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite covers:
- ✅ File parsing (CSV/Excel)
- ✅ Data validation
- ✅ Data transformation
- ✅ API endpoints
- ✅ Database operations
- ✅ Error handling

### Test Structure

```
tests/
├── __init__.py
├── test_api.py          # API endpoint tests
├── test_file_parser.py # File parsing tests
├── test_validation.py  # Validation logic tests
└── test_transformation.py # Data transformation tests
```

## Usage Examples

### Example 1: Complete Workflow

1. **Create Myntra Template**
   ```bash
   curl -X POST "http://localhost:8000/api/marketplace/templates" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Myntra Template",
          "description": "Template for Myntra marketplace",
          "template": {
            "productName": {
              "name": "productName",
              "type": "string",
              "required": true,
              "max_length": 150
            },
            "price": {
              "name": "price",
              "type": "number",
              "required": true,
              "min_value": 0
            },
            "gender": {
              "name": "gender",
              "type": "enum",
              "required": true,
              "enum_values": ["Men", "Women", "Boys", "Girls", "Unisex"]
            }
          }
        }'
   ```

2. **Upload Seller File**
   ```bash
   curl -X POST "http://localhost:8000/api/seller-file/upload" \
        -F "file=@products.csv"
   ```

3. **Create Mapping**
   ```bash
   curl -X POST "http://localhost:8000/api/mapping/" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Myntra Mapping",
          "marketplace_template_id": 1,
          "seller_file_id": 1,
          "column_mapping": [
            {"seller_column": "Name", "marketplace_attribute": "productName"},
            {"seller_column": "Price", "marketplace_attribute": "price"},
            {"seller_column": "Gender", "marketplace_attribute": "gender"}
          ]
        }'
   ```

4. **Get Transformed Data**
   ```bash
   curl -X GET "http://localhost:8000/api/mapping/1/transformed-data"
   ```

### Example 2: Sample Data Files

#### Sample CSV (products.csv)
```csv
SKU,Name,BrandName,Gender,Category,Color,Size,MRP,Price,Material,Image1,Image2,Quantity,Description
SKU001,Classic T-Shirt,Brand A,Men,T-Shirts,Blue,M,500,400,Cotton,https://example.com/img1.jpg,https://example.com/img2.jpg,10,Comfortable cotton t-shirt
SKU002,Denim Jeans,Brand B,Women,Jeans,Blue,32,1200,1000,Denim,https://example.com/jeans1.jpg,https://example.com/jeans2.jpg,5,Stylish denim jeans
```

#### Sample Myntra Template
```json
{
  "productName": {
    "name": "productName",
    "type": "string",
    "required": true,
    "max_length": 150
  },
  "brand": {
    "name": "brand",
    "type": "string",
    "required": true
  },
  "gender": {
    "name": "gender",
    "type": "enum",
    "required": true,
    "enum_values": ["Men", "Women", "Boys", "Girls", "Unisex"]
  },
  "category": {
    "name": "category",
    "type": "enum",
    "required": true,
    "enum_values": ["T-Shirts", "Jeans", "Dresses", "Sarees", "Shoes", "Bags", "Accessories"]
  },
  "color": {
    "name": "color",
    "type": "string",
    "required": true
  },
  "size": {
    "name": "size",
    "type": "string",
    "required": true
  },
  "mrp": {
    "name": "mrp",
    "type": "number",
    "required": true,
    "min_value": 0
  },
  "price": {
    "name": "price",
    "type": "number",
    "required": true,
    "min_value": 0
  },
  "sku": {
    "name": "sku",
    "type": "string",
    "required": true
  },
  "images": {
    "name": "images",
    "type": "array",
    "required": true
  },
  "description": {
    "name": "description",
    "type": "string",
    "required": false
  },
  "material": {
    "name": "material",
    "type": "string",
    "required": false
  }
}
```

## Architecture

### Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite (default) / PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **File Processing**: Pandas
- **Testing**: Pytest
- **Containerization**: Docker

### Key Design Patterns

1. **Repository Pattern**: Database operations abstracted through models
2. **Service Layer**: Business logic separated from API endpoints
3. **Dependency Injection**: FastAPI's built-in DI system
4. **Data Transfer Objects**: Pydantic models for request/response validation

### Scalability Considerations

- **Database**: Can be easily switched from SQLite to PostgreSQL
- **File Storage**: Can be extended to use cloud storage (S3, GCS)
- **Caching**: Redis can be added for frequently accessed data
- **Load Balancing**: Stateless design supports horizontal scaling
- **Background Tasks**: Celery can be added for heavy processing

### Security Features

- **Input Validation**: Comprehensive validation using Pydantic
- **File Type Validation**: Only CSV/Excel files allowed
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Support**: Configurable CORS for frontend integration

### Monitoring and Logging

- **Health Check**: `/health` endpoint for monitoring
- **Structured Logging**: Can be extended with proper logging framework
- **Error Handling**: Comprehensive error responses
- **Metrics**: Can be extended with Prometheus metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test cases for usage examples

