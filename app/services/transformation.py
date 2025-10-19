from typing import List, Dict, Any
from app.services.file_parser import FileParser
import pandas as pd


class DataTransformer:
    @staticmethod
    def transform_data(
        file_path: str, file_type: str, column_mapping: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Transform seller file data according to column mapping using vectorized
        pandas operations to handle large files efficiently.
        """
        # Read and normalize file data
        df = FileParser.get_file_data(file_path, file_type)
        df.rename(
            columns=lambda c: c.strip() if isinstance(c, str) else c, inplace=True
        )

        # Build mapping lookup keyed by normalized seller column name
        mapping_lookup = {
            (
                mapping["seller_column"].strip().lower()
                if isinstance(mapping["seller_column"], str)
                else mapping["seller_column"]
            ): mapping
            for mapping in column_mapping
        }

        transformed_df = pd.DataFrame(index=df.index)

        for seller_col_norm, mapping in mapping_lookup.items():
            marketplace_attr = mapping["marketplace_attribute"]

            # Find the actual column name in df by case-insensitive match
            matched_col = None
            for col in df.columns:
                if isinstance(col, str) and col.strip().lower() == seller_col_norm:
                    matched_col = col
                    break

            if matched_col is None:
                continue

            series = df[matched_col]

            # Apply transformations
            transformation = mapping.get("transformation")
            if transformation == "uppercase":
                series = series.fillna("").astype(str).str.upper().replace({"": None})
            elif transformation == "lowercase":
                series = series.fillna("").astype(str).str.lower().replace({"": None})
            elif transformation == "strip":
                series = series.fillna("").astype(str).str.strip().replace({"": None})
            elif transformation == "split_images":
                series = (
                    series.fillna("")
                    .astype(str)
                    .apply(
                        lambda v: (
                            [img.strip() for img in v.split(",") if img.strip()]
                            if v
                            else []
                        )
                    )
                )

            # Attribute specific handling
            if marketplace_attr == "images":
                series = (
                    series.fillna("")
                    .astype(str)
                    .apply(
                        lambda v: (
                            [img.strip() for img in v.split(",") if img.strip()]
                            if v
                            else []
                        )
                    )
                )

            if marketplace_attr == "bulletPoints":
                series = (
                    series.fillna("")
                    .astype(str)
                    .apply(
                        lambda v: (
                            [p.strip() for p in v.split("|") if p.strip()][:5]
                            if v
                            else []
                        )
                    )
                )

            if marketplace_attr in ["mrp", "price", "listingPrice", "quantity"]:
                cleaned = (
                    series.fillna("")
                    .astype(str)
                    .str.replace(r"[^0-9.\-]", "", regex=True)
                )
                numeric = pd.to_numeric(cleaned.replace({"": None}), errors="coerce")

                def numeric_cast(x):
                    if pd.isna(x):
                        return None
                    if float(x).is_integer():
                        return int(x)
                    return float(x)

                series = numeric.apply(numeric_cast)

            transformed_df[marketplace_attr] = series

        transformed_data = transformed_df.where(
            pd.notnull(transformed_df), None
        ).to_dict(orient="records")
        return transformed_data

    @staticmethod
    def _apply_transformation(value: Any, transformation: str) -> Any:
        """Fallback single-value transformation (kept for backward compatibility)."""
        if transformation == "uppercase":
            return str(value).upper() if value is not None else value
        if transformation == "lowercase":
            return str(value).lower() if value is not None else value
        if transformation == "strip":
            return str(value).strip() if value is not None else value
        if transformation == "split_images":
            if value and isinstance(value, str):
                return [img.strip() for img in value.split(",") if img.strip()]
            return value
        return value

    @staticmethod
    def _handle_special_cases(value: Any, marketplace_attr: str) -> Any:
        """Fallback single-value handler (kept for compatibility)."""
        if marketplace_attr == "images" and value:
            if isinstance(value, str) and "," in value:
                return [img.strip() for img in value.split(",") if img.strip()]
            elif isinstance(value, str):
                return [value]

        if marketplace_attr == "bulletPoints" and value:
            if isinstance(value, str):
                points = [point.strip() for point in value.split("|") if point.strip()]
                return points[:5]

        if marketplace_attr in ["mrp", "price", "listingPrice", "quantity"] and value:
            try:
                f = float(value)
                if f.is_integer():
                    return int(f)
                return f
            except (ValueError, TypeError):
                return value

        return value
