from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="product-listing-system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A backend system for managing marketplace templates, seller files, and data mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/product-listing-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "product-listing=app.main:app",
        ],
    },
)

