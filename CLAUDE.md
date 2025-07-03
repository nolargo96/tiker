# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Japanese stock analysis toolkit for US-listed companies focused on mid-to-long-term investment entry timing analysis. The project implements a 4-expert framework (TECH, FUND, MACRO, RISK) for comprehensive investment analysis.

## Core Architecture

### Main Components
- **unified_stock_analyzer.py**: Central analysis engine using yfinance for data retrieval and mplfinance for chart generation
- **stock_analyzer_lib.py**: Reusable library components with ConfigManager, TechnicalIndicators, and StockDataManager
- **html_report_generator.py**: Interactive HTML report generation with responsive design
- **tiker.md**: Complete analysis framework specification defining the 4-expert discussion format and output structure
- **scripts/**: Individual stock analysis scripts (ASTS, FSLR, JOBY, LUNR, OII, OKLO, RDW, RKLB, TSLA)
- **test_stock_analyzer.py**: Comprehensive test suite using pytest (14 test cases)

### Data Flow
1. yfinance retrieves 1+ year of OHLCV data (minimum 250 trading days)
2. Technical indicators calculated: EMA20/50, SMA200, RSI, Bollinger Bands, ATR
3. Charts generated and saved to `./charts/` directory
4. Analysis reports generated using 4-expert framework from tiker.md

### Analysis Framework (from tiker.md)
- **TECH**: Technical analysis using moving averages, RSI, MACD, Fibonacci
- **FUND**: Fundamental analysis with PER, PBR, DCF, EPS growth
- **MACRO**: Macro environment analysis (Fed rates, CPI, sector trends)
- **RISK**: Risk management with VaR, drawdown analysis, position sizing

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running Analysis
```bash
# Main unified analyzer
python unified_stock_analyzer.py --ticker AAPL --date 2025-01-31

# Individual stock scripts
python scripts/tsla_analysis.py

# Generate detailed reports (following tiker.md format)
python scripts/fslr_final_report.py
```

### Testing
```bash
python -m pytest test_stock_analyzer.py -v
python -m pytest test_stock_analyzer.py -v --cov=stock_analyzer_lib
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

## File Naming Conventions

- Charts: `{TICKER}_chart_{YYYY-MM-DD}.png` in `./charts/`
- Data: `{TICKER}_analysis_data_{YYYY-MM-DD}.csv`
- Reports: `{TICKER}_analysis_{YYYY-MM-DD}.md` in `./reports/`

## Important Notes

- All stock prices in USD with 2 decimal places
- Dates in JST timezone using YYYY-MM-DD format
- Charts must be 16:9 aspect ratio
- Minimum 250 trading days of data required for analysis
- Invalid tickers return specific error messages
- All analysis is educational/simulation only, not investment advice

## Current Portfolio Composition (9 Stocks)

### Default Allocation (Total: 100%)
- **TSLA**: 20% - EV and autonomous driving technology
- **FSLR**: 20% - Solar panels and CdTe technology  
- **RKLB**: 10% - Small-scale rocket and space infrastructure (newly added)
- **ASTS**: 10% - Satellite communications and direct smartphone connectivity
- **OKLO**: 10% - Small modular reactors (SMR) technology
- **JOBY**: 10% - eVTOL and urban air mobility
- **OII**: 10% - Marine engineering and ROV services
- **LUNR**: 5% - Lunar landing and space exploration
- **RDW**: 5% - Space infrastructure and in-orbit manufacturing

### Recent Updates (2025-01-03)
- **Added RKLB (Rocket Lab)**: 10% allocation for small rocket market leader
- **Rebalanced major holdings**: TSLA and FSLR reduced from 25% to 20% each
- **Enhanced analysis**: Added comprehensive expert discussion templates for all 9 stocks

## Configuration

The project uses YAML configuration files and supports environment-specific settings through the ConfigManager class in stock_analyzer_lib.py.

### Key Configuration Areas
- **Data sources**: yfinance API settings and data validation
- **Technical indicators**: EMA/SMA periods, RSI settings, Bollinger Bands parameters
- **Chart generation**: Styling, dimensions, and export formats
- **HTML reports**: Interactive features and responsive design
- **Expert scoring**: Customizable weightings for TECH/FUND/MACRO/RISK analysis