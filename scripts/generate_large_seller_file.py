#!/usr/bin/env python3
"""Generate a large seller CSV for testing.
Usage: python scripts/generate_large_seller_file.py --rows 10000 --out /tmp/large.csv
"""
import csv
import argparse
from random import randint, choice, uniform
from datetime import datetime

SIZES = ["XS", "S", "M", "L", "XL", "XXL", "32", "34", "36"]
BRANDS = ["BrandA", "BrandB", "BrandC", "BrandD"]
TITLES = ["T-Shirt", "Shirt", "Jeans", "Dress", "Saree", "Shoes", "Bag"]
COLORS = ["Red", "Blue", "Green", "Black", "White"]


def generate_row(i):
    sku = f"SKU{i:08d}"
    title = f"{choice(TITLES)} {i}"
    brand = choice(BRANDS)
    gender = choice(["Men", "Women", "Boys", "Girls", "Unisex"])
    category = "T-Shirts"
    color = choice(COLORS)
    size = choice(SIZES)
    mrp = round(uniform(10.0, 200.0), 2)
    # Introduce some invalid rows where price > mrp to test validation
    if i % 1000 == 0:
        price = round(mrp + uniform(1.0, 50.0), 2)
    else:
        price = round(uniform(0.5 * mrp, mrp), 2)
    material = choice(["Cotton", "Polyester", "Silk", "Denim"])
    image1 = f"https://example.com/images/{sku}_1.jpg"
    image2 = f"https://example.com/images/{sku}_2.jpg"
    quantity = randint(0, 100)
    description = f"Auto generated product {i}"
    return [
        sku,
        title,
        brand,
        gender,
        category,
        color,
        size,
        mrp,
        price,
        material,
        image1,
        image2,
        quantity,
        description,
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument(
        "--out", type=str, default="tests/fixtures/large_seller_file.csv"
    )
    args = parser.parse_args()

    headers = [
        "SKU",
        "Name",
        "BrandName",
        "Gender",
        "Category",
        "Color",
        "Size",
        "MRP",
        "Price",
        "Material",
        "Image1",
        "Image2",
        "Quantity",
        "Description",
    ]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(1, args.rows + 1):
            writer.writerow(generate_row(i))
    print(f"Wrote {args.rows} rows to {args.out}")


if __name__ == "__main__":
    main()
