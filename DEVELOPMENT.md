# TextTV Parser - Development Notes

## Project Structure

```
texttv/
├── src/
│   └── texttv_parser/
│       ├── __init__.py      # Package initialization
│       ├── models.py        # Pydantic data models
│       ├── parser.py        # Core parsing logic
│       └── cli.py           # Command-line interface
├── tests/
│   ├── conftest.py          # Test fixtures
│   └── test_parser.py       # Unit tests
├── index.txt                # Sample TextTV data
├── main.py                  # Demo script
├── examples.py              # Usage examples
├── pyproject.toml           # Project configuration
└── README.md                # Documentation
```

## Architecture

### Models (models.py)
- **TextTVPosition**: Row/column position on page
- **TextTVContent**: Individual content item (text, color, etc.)
- **TextTVPage**: Complete page with metadata
- **TextTVResponse**: API response wrapper

### Parser (parser.py)
- **TextTVParser**: Async API client
  - `get_page()`: Fetch single page
  - `get_page_range()`: Fetch multiple pages
  - `search_pages()`: Search across pages
  - `parse_from_file()`: Parse local JSON
  
- **SyncTextTVParser**: Synchronous wrapper for simple usage

### CLI (cli.py)
Commands:
- `texttv get-page <number>`: Fetch and display page
- `texttv parse-file <path>`: Parse local file
- `texttv search <query>`: Search across pages

## Data Flow

1. **Raw API/File Data** → JSON with positioned content
2. **Pydantic Parsing** → Validated TextTVPage objects
3. **Text Cleaning** → `get_clean_text()` extracts readable content
4. **Output** → Clean text or structured data

## Text Cleaning Algorithm

The `get_clean_text()` method:
1. Filters text-type content items
2. Sorts by row position
3. Strips whitespace from each line
4. Removes empty lines
5. Filters out headers (SVT TEXT, Sida X (Y/Z))
6. Filters out navigation menus (lines with 3+ page numbers)
7. Returns cleaned, readable text

## API Structure (SVT TextTV)

Typical endpoint: `https://www.svt.se/text-tv/api/pages/{page_number}`

Query parameters:
- `sub`: Subpage number

Response structure:
```json
{
  "page": {
    "number": "100",
    "title": "Nyheter",
    "content": [
      {
        "type": "text",
        "data": "...",
        "position": {"row": 1, "col": 1}
      }
    ],
    "updated": "2024-10-13T10:30:00Z",
    "subpage": 1,
    "total_subpages": 5
  }
}
```

## Testing Strategy

- **Unit tests**: Test models, parsing, text cleaning
- **Integration tests**: Test with sample data files
- **Fixtures**: Reusable test data in conftest.py

## Development Workflow

```bash
# Setup
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Format code
uv run black src tests

# Lint
uv run ruff check src tests

# Run demo
uv run python main.py

# Use CLI
uv run texttv parse-file index.txt
```

## Future Enhancements

- [ ] HTML output format
- [ ] Markdown export
- [ ] Image/graphic extraction
- [ ] Real-time page monitoring
- [ ] Database storage
- [ ] Web interface
- [ ] API rate limiting
- [ ] Caching layer
- [ ] More comprehensive text cleaning
- [ ] Support for color/formatting codes

## Dependencies

**Core:**
- httpx: Async HTTP client
- pydantic: Data validation
- typer: CLI framework
- rich: Terminal output formatting

**Dev:**
- pytest: Testing framework
- pytest-asyncio: Async test support
- black: Code formatting
- ruff: Fast linting

## Notes

- TextTV uses Teletext format (40x25 character grid)
- Pages 100-899 are content pages
- Each page can have multiple subpages
- Content includes positioning data for proper layout
- Some pages have color/formatting codes (type: "color")
