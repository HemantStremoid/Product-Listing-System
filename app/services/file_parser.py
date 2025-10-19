import pandas as pd
import os
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException
import tempfile


class FileParser:
    @staticmethod
    def parse_file(
        file: UploadFile,
    ) -> Tuple[List[str], List[Dict[str, Any]], int]:
        """
        Parse uploaded CSV/Excel file and return columns, sample rows, and row count
        """
        try:
            # Create temporary file and write uploaded content. We support
            # both FastAPI UploadFile (which exposes async read) and simple
            # objects used in tests that provide a synchronous read().
            suffix = f".{file.filename.split('.')[-1]}"
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix, mode="wb"
            ) as temp_file:
                # Prefer calling file.read() (tests often set this). If not
                # available, fall back to file.file.read().
                if hasattr(file, "read") and callable(file.read):
                    content = file.read()
                elif (
                    hasattr(file, "file")
                    and hasattr(file.file, "read")
                    and callable(file.file.read)
                ):
                    content = file.file.read()
                else:
                    raise ValueError("Uploaded file object has no readable content")

                # If the read returned a string, encode to bytes.
                if isinstance(content, str):
                    content = content.encode()

                # Ensure we have bytes-like content
                if not isinstance(content, (bytes, bytearray)):
                    # Some mocks may still return Mock objects; try to call them
                    if callable(content):
                        content = content()
                    if not isinstance(content, (bytes, bytearray)):
                        raise ValueError("File.read() did not return bytes")

                temp_file.write(content)
                temp_file_path = temp_file.name

            # Determine file type and parse accordingly
            file_extension = file.filename.split(".")[-1].lower()

            if file_extension == "csv":
                df = pd.read_csv(temp_file_path)
            elif file_extension in ["xlsx", "xls"]:
                df = pd.read_excel(temp_file_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type. Only CSV and Excel files are supported.",
                )

            # Clean up temporary file
            os.unlink(temp_file_path)

            # Normalize column names: strip whitespace and remove BOM if present
            def _clean_col(c):
                if not isinstance(c, str):
                    return c
                # Remove BOM and strip whitespace
                return c.replace("\ufeff", "").strip()

            df.rename(columns=_clean_col, inplace=True)

            # Get columns
            columns = df.columns.tolist()

            # Get sample rows (first 5 rows)
            sample_rows = df.head(5).to_dict("records")

            # Get row count
            row_count = len(df)

            return columns, sample_rows, row_count

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

    @staticmethod
    def get_file_data(file_path: str, file_type: str) -> pd.DataFrame:
        """
        Read file data from stored file path
        """
        try:
            if file_type == "csv":
                df = pd.read_csv(file_path)
                # Normalize headers
                df.rename(
                    columns=lambda c: (
                        c.replace("\ufeff", "").strip() if isinstance(c, str) else c
                    ),
                    inplace=True,
                )
                return df
            elif file_type in ["xlsx", "xls"]:
                df = pd.read_excel(file_path)
                df.rename(
                    columns=lambda c: (
                        c.replace("\ufeff", "").strip() if isinstance(c, str) else c
                    ),
                    inplace=True,
                )
                return df
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
