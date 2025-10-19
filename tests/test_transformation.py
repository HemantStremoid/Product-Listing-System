import pytest
import pandas as pd
import tempfile
import os
from app.services.transformation import DataTransformer


class TestDataTransformer:

    def test_transform_basic_data(self):
        """Test basic data transformation"""
        # Create temporary CSV file
        csv_content = (
            "SKU,Name,BrandName,Price,MRP\nSKU001,Test Product,Brand A,100,150"
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            column_mapping = [
                {"seller_column": "SKU", "marketplace_attribute": "sku"},
                {"seller_column": "Name", "marketplace_attribute": "productName"},
                {"seller_column": "BrandName", "marketplace_attribute": "brand"},
                {"seller_column": "Price", "marketplace_attribute": "price"},
                {"seller_column": "MRP", "marketplace_attribute": "mrp"},
            ]

            result = DataTransformer.transform_data(
                temp_file_path, "csv", column_mapping
            )

            assert len(result) == 1
            assert result[0]["sku"] == "SKU001"
            assert result[0]["productName"] == "Test Product"
            assert result[0]["brand"] == "Brand A"
            assert result[0]["price"] == 100
            assert result[0]["mrp"] == 150

        finally:
            os.unlink(temp_file_path)

    def test_transform_with_transformations(self):
        """Test data transformation with transformation rules"""
        csv_content = "Name,Price\nTest Product,100"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            column_mapping = [
                {
                    "seller_column": "Name",
                    "marketplace_attribute": "productName",
                    "transformation": "uppercase",
                },
                {"seller_column": "Price", "marketplace_attribute": "price"},
            ]

            result = DataTransformer.transform_data(
                temp_file_path, "csv", column_mapping
            )

            assert result[0]["productName"] == "TEST PRODUCT"
            assert result[0]["price"] == 100

        finally:
            os.unlink(temp_file_path)

    def test_transform_images_to_array(self):
        """Test transformation of image fields to arrays"""
        csv_content = (
            "Image1,Image2\nhttps://example.com/img1.jpg,https://example.com/img2.jpg"
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            column_mapping = [
                {"seller_column": "Image1", "marketplace_attribute": "images"}
            ]

            result = DataTransformer.transform_data(
                temp_file_path, "csv", column_mapping
            )

            assert result[0]["images"] == ["https://example.com/img1.jpg"]

        finally:
            os.unlink(temp_file_path)

    def test_transform_bullet_points(self):
        """Test transformation of bullet points"""
        csv_content = "BulletPoints\nPoint 1|Point 2|Point 3|Point 4|Point 5|Point 6"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            column_mapping = [
                {
                    "seller_column": "BulletPoints",
                    "marketplace_attribute": "bulletPoints",
                }
            ]

            result = DataTransformer.transform_data(
                temp_file_path, "csv", column_mapping
            )

            # Should be limited to 5 points
            assert len(result[0]["bulletPoints"]) == 5
            assert result[0]["bulletPoints"][0] == "Point 1"

        finally:
            os.unlink(temp_file_path)

    def test_transform_numeric_fields(self):
        """Test transformation of numeric fields"""
        csv_content = "Price,MRP,Quantity\n100.50,150.75,10"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            column_mapping = [
                {"seller_column": "Price", "marketplace_attribute": "price"},
                {"seller_column": "MRP", "marketplace_attribute": "mrp"},
                {"seller_column": "Quantity", "marketplace_attribute": "quantity"},
            ]

            result = DataTransformer.transform_data(
                temp_file_path, "csv", column_mapping
            )

            assert isinstance(result[0]["price"], float)
            assert result[0]["price"] == 100.5
            assert isinstance(result[0]["mrp"], float)
            assert result[0]["mrp"] == 150.75
            assert isinstance(result[0]["quantity"], int)
            assert result[0]["quantity"] == 10

        finally:
            os.unlink(temp_file_path)

    def test_apply_transformations(self):
        """Test individual transformation functions"""
        # Test uppercase transformation
        result = DataTransformer._apply_transformation("test", "uppercase")
        assert result == "TEST"

        # Test lowercase transformation
        result = DataTransformer._apply_transformation("TEST", "lowercase")
        assert result == "test"

        # Test strip transformation
        result = DataTransformer._apply_transformation("  test  ", "strip")
        assert result == "test"

        # Test split_images transformation
        result = DataTransformer._apply_transformation(
            "img1.jpg,img2.jpg,img3.jpg", "split_images"
        )
        assert result == ["img1.jpg", "img2.jpg", "img3.jpg"]

    def test_handle_special_cases(self):
        """Test handling of special cases"""
        # Test images field
        result = DataTransformer._handle_special_cases("img1.jpg,img2.jpg", "images")
        assert result == ["img1.jpg", "img2.jpg"]

        # Test single image
        result = DataTransformer._handle_special_cases("img1.jpg", "images")
        assert result == ["img1.jpg"]

        # Test bullet points
        result = DataTransformer._handle_special_cases(
            "Point 1|Point 2|Point 3", "bulletPoints"
        )
        assert result == ["Point 1", "Point 2", "Point 3"]

        # Test numeric fields
        result = DataTransformer._handle_special_cases("100.50", "price")
        assert result == 100.5

        result = DataTransformer._handle_special_cases("10", "quantity")
        assert result == 10

