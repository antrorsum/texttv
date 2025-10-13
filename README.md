# TextTV Parser

A Python application to parse and clean data from Sweden SVT TextTV REST API.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Try it immediately!
uv run python getting_started.py
```

This interactive guide will walk you through all features!

## Features

- 🇸🇪 Parse Sweden SVT TextTV pages from REST API
- 🧹 Clean and extract readable text from TextTV format
- 📝 Export cleaned data to JSON
- 🔍 Search across multiple pages
- 🚀 Async and sync API support
- 🎯 Type-safe with Pydantic models
- 💻 CLI interface with rich output
- 🔄 **Supports texttv.nu API format**

## Installation

This project uses [uv](https://github.com/astral-sh/uv) as the package manager:

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev
```

## Quick Start

### Parse from sample file
```bash
# Run the demo with sample data
uv run python main.py

# Parse a file and show clean text only
uv run texttv parse-file index.txt --clean
```

### Fetch live data
```bash
# Get page 100 (news)
uv run texttv get-page 100

# Get a specific subpage
uv run texttv get-page 100 --subpage 2

# Save to file
uv run texttv get-page 100 --output news.json
```

### Search functionality
```bash
# Search for text in news pages (100-199)
uv run texttv search "klimat" --start 100 --end 110

# Search in sports pages
uv run texttv search "fotboll" --start 150 --end 159
```

## Programmatic Usage

### Synchronous API
```python
from src.texttv_parser import SyncTextTVParser

parser = SyncTextTVParser()

# Fetch a page
page = parser.get_page("100")
if page:
    print(f"Title: {page.title}")
    print(f"Clean text:\n{page.get_clean_text()}")

# Parse from file
page = parser.parse_from_file("index.txt")
```

### Asynchronous API
```python
import asyncio
from src.texttv_parser import TextTVParser

async def main():
    async with TextTVParser() as parser:
        # Get a single page
        page = await parser.get_page("100")
        
        # Get multiple pages
        pages = await parser.get_page_range("100", "105")
        
        # Search across pages
        results = await parser.search_pages("klimat", (100, 110))

asyncio.run(main())
```

## Data Structure

The parser works with the **texttv.nu API format**:

### Real API Format (texttv.nu)
```bash
# Download real data
curl "https://api.texttv.nu/api/get/100?app=texttv-parser" > news.json

# Parse it
uv run texttv parse-file news.json --clean
```

### Data Flow
```python
# Raw TextTV data from API
[{
  "num": "100",
  "title": "Nyheter",
  "content": ["<div>...HTML content...</div>"],
  "date_updated_unix": 1697200000,
  ...
}]

# Cleaned output
page.get_clean_text() returns:
"""
Regeringen presenterar ny klimatpolitik

Statsministern meddelade idag att regeringen
kommer att presentera nya åtgärder för att
minska utsläppen med 30 procent till 2030.
"""
```

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src
```

## TextTV Page Structure

Swedish TextTV uses a specific format:
- Page numbers: 100-899 (100-199 = News, 150-159 = Sports, etc.)
- Each page can have multiple subpages
- Content includes navigation, headers, and actual text
- The parser extracts only the meaningful text content

## API Endpoints

The real TextTV API:
- **texttv.nu**: `https://api.texttv.nu/api/get/{page_number}?app=yourapp`
- Example: `https://api.texttv.nu/api/get/100?app=texttv-parser`

See [API_FORMATS.md](API_FORMATS.md) for detailed documentation on the API format.

## License

MIT License - see LICENSE file for details.
