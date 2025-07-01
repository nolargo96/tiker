"""
Setup script for Stock Analyzer
株式分析ツールのセットアップスクリプト
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tiker-stock-analyzer",
    version="1.0.0",
    author="Stock Analysis Team",
    author_email="noreply@example.com",
    description="米国株式投資分析ツール - 4専門家による統合分析フレームワーク",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/tiker-stock-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tiker-analyze=unified_stock_analyzer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.md"],
    },
    keywords="stock, analysis, finance, investment, technical-analysis, yfinance",
    project_urls={
        "Bug Reports": "https://github.com/example/tiker-stock-analyzer/issues",
        "Source": "https://github.com/example/tiker-stock-analyzer",
        "Documentation": "https://github.com/example/tiker-stock-analyzer/wiki",
    },
)