#!/usr/bin/env python3
"""Generate large seller file, upload, map and measure time.
Usage: python scripts/run_large_test.py --rows 5000
"""
import argparse
import time
import requests
import os
from subprocess import check_call

BASE_URL = os.environ.get("APP_URL", "http://localhost:8000")


def generate(rows, out):
    check_call(
        [
            "python",
            "scripts/generate_large_seller_file.py",
            "--rows",
            str(rows),
            "--out",
            out,
        ]
    )


def upload(file_path):
    url = f"{BASE_URL}/api/seller-file/upload"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        r = requests.post(url, files=files)
    r.raise_for_status()
    return r.json()


def create_mapping(template_id, seller_file_id):
    url = f"{BASE_URL}/api/mapping/"
    payload = {
        "name": "Large test mapping",
        "marketplace_template_id": template_id,
        "seller_file_id": seller_file_id,
        "column_mapping": [
            {"seller_column": "Name", "marketplace_attribute": "title"},
            {"seller_column": "Price", "marketplace_attribute": "price"},
            {"seller_column": "BrandName", "marketplace_attribute": "brand"},
        ],
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument(
        "--out", type=str, default="tests/fixtures/large_seller_file.csv"
    )
    parser.add_argument("--template-id", type=int, default=1)
    args = parser.parse_args()

    print("Generating CSV...")
    t0 = time.time()
    generate(args.rows, args.out)
    t1 = time.time()
    print(f"CSV generated in {t1 - t0:.2f}s")

    print("Uploading...")
    t0 = time.time()
    up = upload(args.out)
    t1 = time.time()
    print(f"Upload done in {t1 - t0:.2f}s; response id={up.get('id')}")

    seller_file_id = up.get("id")
    print("Creating mapping (transform + validate)...")
    t0 = time.time()
    mapping = create_mapping(args.template_id, seller_file_id)
    t1 = time.time()
    print(f"Mapping created in {t1 - t0:.2f}s; mapping id={mapping.get('id')}")
    print("Summary:")
    print(f"Rows: {args.rows}")
    print(f"Transformed rows: {len(mapping.get('transformed_data') or [])}")
    print(f"Validation is_valid: {mapping.get('is_valid')}")


if __name__ == "__main__":
    main()
