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
- **TextTVPage**: Complete page with metadata from texttv.nu API

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

1. **Raw API/File Data** → JSON with HTML content from texttv.nu
2. **Pydantic Parsing** → Validated TextTVPage objects
3. **Text Cleaning** → `get_clean_text()` extracts readable content from HTML
4. **Output** → Clean text or structured data

## Text Cleaning Algorithm

The `get_clean_text()` method:
1. Parses HTML content with BeautifulSoup
2. Removes script and style elements
3. Extracts text content
4. Strips whitespace from each line
5. Removes empty lines
6. Filters out headers (SVT TEXT) and lone page numbers
7. Removes duplicate consecutive lines
8. Returns cleaned, readable text

## API Structure (texttv.nu)

Endpoint: `https://api.texttv.nu/api/get/{page_number}`

Query parameters:
- `app`: Application identifier (recommended)

Response structure:
```json
[{
  "num": "100",
  "title": "Nyheter",
  "content": ["<div>...HTML content...</div>"],
  "content_plain": [],
  "next_page": "101",
  "prev_page": "99",
  "date_updated_unix": 1697200000,
  "permalink": "https://texttv.nu/100",
  "id": "12345",
  "breadcrumbs": []
}]
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
- beautifulsoup4: HTML parsing
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
- Content is HTML with CSS classes for styling
- The parser extracts clean text from HTML structure
