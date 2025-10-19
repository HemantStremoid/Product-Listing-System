from fastapi.testclient import TestClient
from app.models import Base
import tempfile
import os

# Defer SQLAlchemy imports and engine creation to setup_module to avoid import-time
# errors on Python versions where typing internals differ (e.g., Python 3.13)
engine = None
TestingSessionLocal = None
_orig_get_db = None


def setup_module(module):
    """Create test engine, session factory and override app dependency."""
    global engine, TestingSessionLocal, app, client, _orig_get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # import get_db here to avoid importing app.database at module import time
    # (which would import SQLAlchemy immediately and can fail under some
    # Python versions). Save a reference so teardown can remove the override.
    from app.database import get_db as _get_db

    # _orig_get_db is declared global above; assign to it below
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    _orig_get_db = _get_db

    # Create test database tables
    Base.metadata.create_all(bind=engine)

    # Import the app AFTER the test DB is prepared so that app import
    # (and any SQLAlchemy imports) occur after tests have configured the
    # test engine.
    from app.main import app as _app

    app = _app

    # Now that `app` is available, set the dependency override and create
    # the TestClient.
    app.dependency_overrides[_orig_get_db] = override_get_db

    client = TestClient(app)


def teardown_module(module):
    """Drop test tables and remove test DB file."""
    global engine
    try:
        if engine is not None:
            Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    try:
        if os.path.exists("test.db"):
            os.unlink("test.db")
    except Exception:
        pass
    try:
        if "client" in globals() and client is not None:
            client.close()
    except Exception:
        pass
    # Remove dependency override
    try:
        if _orig_get_db is not None:
            app.dependency_overrides.pop(_orig_get_db, None)
    except Exception:
        pass


class TestAPI:

    def setup_method(self):
        """Setup test database"""
        # Clear existing data
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Product Listing System API"

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_create_marketplace_template(self):
        """Test creating marketplace template"""
        template_data = {
            "name": "Myntra Template",
            "description": "Template for Myntra marketplace",
            "template": {
                "productName": {
                    "name": "productName",
                    "type": "string",
                    "required": True,
                    "max_length": 150,
                },
                "price": {
                    "name": "price",
                    "type": "number",
                    "required": True,
                    "min_value": 0,
                },
            },
        }

        response = client.post("/api/marketplace/templates", json=template_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Myntra Template"
        assert data["template"]["productName"]["required"]

    def test_get_marketplace_templates(self):
        """Test getting marketplace templates"""
        # First create a template
        template_data = {
            "name": "Test Template",
            "description": "Test template",
            "template": {
                "productName": {
                    "name": "productName",
                    "type": "string",
                    "required": True,
                }
            },
        }

        client.post("/api/marketplace/templates", json=template_data)

        # Then get all templates
        response = client.get("/api/marketplace/templates")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Template"

    def test_upload_seller_file(self):
        """Test uploading seller file"""
        # Create a test CSV file
        csv_content = "SKU,Name,Price\nSKU001,Test Product,100"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/api/seller-file/upload",
                    files={"file": ("test.csv", f, "text/csv")},
                )

            assert response.status_code == 200

            data = response.json()
            assert data["original_filename"] == "test.csv"
            assert "SKU" in data["columns"]
            assert "Name" in data["columns"]
            assert "Price" in data["columns"]
            assert data["row_count"] == 1

        finally:
            os.unlink(temp_file_path)

    def test_create_mapping(self):
        """Test creating a mapping"""
        # First create marketplace template
        template_data = {
            "name": "Test Template",
            "description": "Test template",
            "template": {
                "productName": {
                    "name": "productName",
                    "type": "string",
                    "required": True,
                },
                "price": {"name": "price", "type": "number", "required": True},
            },
        }

        template_response = client.post(
            "/api/marketplace/templates", json=template_data
        )
        template_id = template_response.json()["id"]

        # Create seller file
        csv_content = "SKU,Name,Price\nSKU001,Test Product,100"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                file_response = client.post(
                    "/api/seller-file/upload",
                    files={"file": ("test.csv", f, "text/csv")},
                )

            file_id = file_response.json()["id"]

            # Create mapping
            mapping_data = {
                "name": "Test Mapping",
                "marketplace_template_id": template_id,
                "seller_file_id": file_id,
                "column_mapping": [
                    {"seller_column": "Name", "marketplace_attribute": "productName"},
                    {"seller_column": "Price", "marketplace_attribute": "price"},
                ],
            }

            response = client.post("/api/mapping/", json=mapping_data)
            assert response.status_code == 200

            data = response.json()
            assert data["name"] == "Test Mapping"
            assert data["is_valid"]

        finally:
            os.unlink(temp_file_path)

    def test_get_transformed_data(self):
        """Test getting transformed data"""
        # Create template, file, and mapping first
        template_data = {
            "name": "Test Template",
            "description": "Test template",
            "template": {
                "productName": {
                    "name": "productName",
                    "type": "string",
                    "required": True,
                },
                "price": {"name": "price", "type": "number", "required": True},
            },
        }

        template_response = client.post(
            "/api/marketplace/templates", json=template_data
        )
        template_id = template_response.json()["id"]

        csv_content = "SKU,Name,Price\nSKU001,Test Product,100"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                file_response = client.post(
                    "/api/seller-file/upload",
                    files={"file": ("test.csv", f, "text/csv")},
                )

            file_id = file_response.json()["id"]

            mapping_data = {
                "name": "Test Mapping",
                "marketplace_template_id": template_id,
                "seller_file_id": file_id,
                "column_mapping": [
                    {"seller_column": "Name", "marketplace_attribute": "productName"},
                    {"seller_column": "Price", "marketplace_attribute": "price"},
                ],
            }

            mapping_response = client.post("/api/mapping/", json=mapping_data)
            mapping_id = mapping_response.json()["id"]

            # Get transformed data
            response = client.get(f"/api/mapping/{mapping_id}/transformed-data")
            assert response.status_code == 200

            data = response.json()
            assert data["mapping_id"] == mapping_id
            assert data["total_rows"] == 1
            assert data["valid_rows"] == 1
            assert data["invalid_rows"] == 0
            assert len(data["data"]) == 1
            assert data["data"][0]["productName"] == "Test Product"
            assert data["data"][0]["price"] == 100

        finally:
            os.unlink(temp_file_path)
