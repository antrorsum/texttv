"""Test cases for TextTV Parser."""

import json
import pytest
from texttv.models import TextTVPage
from texttv.parser import SyncTextTVParser, TextTVParser


@pytest.fixture
def sample_data():
    """Sample TextTV API data for testing (texttv.nu format)."""
    return [
        {
            "num": "100",
            "title": "Nyheter",
            "content": [
                '<div class="root"><span class="line">Regeringen presenterar ny klimatpolitik</span><span class="line">Statsministern meddelade idag att regeringen</span></div>'
            ],
            "content_plain": [],
            "next_page": "101",
            "prev_page": "99",
            "date_updated_unix": 1697200000,
            "permalink": "https://texttv.nu/100",
            "id": "12345",
            "breadcrumbs": [],
        }
    ]


def test_texttv_page_parsing(sample_data):
    """Test parsing of TextTV page."""
    page = TextTVPage.model_validate(sample_data[0])

    assert page.num == "100"
    assert page.title == "Nyheter"
    assert len(page.content) > 0
    assert page.next_page == "101"


def test_clean_text_extraction(sample_data):
    """Test text cleaning functionality."""
    page = TextTVPage.model_validate(sample_data[0])

    clean_text = page.get_clean_text()

    # Should contain the actual content
    assert "Regeringen presenterar ny klimatpolitik" in clean_text
    assert "Statsministern meddelade idag att regeringen" in clean_text

    # Should be properly cleaned (no excessive whitespace)
    lines = clean_text.split("\n")
    for line in lines:
        # No line should have leading/trailing whitespace
        assert line == line.strip()


def test_file_parsing(tmp_path, sample_data):
    """Test parsing from file."""
    # Create temporary file
    temp_file = tmp_path / "test.json"
    with open(temp_file, "w") as f:
        json.dump(sample_data, f)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(temp_file))

    assert page is not None
    assert page.num == "100"
    assert page.title == "Nyheter"


def test_invalid_file_parsing():
    """Test parsing non-existent file."""
    parser = SyncTextTVParser()
    page = parser.parse_from_file("nonexistent.json")

    assert page is None


def test_api_format_parsing(tmp_path):
    """Test parsing texttv.nu API format."""
    # Sample API format data
    api_data = [
        {
            "num": "100",
            "title": "Nyheter",
            "content": [
                '<div class="root"><span class="line">Test content</span></div>'
            ],
            "content_plain": [],
            "next_page": "101",
            "prev_page": "99",
            "date_updated_unix": 1697200000,
            "permalink": "https://texttv.nu/100",
            "id": "12345",
            "breadcrumbs": [],
        }
    ]

    # Write to temp file
    temp_file = tmp_path / "api.json"
    with open(temp_file, "w") as f:
        json.dump(api_data, f)

    # Parse the file
    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(temp_file))

    assert page is not None
    assert page.num == "100"
    assert page.title == "Nyheter"
    assert "Test content" in page.get_clean_text()


def test_compact_text_conversion():
    """Test compact text conversion with Swedish characters."""
    # Sample data with Swedish characters and mixed case
    sample_data = {
        "num": "100",
        "title": "Nyheter",
        "content": [
            "<div>Regeringen presenterar åtgärder<br>Miljön och klimatet<br>Räddningstjänsten räddade öar</div>"
        ],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": [],
    }

    page = TextTVPage.model_validate(sample_data)
    compact_text = page.get_compact_text()

    # Should be uppercase
    assert compact_text.isupper()

    # Should contain Swedish characters in uppercase
    assert "Å" in compact_text
    assert "Ö" in compact_text
    assert "Ä" in compact_text

    # Should not contain lowercase
    assert "å" not in compact_text
    assert "ö" not in compact_text
    assert "ä" not in compact_text

    # Should contain the actual content
    assert "REGERINGEN" in compact_text
    assert "MILJÖN" in compact_text
    assert "RÄDDNINGSTJÄNSTEN" in compact_text


def test_compact_special_characters():
    """Test compact text handling of special characters."""
    # Sample data with special characters (using actual special Unicode chars)
    sample_data = {
        "num": "100",
        "title": "Test",
        "content": [
            "<div>Test \u2013 en dash<br>Test \u2014 em dash<br>Test \u201csmart\u201d quotes<br>Test \u2018curly\u2019 quotes<br>Test\u2026 ellipsis</div>"
        ],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": [],
    }

    page = TextTVPage.model_validate(sample_data)
    compact_text = page.get_compact_text()

    # Dashes should be converted to hyphen (but compacted to single dash)
    assert "-" in compact_text
    assert "\u2013" not in compact_text  # en dash
    assert "\u2014" not in compact_text  # em dash

    # Smart quotes should be converted to straight quotes
    assert '"' in compact_text
    assert "\u201c" not in compact_text  # left double quote
    assert "\u201d" not in compact_text  # right double quote

    # Curly quotes should be converted to straight apostrophe
    assert "'" in compact_text
    assert "\u2018" not in compact_text  # left single quote
    assert "\u2019" not in compact_text  # right single quote

    # Ellipsis should be converted to periods (then compacted to single period)
    assert "." in compact_text
    assert "\u2026" not in compact_text  # horizontal ellipsis


def test_compact_only_supported_chars():
    """Test that compact text only contains supported characters."""
    sample_data = {
        "num": "100",
        "title": "Test",
        "content": ["<div>Test 123 with numbers and punctuation: !@#$%</div>"],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": [],
    }

    page = TextTVPage.model_validate(sample_data)
    compact_text = page.get_compact_text()

    # Define compact text supported characters
    compact_chars = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        r" ./?+-`~!@#$%^&*()_=[]\{}|;:'\"&<>,"
        "¡¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
        "\n"  # newlines are allowed
    )

    # Check that all characters in output are supported
    for char in compact_text:
        assert char in compact_chars, f"Unsupported character: {char}"


def test_compact_removes_padding():
    """Test that compact text removes padding."""
    sample_data = {
        "num": "100",
        "title": "Test",
        "content": [
            "<div>Test    with    multiple    spaces<br>Line with... lots.... of dots....<br>Some----dashes----here<br>Normal text here</div>"
        ],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": [],
    }

    page = TextTVPage.model_validate(sample_data)
    compact = page.get_compact_text()

    # Multiple spaces should be reduced to single space
    assert "    " not in compact

    # Multiple dots should be reduced to single dot
    assert "..." not in compact
    assert ".." not in compact

    # Multiple dashes should be reduced to single dash
    assert "--" not in compact

    # Content should still be present
    assert "TEST WITH MULTIPLE SPACES" in compact
    assert "LOTS" in compact
    assert "DOTS" in compact
    assert "DASHES" in compact
    assert "NORMAL TEXT HERE" in compact


def test_compact_preserves_content():
    """Test that compact text preserves actual content (letters and numbers)."""
    sample_data = {
        "num": "100",
        "title": "Test",
        "content": [
            "<div>News    123<br>Weather....forecast<br>Temperature----20C</div>"
        ],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": [],
    }

    page = TextTVPage.model_validate(sample_data)
    compact = page.get_compact_text()

    # All content should be preserved
    assert "NEWS" in compact
    assert "123" in compact
    assert "WEATHER" in compact
    assert "FORECAST" in compact
    assert "TEMPERATURE" in compact
    assert "20C" in compact


@pytest.mark.asyncio
async def test_get_page_range_parallel():
    """Test that get_page_range fetches pages in parallel."""
    # Create mock pages
    mock_pages = {
        "100": TextTVPage(
            num="100",
            title="Page 100",
            content=["<div>Content 100</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/100",
            id="100",
        ),
        "101": TextTVPage(
            num="101",
            title="Page 101",
            content=["<div>Content 101</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/101",
            id="101",
        ),
        "102": TextTVPage(
            num="102",
            title="Page 102",
            content=["<div>Content 102</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/102",
            id="102",
        ),
    }

    async with TextTVParser() as parser:
        # Mock the get_page method to return our mock pages
        async def mock_get_page(page_number, app="texttv-parser", include_plain_text=False):
            return mock_pages.get(page_number)

        parser.get_page = mock_get_page

        # Fetch range
        results = await parser.get_page_range("100", "102")

        # Verify all pages were fetched
        assert len(results) == 3
        assert "100" in results
        assert "101" in results
        assert "102" in results
        assert results["100"].title == "Page 100"
        assert results["101"].title == "Page 101"
        assert results["102"].title == "Page 102"


@pytest.mark.asyncio
async def test_get_page_range_handles_missing_pages():
    """Test that get_page_range handles missing pages gracefully."""
    # Create mock pages with one missing
    mock_pages = {
        "100": TextTVPage(
            num="100",
            title="Page 100",
            content=["<div>Content 100</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/100",
            id="100",
        ),
        "102": TextTVPage(
            num="102",
            title="Page 102",
            content=["<div>Content 102</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/102",
            id="102",
        ),
    }

    async with TextTVParser() as parser:
        # Mock the get_page method to return our mock pages
        async def mock_get_page(page_number, app="texttv-parser", include_plain_text=False):
            return mock_pages.get(page_number)

        parser.get_page = mock_get_page

        # Fetch range (101 is missing)
        results = await parser.get_page_range("100", "102")

        # Verify only existing pages are returned
        assert len(results) == 2
        assert "100" in results
        assert "101" not in results  # Missing page should not be in results
        assert "102" in results


@pytest.mark.asyncio
async def test_search_pages():
    """Test search_pages functionality."""
    # Create mock pages
    mock_pages = {
        "100": TextTVPage(
            num="100",
            title="Weather News",
            content=["<div>The weather today is sunny</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/100",
            id="100",
        ),
        "101": TextTVPage(
            num="101",
            title="Sports",
            content=["<div>Football match results</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/101",
            id="101",
        ),
        "102": TextTVPage(
            num="102",
            title="Weather Forecast",
            content=["<div>Tomorrow weather will be rainy</div>"],
            date_updated_unix=1697200000,
            permalink="https://texttv.nu/102",
            id="102",
        ),
    }

    async with TextTVParser() as parser:
        # Mock the get_page method
        async def mock_get_page(page_number, app="texttv-parser", include_plain_text=False):
            return mock_pages.get(page_number)

        parser.get_page = mock_get_page

        # Search for "weather"
        results = await parser.search_pages("weather", (100, 102))

        # Should find pages 100 and 102 (both contain "weather")
        assert len(results) == 2
        assert "100" in results
        assert "101" not in results  # Doesn't contain "weather"
        assert "102" in results


@pytest.mark.asyncio
async def test_search_pages_case_insensitive():
    """Test that search_pages is case-insensitive."""
    # Create mock page
    mock_page = TextTVPage(
        num="100",
        title="News",
        content=["<div>Regeringen presenterar KLIMATPOLITIK</div>"],
        date_updated_unix=1697200000,
        permalink="https://texttv.nu/100",
        id="100",
    )

    async with TextTVParser() as parser:
        # Mock the get_page method
        async def mock_get_page(page_number, app="texttv-parser", include_plain_text=False):
            return mock_page if page_number == "100" else None

        parser.get_page = mock_get_page

        # Search with different case
        results = await parser.search_pages("klimat", (100, 100))

        # Should find the page despite case difference
        assert len(results) == 1
        assert "100" in results
