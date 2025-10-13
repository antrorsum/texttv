"""Test fixtures and utilities."""

import pytest


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "page": {
            "number": "150",
            "title": "Sport",
            "content": [
                {
                    "type": "text",
                    "data": "  SPORT                                            Sida 150 (1/3) ",
                    "position": {"row": 3, "col": 1}
                },
                {
                    "type": "text",
                    "data": "  Sverige vinner VM-guld                                         ",
                    "position": {"row": 5, "col": 1}
                },
                {
                    "type": "text",
                    "data": "  Det svenska laget tog hem guldet efter en                     ",
                    "position": {"row": 7, "col": 1}
                },
                {
                    "type": "text",
                    "data": "  spännande final mot Norge.                                     ",
                    "position": {"row": 8, "col": 1}
                }
            ],
            "updated": "2024-10-13T15:45:00Z",
            "subpage": 1,
            "total_subpages": 3
        }
    }
