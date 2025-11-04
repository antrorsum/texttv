# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TextTV Parser is a Python application that parses and cleans data from Sweden's TextTV REST API (texttv.nu). It fetches HTML-based content from the real API and extracts readable text.

**Package Manager**: This project uses `uv` (not pip/poetry). Always use `uv run` to execute commands and `uv sync` to manage dependencies.

**Build System**: Uses Hatchling (configured in pyproject.toml) with package source in `src/texttv/` directory.

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

# Run with coverage report (creates htmlcov/index.html)
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

# Type checking (mypy not currently configured in dev dependencies)
uv run mypy src
```

### Building and Distribution
```bash
# Build package (creates dist/ directory with wheel and sdist)
uv build

# Install package locally in editable mode (development)
uv pip install -e .
```

### CLI Usage
```bash
# Parse a local file with real API format
uv run texttv parse-file index.txt --clean

# View colored TextTV display (with ANSI colors)
uv run texttv parse-file index.txt --colored

# View compact text (uppercase, limited character set, no padding)
uv run texttv parse-file index.txt --compact

# Fetch live page from texttv.nu API
uv run texttv get-page 100

# Fetch and display with colored TextTV rendering
uv run texttv get-page 100 --colored

# Fetch and display compact text
uv run texttv get-page 100 --compact

# Fetch page with API plain text content
uv run texttv get-page 100 --include-plain --plain-text

# Search across pages
uv run texttv search "klimat" --start 100 --end 110

# Interactive browser with arrow key navigation
uv run texttv browse

# Start browsing from a specific page
uv run texttv browse 300
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

# Fetch live data from API (requires internet connection)
uv run python examples/fetch_real_data.py
```

## Architecture Overview

### Core Components

1. **models.py** - Pydantic data model
   - `TextTVPage`: The single page model for texttv.nu API format
   - Fields: `num` (page number), `title`, `content` (HTML array), `content_plain` (API plain text), `date_updated_unix`, `next_page`, `prev_page`, `permalink`, `id`
   - `get_clean_text()` method extracts readable text from HTML content
   - `get_plain_text()` returns plain text from API (if available)
   - `get_colored_text()` renders TextTV display with ANSI color codes

2. **parser.py** - Parsing logic
   - `TextTVParser`: Async HTTP client for API access
   - `SyncTextTVParser`: Synchronous wrapper for simple usage
   - `parse_from_file()`: Parses local JSON files (expects texttv.nu format)
   - `get_page()`: Fetches first subpage from texttv.nu API with `?app=` parameter
   - `get_all_subpages()`: Fetches all subpages for a page number (API returns list of pages)

3. **cli.py** - Command-line interface using Typer and Rich
   - `get-page`: Fetch and display pages from texttv.nu API
   - `parse-file`: Parse local JSON files in texttv.nu format
   - `search`: Search text across page ranges
   - `browse`: Interactive TextTV browser with arrow key navigation (Left/Right for pages, Up/Down for subpages)

4. **terminal_renderer.py** - ANSI terminal rendering
   - `TerminalRenderer`: Converts TextTV HTML with CSS classes to ANSI color codes
   - Maps TextTV color classes (bgBl, bgW, etc.) to terminal colors
   - Supports double-height text rendering with bold formatting
   - Used by `TextTVPage.get_colored_text()` method

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

The API returns a list of page objects (subpages). Most pages have 1 subpage, but some may have multiple versions/updates. The parser handles both list format and single dict format.

### Subpages
- The API can return multiple subpages for a single page number (e.g., breaking news updates)
- Each subpage has the same `num` but different `id` and potentially different content
- Use `parser.get_all_subpages(page_number)` to fetch all subpages
- Use `parser.get_page(page_number)` to fetch only the first subpage (default behavior)
- The `browse` command allows navigating through subpages with Up/Down arrow keys

### Text Cleaning Algorithm

Located in `TextTVPage.get_clean_text()` ([models.py](src/texttv/models.py)):

1. Parses HTML content with BeautifulSoup
2. Removes script and style tags
3. Extracts text content
4. Filters "SVT Text" headers (from the top row)
5. Preserves reference page numbers (e.g., "130", "136") as they link to related articles
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
- Optional: Include `includePlainTextContent=1` to get plain text from API
- HTTP client uses 30s timeout with custom User-Agent
- API returns HTML content in the `content` field (array of strings)
- API returns plain text in `content_plain` field (when `includePlainTextContent=1` is used)

### TextTV Page Numbering
- 100-149: News (Nyheter)
- 150-179: Sports (Sport)
- 200-249: Economy (Ekonomi)
- 300-399: Weather (Väder)
- 400-499: Lottery/Games

### TextTV Display Format
- **Standard dimensions**: 40 columns × 24 rows (classic teletext format)
- The terminal renderer automatically pads each line to exactly 40 characters
- Padding uses the last background color of the line to maintain visual continuity
- All 24 rows are preserved, including graphics and decorative elements

### TextTV Graphics (bgImg)
- TextTV uses custom 13×16 pixel GIF images for graphical characters (logos, weather symbols, decorative elements)
- These are referenced as `bgImg` class with URLs like `https://l.texttv.nu/storage/chars/693852549.gif`
- The terminal renderer uses Unicode Legacy Computing symbols (U+1FB00-U+1FB3B) for mosaic graphics
- GIF IDs are mapped to appropriate mosaic characters in [gif_char_mapping.json](gif_char_mapping.json)
- Example: The "SVT Text" logo on lines 2-5 of page 100 is composed of bgImg characters
- Weather maps (e.g., page 401) use colored bgImg blocks to show cloud cover, temperature zones, etc.

### Whitespace Preservation
- **Fixed**: The renderer now preserves exact whitespace from the HTML
- Uses non-breaking space (U+00A0) as placeholder during parsing to prevent HTML parser from collapsing spaces
- Placeholders are restored to regular spaces after rendering
- This ensures perfect alignment of TextTV graphics and logos (e.g., "SVT Text" logo)
- Lines are padded to exactly 40 characters using the last background color of the line

### TextTV Color System
The HTML content uses CSS classes for colors that are mapped to ANSI codes:
- **Background colors**: `bgBl` (black), `bgB` (blue), `bgW` (white), `bgR` (red), `bgG` (green), `bgY` (yellow), `bgC` (cyan), `bgM` (magenta)
  - **CRITICAL**: `Bl` = Black (two letters), `B` = Blue (single letter) - this distinction is essential for correct parsing
- **Foreground colors**: `W` (white), `Y` (yellow), `C` (cyan), `R` (red), `G` (green), `B` (blue), `M` (magenta), `bl` (black)
  - **CRITICAL**: `B` (capital) = Blue FG, `bl` (lowercase) = Black FG - opposite of background!
- **Text styles**: `DH` (double-height, rendered as bold in terminal)
- **Bright colors**: The renderer uses bright ANSI colors (90-97 FG, 100-107 BG) by default for better visibility
  - Exception: Red uses standard ANSI red (31/41) for correct weather map appearance
  - Can be disabled by passing `use_bright_colors=False` to TerminalRenderer
- **Solid color blocks**: When `bgImg` has only a background color (no foreground), the renderer automatically sets matching foreground color to create solid blocks
- The TerminalRenderer class ([terminal_renderer.py](src/texttv/terminal_renderer.py)) handles conversion to ANSI escape codes for terminal display
- See [COLOR_REFERENCE.md](COLOR_REFERENCE.md) for the complete color mapping table

## Common Development Patterns

### Testing Strategy
- Tests use pytest with fixtures for sample data
- Sample data mimics the texttv.nu API format (list with single dict)
- Use `tmp_path` fixture for testing file parsing
- Test both list format `[{...}]` and dict format `{...}` since parser handles both
- Key test areas: page parsing, text cleaning, file parsing, API format compatibility

### Modifying Text Cleaning
- Edit `TextTVPage.get_clean_text()` in [models.py](src/texttv/models.py)
- The method uses BeautifulSoup to parse HTML and extract text
- Consider Swedish character handling (å, ä, ö) when modifying
- Be careful with number filtering - reference page numbers are important content
- Test with real API data from [index.txt](index.txt)

### Adding New CLI Commands
1. Add `@app.command()` decorated function in [cli.py](src/texttv/cli.py)
2. Use Rich Console for output formatting
3. Use Typer for argument/option parsing
4. Follow existing patterns for error handling and user feedback
5. Access page data via `page.num`, `page.title`, `page.date_updated_unix`, etc.

### Working with Page Data
- Page number: `page.num` (string, e.g., "100")
- Title: `page.title` (string)
- Updated timestamp: `page.date_updated_unix` (int, convert with `datetime.fromtimestamp()`)
- Navigation: `page.next_page`, `page.prev_page` (optional strings)
- Clean text: `page.get_clean_text()` (method - extracts and cleans HTML)
- API plain text: `page.get_plain_text()` (method - returns plain text from API if available, None otherwise)
- Colored terminal output: `page.get_colored_text(use_bold=True)` (method - renders with ANSI color codes)

### Sample Data Files
- [index.txt](index.txt): Real API response from page 100, used for testing and examples
- Contains actual HTML with Swedish characters (å, ä, ö) and TextTV formatting
- Includes `content_plain` field with API plain text (fetched with `includePlainTextContent=1`)
- All examples reference this file using `Path(__file__).parent.parent / "index.txt"`

### Text Extraction Methods
The parser provides five ways to get text from a page:

1. **`page.get_clean_text()`** - Extracts text from HTML and cleans it (recommended)
   - Parses HTML with BeautifulSoup
   - Removes navigation elements and "SVT Text" headers
   - Preserves reference page numbers (they link to related articles)
   - Removes duplicate consecutive lines
   - Returns clean, readable text

2. **`page.get_plain_text()`** - Returns plain text from API (if available)
   - Only available when fetched with `include_plain_text=True` parameter
   - Returns the `content_plain` field from the API
   - Preserves original TextTV formatting and spacing
   - Returns `None` if plain text was not requested

3. **`page.get_colored_text(use_bold=True)`** - Terminal rendering with ANSI colors
   - Renders TextTV page as it appears on actual TextTV display
   - Converts CSS classes (bgBl, bgW, W, Y, etc.) to ANSI escape codes
   - Supports background and foreground colors
   - Optional bold formatting for double-height text
   - Returns string with ANSI codes for terminal display

4. **`page.get_compact_text()`** - Compact text with limited character set for efficient transmission
   - Converts to uppercase
   - Filters to supported character set:
     - Uppercase A-Z, numbers 0-9, space
     - Common punctuation: `./?+-\`~!@#$%^&*()_=[]\{}|;:'",&<>,`
     - Extended Latin-1 including Swedish Å, Ä, Ö
   - Maps unsupported characters (smart quotes, em/en dashes, ellipsis) to safe alternatives
   - Always removes padding for compact transmission:
     - Reduces multiple consecutive spaces to single space
     - Reduces multiple dots (....) to single dot (.)
     - Reduces multiple dashes (----) to single dash (-)
     - Preserves all letters, numbers, and actual content
     - Strips leading/trailing padding characters

5. **`page.content`** - Raw HTML content array
   - Original HTML from the API
   - Useful for custom processing

### Entry Points
- CLI: `texttv` command (defined in pyproject.toml scripts)
- Python API: Import from `texttv` package (`from texttv import TextTVParser, SyncTextTVParser`)
- Package structure: `src/texttv/` contains all source code
