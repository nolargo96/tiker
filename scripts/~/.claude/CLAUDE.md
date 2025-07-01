# User Memory

## Code Preferences
- Keep responses concise (max 4 lines unless detail requested)
- Answer directly without preamble/postamble
- Use Japanese for comments in Japanese codebases
- Prefer editing existing files over creating new ones

## Development Workflow
- Always use TodoWrite for complex tasks
- Run lint/typecheck commands after code changes
- Never commit without explicit user request
- Search extensively before implementing

## Stock Analysis Project Preferences
- Focus on US-listed companies only
- Use USD pricing with 2 decimal places
- Date format: YYYY-MM-DD (JST)
- Chart aspect ratio: 16:9
- Minimum 250 trading days for analysis
- 4-expert framework: TECH, FUND, MACRO, RISK

## Common Commands
```bash
# Testing
python -m pytest test_stock_analyzer.py -v

# Code quality
black .
flake8 .
mypy .

# Stock analysis
python unified_stock_analyzer.py --ticker TICKER --date YYYY-MM-DD
```

## Tools & Libraries
- yfinance for stock data
- mplfinance for charts
- pandas/numpy for analysis
- matplotlib for visualization
- pytest for testing