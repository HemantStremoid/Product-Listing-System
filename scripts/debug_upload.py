from fastapi.testclient import TestClient
import tempfile
import os
from unittest.mock import Mock

# Setup test DB similar to tests/test_api.setup_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.main import app as _app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database import get_db as _get_db


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


app = _app
app.dependency_overrides[_get_db] = override_get_db
client = TestClient(app)

# Create a temp CSV similar to the test
csv_content = "SKU,Name,Price\nSKU001,Test Product,100"
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
    temp_file.write(csv_content)
    temp_file_path = temp_file.name

with open(temp_file_path, "rb") as f:
    response = client.post(
        "/api/seller-file/upload", files={"file": ("test.csv", f, "text/csv")}
    )

print("STATUS:", response.status_code)
try:
    print("JSON:", response.json())
except Exception:
    print("TEXT:", response.text)

# Cleanup
if os.path.exists(temp_file_path):
    os.unlink(temp_file_path)

# Drop tables
Base.metadata.drop_all(bind=engine)
if os.path.exists("test.db"):
    os.unlink("test.db")
