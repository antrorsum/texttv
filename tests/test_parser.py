"""Test cases for TextTV Parser."""

import json
import pytest
from texttv.models import TextTVPage
from texttv.parser import SyncTextTVParser


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


def test_js8call_text_conversion():
    """Test JS8Call text conversion with Swedish characters."""
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
    js8_text = page.get_js8call_text()

    # Should be uppercase
    assert js8_text.isupper()

    # Should contain Swedish characters in uppercase
    assert "Å" in js8_text
    assert "Ö" in js8_text
    assert "Ä" in js8_text

    # Should not contain lowercase
    assert "å" not in js8_text
    assert "ö" not in js8_text
    assert "ä" not in js8_text

    # Should contain the actual content
    assert "REGERINGEN" in js8_text
    assert "MILJÖN" in js8_text
    assert "RÄDDNINGSTJÄNSTEN" in js8_text


def test_js8call_special_characters():
    """Test JS8Call handling of special characters."""
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
    js8_text = page.get_js8call_text()

    # Dashes should be converted to hyphen
    assert "-" in js8_text
    assert "\u2013" not in js8_text  # en dash
    assert "\u2014" not in js8_text  # em dash

    # Smart quotes should be converted to straight quotes
    assert '"' in js8_text
    assert "\u201c" not in js8_text  # left double quote
    assert "\u201d" not in js8_text  # right double quote

    # Curly quotes should be converted to straight apostrophe
    assert "'" in js8_text
    assert "\u2018" not in js8_text  # left single quote
    assert "\u2019" not in js8_text  # right single quote

    # Ellipsis should be converted to three periods
    assert "..." in js8_text
    assert "\u2026" not in js8_text  # horizontal ellipsis


def test_js8call_only_supported_chars():
    """Test that JS8Call text only contains supported characters."""
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
    js8_text = page.get_js8call_text()

    # Define JS8Call supported characters
    js8call_chars = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        r" ./?+-`~!@#$%^&*()_=[]\{}|;:'\"&<>,"
        "¡¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
        "\n"  # newlines are allowed
    )

    # Check that all characters in output are supported
    for char in js8_text:
        assert char in js8call_chars, f"Unsupported character: {char}"


def test_js8call_compact_mode():
    """Test JS8Call compact mode removes padding."""
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

    # Normal mode
    normal = page.get_js8call_text()

    # Compact mode
    compact = page.get_js8call_text(compact=True)

    # Compact should be shorter
    assert len(compact) < len(normal)

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


def test_js8call_compact_preserves_content():
    """Test that compact mode preserves actual content (letters and numbers)."""
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
    compact = page.get_js8call_text(compact=True)

    # All content should be preserved
    assert "NEWS" in compact
    assert "123" in compact
    assert "WEATHER" in compact
    assert "FORECAST" in compact
    assert "TEMPERATURE" in compact
    assert "20C" in compact
