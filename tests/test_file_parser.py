import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock
from app.services.file_parser import FileParser


class TestFileParser:

    def test_parse_csv_file(self):
        """Test parsing CSV file"""
        # Create a temporary CSV file
        csv_content = (
            "SKU,Name,BrandName,Price,MRP\nSKU001,Test Product,Brand A,100,150"
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            # Create mock UploadFile
            mock_file = Mock()
            mock_file.filename = "test.csv"
            mock_file.read = Mock(return_value=csv_content.encode())

            # Test the parser
            columns, sample_rows, row_count = FileParser.parse_file(mock_file)

            assert columns == ["SKU", "Name", "BrandName", "Price", "MRP"]
            assert len(sample_rows) == 1
            assert sample_rows[0]["SKU"] == "SKU001"
            assert row_count == 1

        finally:
            os.unlink(temp_file_path)

    def test_parse_excel_file(self):
        """Test parsing Excel file"""
        # Create a temporary Excel file
        df = pd.DataFrame(
            {
                "SKU": ["SKU001", "SKU002"],
                "Name": ["Product 1", "Product 2"],
                "Price": [100, 200],
            }
        )

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            df.to_excel(temp_file.name, index=False)
            temp_file_path = temp_file.name

        try:
            # Create mock UploadFile
            mock_file = Mock()
            mock_file.filename = "test.xlsx"
            with open(temp_file_path, "rb") as f:
                mock_file.read = Mock(return_value=f.read())

            # Test the parser
            columns, sample_rows, row_count = FileParser.parse_file(mock_file)

            assert "SKU" in columns
            assert "Name" in columns
            assert "Price" in columns
            assert row_count == 2

        finally:
            os.unlink(temp_file_path)

    def test_get_file_data_csv(self):
        """Test reading CSV file data"""
        csv_content = "SKU,Name,Price\nSKU001,Test,100"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            df = FileParser.get_file_data(temp_file_path, "csv")
            assert len(df) == 1
            assert df.iloc[0]["SKU"] == "SKU001"

        finally:
            os.unlink(temp_file_path)

    def test_get_file_data_excel(self):
        """Test reading Excel file data"""
        df = pd.DataFrame({"SKU": ["SKU001"], "Name": ["Test Product"], "Price": [100]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            df.to_excel(temp_file.name, index=False)
            temp_file_path = temp_file.name

        try:
            result_df = FileParser.get_file_data(temp_file_path, "xlsx")
            assert len(result_df) == 1
            assert result_df.iloc[0]["SKU"] == "SKU001"

        finally:
            os.unlink(temp_file_path)

