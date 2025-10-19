from typing import List, Dict, Any, Optional
from app.schemas import (
    ValidationResult,
    ValidationError,
    AttributeDefinition,
    AttributeType,
)
import re


class DataValidator:
    @staticmethod
    def validate_data(
        data: List[Dict[str, Any]],
        template: Dict[str, AttributeDefinition],
        column_mapping: List[Dict[str, str]],
    ) -> ValidationResult:
        """
        Validate transformed data against marketplace template
        """
        errors = []
        warnings = []

        # Create mapping dictionary for quick lookup
        mapping_dict = {
            mapping["seller_column"]: mapping["marketplace_attribute"]
            for mapping in column_mapping
        }

        for row_idx, row in enumerate(data):
            for seller_col, marketplace_attr in mapping_dict.items():
                if marketplace_attr in template:
                    attr_def = template[marketplace_attr]
                    # Normalize attr_def: templates may store plain dicts (from JSON)
                    # or AttributeDefinition instances. Convert dict -> AttributeDefinition
                    # so downstream code can use attributes like .required and .type.
                    if isinstance(attr_def, dict):
                        try:
                            attr_def = AttributeDefinition(**attr_def)
                        except Exception:
                            # If conversion fails, skip validation for this attribute
                            continue
                    value = row.get(marketplace_attr)

                    # Check required fields
                    if attr_def.required and (value is None or value == ""):
                        errors.append(
                            ValidationError(
                                field=marketplace_attr,
                                message=f"Required field '{marketplace_attr}' is missing or empty",
                                row=row_idx + 1,
                            )
                        )
                        continue

                    # Skip validation if value is empty and field is not required
                    if value is None or value == "":
                        continue

                    # Type-specific validation
                    validation_error = DataValidator._validate_field_type(
                        value, attr_def, marketplace_attr, row_idx + 1
                    )
                    if validation_error:
                        errors.append(validation_error)

                    # Additional business rules validation
                    business_error = DataValidator._validate_business_rules(
                        value, marketplace_attr, row, row_idx + 1
                    )
                    if business_error:
                        errors.append(business_error)

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    @staticmethod
    def _validate_field_type(
        value: Any, attr_def: AttributeDefinition, field_name: str, row: int
    ) -> Optional[ValidationError]:
        """Validate field type and constraints"""

        if attr_def.type == AttributeType.STRING:
            if not isinstance(value, str):
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be a string",
                    row=row,
                )

            if attr_def.max_length and len(value) > attr_def.max_length:
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' exceeds maximum length of {attr_def.max_length}",
                    row=row,
                )

        elif attr_def.type == AttributeType.NUMBER:
            try:
                num_value = float(value)
                if attr_def.min_value is not None and num_value < attr_def.min_value:
                    return ValidationError(
                        field=field_name,
                        message=f"Field '{field_name}' must be >= {attr_def.min_value}",
                        row=row,
                    )
                if attr_def.max_value is not None and num_value > attr_def.max_value:
                    return ValidationError(
                        field=field_name,
                        message=f"Field '{field_name}' must be <= {attr_def.max_value}",
                        row=row,
                    )
            except (ValueError, TypeError):
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be a valid number",
                    row=row,
                )

        elif attr_def.type == AttributeType.INTEGER:
            try:
                int_value = int(value)
                if attr_def.min_value is not None and int_value < attr_def.min_value:
                    return ValidationError(
                        field=field_name,
                        message=f"Field '{field_name}' must be >= {attr_def.min_value}",
                        row=row,
                    )
                if attr_def.max_value is not None and int_value > attr_def.max_value:
                    return ValidationError(
                        field=field_name,
                        message=f"Field '{field_name}' must be <= {attr_def.max_value}",
                        row=row,
                    )
            except (ValueError, TypeError):
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be a valid integer",
                    row=row,
                )

        elif attr_def.type == AttributeType.ENUM:
            if attr_def.enum_values and value not in attr_def.enum_values:
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be one of: {', '.join(attr_def.enum_values)}",
                    row=row,
                )

        elif attr_def.type == AttributeType.ARRAY:
            if not isinstance(value, list):
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be an array",
                    row=row,
                )

        return None

    @staticmethod
    def _validate_business_rules(
        value: Any, field_name: str, row: Dict[str, Any], row_num: int
    ) -> Optional[ValidationError]:
        """Validate business-specific rules"""

        # Price <= MRP validation
        if field_name == "price" and "mrp" in row:
            try:
                price = float(value)
                mrp = float(row.get("mrp", 0))
                if price > mrp:
                    return ValidationError(
                        field=field_name,
                        message=f"Price ({price}) cannot be greater than MRP ({mrp})",
                        row=row_num,
                    )
            except (ValueError, TypeError):
                pass

        # URL validation for image fields
        if field_name.startswith("image") and value:
            if not DataValidator._is_valid_url(str(value)):
                return ValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be a valid URL",
                    row=row_num,
                )

        return None

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Simple URL validation"""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None
