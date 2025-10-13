# Quick Start Guide

## Installation

```bash
# Make sure you have uv installed
# Visit: https://github.com/astral-sh/uv

# Clone or navigate to the project
cd texttv

# Install dependencies
uv sync
```

## Your First Parse

### 1. Parse the sample file

```bash
uv run texttv parse-file index.txt --clean
```

### 2. Run the demo

```bash
uv run python main.py
```

### 3. See all examples

```bash
uv run python examples.py
```

## Common Tasks

### Parse a local JSON file
```bash
uv run texttv parse-file your_file.json
```

### Fetch a live page (requires API access)
```bash
# News page
uv run texttv get-page 100

# Sports page  
uv run texttv get-page 150

# Specific subpage
uv run texttv get-page 100 --subpage 2

# Save to file
uv run texttv get-page 100 --output news.json
```

### Search for content
```bash
# Search in news pages (100-199)
uv run texttv search "klimat" --start 100 --end 110

# Search in sports pages (150-159)
uv run texttv search "fotboll" --start 150 --end 159
```

## Use in Your Code

### Simple synchronous usage
```python
from src.texttv_parser import SyncTextTVParser

parser = SyncTextTVParser()

# Parse a file
page = parser.parse_from_file("index.txt")
if page:
    print(page.title)
    print(page.get_clean_text())

# Fetch from API (requires actual endpoint)
# page = parser.get_page("100")
```

### Advanced async usage
```python
import asyncio
from src.texttv_parser import TextTVParser

async def main():
    async with TextTVParser() as parser:
        # Single page
        page = await parser.get_page("100")
        
        # Multiple pages
        pages = await parser.get_page_range("100", "105")
        
        # Search
        results = await parser.search_pages("climate", (100, 110))

asyncio.run(main())
```

## Understanding the Output

### Raw data structure
TextTV pages come with positioned content:
```json
{
  "page": {
    "number": "100",
    "title": "Nyheter",
    "content": [
      {
        "type": "text",
        "data": "  Some text here  ",
        "position": {"row": 5, "col": 1}
      }
    ]
  }
}
```

### Cleaned output
The parser extracts and cleans the text:
```
Some text here
```

Removes:
- Excessive whitespace
- Page headers (SVT TEXT, Sida X)
- Navigation menus
- Empty lines

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test
uv run pytest tests/test_parser.py::test_clean_text_extraction -v
```

## Common Page Numbers

- **100-149**: News (Nyheter)
- **150-179**: Sports (Sport)
- **200-249**: Economy (Ekonomi)
- **300-399**: Weather (Väder)
- **400-499**: Lottery/Games (Lotto/Spel)

## Troubleshooting

### Import errors
Make sure you've run `uv sync` to install dependencies.

### API access
The actual SVT API endpoint may vary or require specific headers. Check the latest documentation or inspect network traffic from the official TextTV website.

### Empty results
Some pages may be empty or unavailable. Check the page number exists on the official TextTV service.

## Next Steps

1. ✅ Try parsing the sample `index.txt` file
2. ✅ Run the examples to see different usage patterns
3. ✅ Write your own scripts using the parser
4. 📖 Read `DEVELOPMENT.md` for architecture details
5. 🧪 Add your own tests
6. 🚀 Extend with new features

## Help

Run any command with `--help`:
```bash
uv run texttv --help
uv run texttv get-page --help
uv run texttv search --help
```
