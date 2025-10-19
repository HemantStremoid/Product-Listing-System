Testing guide for Product Listing System

Overview
This file contains example templates, seller CSVs and mapping JSONs in `tests/fixtures/` to exercise real-world scenarios.

Fixtures included
- myntra_template.json - Myntra-like marketplace template
- flipkart_template.json - Flipkart-like marketplace template
- seller_good.csv - Example seller file with good data
- seller_missing_fields.csv - Seller file missing required fields
- seller_invalid_prices.csv - Seller file with price > mrp for some rows
- mapping_myntra_example.json - Example mapping payload for Myntra

Quick manual tests (curl)
1) Create a marketplace template (Myntra)
curl -X POST "http://localhost:8000/api/marketplace/templates" -H "Content-Type: application/json" -d @tests/fixtures/myntra_template.json

2) Upload a seller file (good)
curl -F "file=@tests/fixtures/seller_good.csv" http://localhost:8000/api/seller-file/upload

3) Create mapping (use returned ids or adjust mapping json)
curl -X POST "http://localhost:8000/api/mapping/" -H "Content-Type: application/json" -d @tests/fixtures/mapping_myntra_example.json

Scenarios to run
- Basic happy path: myntra_template + seller_good.csv + mapping_myntra_example.json
- Missing required fields: same template + seller_missing_fields.csv => expect validation errors for missing productName/brand
- Price validation: same template + seller_invalid_prices.csv => expect validation errors where price > mrp

Notes
- Use Swagger UI at /docs for interactive testing and file upload from the browser.
- For large-file testing use scripts/run_large_test.py --rows N
