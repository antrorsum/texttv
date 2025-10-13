# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TextTV Parser is a Python application that parses and cleans data from Sweden's TextTV REST API (texttv.nu). It fetches HTML-based content from the real API and extracts readable text.

## Essential Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_parser.py -v

# Run specific test
uv run pytest tests/test_parser.py::test_name -v
```

### Code Quality
```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src
```

### CLI Usage
```bash
# Parse a local file with real API format
uv run texttv parse-file index.txt --clean

# Fetch live page from texttv.nu API
uv run texttv get-page 100

# Search across pages
uv run texttv search "klimat" --start 100 --end 110
```

### Running Examples
```bash
# Interactive getting started guide
uv run python examples/getting_started.py

# Basic demo with sample data
uv run python examples/main.py

# Usage examples
uv run python examples/examples.py

# Advanced examples (7 different scenarios)
uv run python examples/advanced_examples.py
```

## Architecture Overview

### Core Components

1. **models.py** - Pydantic data model
   - `TextTVPage`: The single page model for texttv.nu API format
   - Fields: `num` (page number), `title`, `content` (HTML array), `date_updated_unix`, `next_page`, `prev_page`, `permalink`, `id`
   - `get_clean_text()` method extracts readable text from HTML content

2. **parser.py** - Parsing logic
   - `TextTVParser`: Async HTTP client for API access
   - `SyncTextTVParser`: Synchronous wrapper for simple usage
   - `parse_from_file()`: Parses local JSON files (expects texttv.nu format)
   - `get_page()`: Fetches pages from texttv.nu API with `?app=` parameter

3. **cli.py** - Command-line interface using Typer and Rich
   - `get-page`: Fetch and display pages from texttv.nu API
   - `parse-file`: Parse local JSON files in texttv.nu format
   - `search`: Search text across page ranges

### API Format (texttv.nu)

The parser works with the texttv.nu API format:

```json
[{
  "num": "100",
  "title": "Hamas har frigivit samtliga ur gisslan",
  "content": ["<div>...HTML...</div>"],
  "content_plain": [],
  "next_page": "101",
  "prev_page": "100",
  "date_updated_unix": 1760375163,
  "permalink": "https://texttv.nu/100/start-36750942",
  "id": "36750942",
  "breadcrumbs": []
}]
```

The API returns a list with one page object. The parser handles both list format and single dict format.

### Text Cleaning Algorithm

Located in `TextTVPage.get_clean_text()` ([models.py](src/texttv_parser/models.py)):

1. Parses HTML content with BeautifulSoup
2. Removes script and style tags
3. Extracts text content
4. Filters lone page numbers (e.g., "101")
5. Filters "SVT Text" headers
6. Removes duplicate consecutive lines
7. Returns cleaned, readable text

## Important Implementation Details

### Async/Sync Patterns
- Use `async with TextTVParser() as parser` for async operations
- Use `SyncTextTVParser()` for simple synchronous usage
- `SyncTextTVParser` internally calls `asyncio.run()` to wrap async methods

### API Integration
- Default base URL: `https://api.texttv.nu/api/get`
- API endpoint pattern: `https://api.texttv.nu/api/get/{page}?app=yourapp`
- Always include `?app=` parameter when using texttv.nu API
- HTTP client uses 30s timeout with custom User-Agent
- API returns HTML content in the `content` field (array of strings)

### TextTV Page Numbering
- 100-149: News (Nyheter)
- 150-179: Sports (Sport)
- 200-249: Economy (Ekonomi)
- 300-399: Weather (Väder)
- 400-499: Lottery/Games

### Package Manager
This project uses `uv` (not pip/poetry). Always use `uv run` to execute commands and `uv sync` to manage dependencies.

## Common Development Patterns

### Modifying Text Cleaning
- Edit `TextTVPage.get_clean_text()` in [models.py](src/texttv_parser/models.py)
- The method uses BeautifulSoup to parse HTML and extract text
- Consider Swedish character handling (å, ä, ö) when modifying
- Test with real API data from [index.txt](index.txt)

### Adding New CLI Commands
1. Add `@app.command()` decorated function in [cli.py](src/texttv_parser/cli.py)
2. Use Rich Console for output formatting
3. Use Typer for argument/option parsing
4. Follow existing patterns for error handling and user feedback
5. Access page data via `page.num`, `page.title`, `page.date_updated_unix`, etc.

### Working with Page Data
- Page number: `page.num` (string, e.g., "100")
- Title: `page.title` (string)
- Updated timestamp: `page.date_updated_unix` (int, convert with `datetime.fromtimestamp()`)
- Navigation: `page.next_page`, `page.prev_page` (optional strings)
- Clean text: `page.get_clean_text()` (method)
