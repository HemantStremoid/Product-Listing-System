import pytest
from app.services.validation import DataValidator
from app.schemas import AttributeDefinition, AttributeType, ValidationError


class TestDataValidator:

    def test_validate_required_fields(self):
        """Test validation of required fields"""
        template = {
            "productName": AttributeDefinition(
                name="productName", type=AttributeType.STRING, required=True
            ),
            "price": AttributeDefinition(
                name="price", type=AttributeType.NUMBER, required=True
            ),
        }

        data = [
            {"productName": "Test Product", "price": 100},
            {"productName": "", "price": 200},  # Empty required field
            {"price": 300},  # Missing required field
        ]

        column_mapping = [
            {"seller_column": "Name", "marketplace_attribute": "productName"},
            {"seller_column": "Price", "marketplace_attribute": "price"},
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 2  # Two validation errors
        assert any(error.field == "productName" for error in result.errors)
        assert any(error.field == "productName" for error in result.errors)

    def test_validate_string_length(self):
        """Test validation of string length constraints"""
        template = {
            "productName": AttributeDefinition(
                name="productName",
                type=AttributeType.STRING,
                required=True,
                max_length=10,
            )
        }

        data = [
            {"productName": "Short"},  # Valid
            {
                "productName": "This is a very long product name that exceeds the limit"
            },  # Invalid
        ]

        column_mapping = [
            {"seller_column": "Name", "marketplace_attribute": "productName"}
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "exceeds maximum length" in result.errors[0].message

    def test_validate_numeric_constraints(self):
        """Test validation of numeric constraints"""
        template = {
            "price": AttributeDefinition(
                name="price",
                type=AttributeType.NUMBER,
                required=True,
                min_value=0,
                max_value=1000,
            )
        }

        data = [
            {"price": 100},  # Valid
            {"price": -50},  # Invalid: below min
            {"price": 1500},  # Invalid: above max
            {"price": "invalid"},  # Invalid: not a number
        ]

        column_mapping = [{"seller_column": "Price", "marketplace_attribute": "price"}]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 3

    def test_validate_enum_values(self):
        """Test validation of enum values"""
        template = {
            "gender": AttributeDefinition(
                name="gender",
                type=AttributeType.ENUM,
                required=True,
                enum_values=["Men", "Women", "Unisex"],
            )
        }

        data = [
            {"gender": "Men"},  # Valid
            {"gender": "Invalid"},  # Invalid
            {"gender": "Women"},  # Valid
        ]

        column_mapping = [
            {"seller_column": "Gender", "marketplace_attribute": "gender"}
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "must be one of" in result.errors[0].message

    def test_validate_business_rules(self):
        """Test validation of business rules"""
        template = {
            "price": AttributeDefinition(
                name="price", type=AttributeType.NUMBER, required=True
            ),
            "mrp": AttributeDefinition(
                name="mrp", type=AttributeType.NUMBER, required=True
            ),
        }

        data = [
            {"price": 100, "mrp": 150},  # Valid: price <= mrp
            {"price": 200, "mrp": 150},  # Invalid: price > mrp
        ]

        column_mapping = [
            {"seller_column": "Price", "marketplace_attribute": "price"},
            {"seller_column": "MRP", "marketplace_attribute": "mrp"},
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "cannot be greater than MRP" in result.errors[0].message

    def test_validate_url_fields(self):
        """Test validation of URL fields"""
        template = {
            "image1": AttributeDefinition(
                name="image1", type=AttributeType.STRING, required=True
            )
        }

        data = [
            {"image1": "https://example.com/image.jpg"},  # Valid URL
            {"image1": "not-a-url"},  # Invalid URL
        ]

        column_mapping = [
            {"seller_column": "Image1", "marketplace_attribute": "image1"}
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "must be a valid URL" in result.errors[0].message

    def test_valid_data_passes_validation(self):
        """Test that valid data passes validation"""
        template = {
            "productName": AttributeDefinition(
                name="productName",
                type=AttributeType.STRING,
                required=True,
                max_length=100,
            ),
            "price": AttributeDefinition(
                name="price", type=AttributeType.NUMBER, required=True, min_value=0
            ),
            "gender": AttributeDefinition(
                name="gender",
                type=AttributeType.ENUM,
                required=True,
                enum_values=["Men", "Women", "Unisex"],
            ),
        }

        data = [{"productName": "Test Product", "price": 100, "gender": "Men"}]

        column_mapping = [
            {"seller_column": "Name", "marketplace_attribute": "productName"},
            {"seller_column": "Price", "marketplace_attribute": "price"},
            {"seller_column": "Gender", "marketplace_attribute": "gender"},
        ]

        result = DataValidator.validate_data(data, template, column_mapping)

        assert result.is_valid
        assert len(result.errors) == 0

