"""Test cases for TextTV Parser."""

import json
from pathlib import Path
import pytest
from src.texttv_parser.models import TextTVPage
from src.texttv_parser.parser import SyncTextTVParser


@pytest.fixture
def sample_data():
    """Sample TextTV API data for testing (texttv.nu format)."""
    return [{
        "num": "100",
        "title": "Nyheter",
        "content": ["<div class=\"root\"><span class=\"line\">Regeringen presenterar ny klimatpolitik</span><span class=\"line\">Statsministern meddelade idag att regeringen</span></div>"],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": []
    }]


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
    with open(temp_file, 'w') as f:
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
    api_data = [{
        "num": "100",
        "title": "Nyheter",
        "content": ["<div class=\"root\"><span class=\"line\">Test content</span></div>"],
        "content_plain": [],
        "next_page": "101",
        "prev_page": "99",
        "date_updated_unix": 1697200000,
        "permalink": "https://texttv.nu/100",
        "id": "12345",
        "breadcrumbs": []
    }]

    # Write to temp file
    temp_file = tmp_path / "api.json"
    with open(temp_file, 'w') as f:
        json.dump(api_data, f)

    # Parse the file
    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(temp_file))

    assert page is not None
    assert page.num == "100"
    assert page.title == "Nyheter"
    assert "Test content" in page.get_clean_text()