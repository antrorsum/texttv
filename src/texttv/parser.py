"""TextTV API Parser - Main parsing functionality."""

import asyncio
import json
from typing import Optional, Dict, List

import httpx
from .models import TextTVPage


class TextTVParser:
    """Parser for Sweden SVT TextTV REST API."""

    def __init__(self, base_url: str = "https://api.texttv.nu/api/get"):
        """Initialize the parser.

        Args:
            base_url: Base URL for the TextTV API (default: texttv.nu API)
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "TextTV-Parser/0.1.0",
                "Accept": "application/json",
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def get_page(
        self,
        page_number: str,
        app: str = "texttv-parser",
        include_plain_text: bool = False,
    ) -> Optional[TextTVPage]:
        """Fetch a specific TextTV page from texttv.nu API.

        Args:
            page_number: Page number (e.g., "100", "150")
            app: Application identifier for the API
            include_plain_text: Include plain text content from API (sets includePlainTextContent=1)

        Returns:
            TextTVPage object or None if not found
        """
        pages = await self.get_all_subpages(page_number, app, include_plain_text)
        return pages[0] if pages else None

    async def get_all_subpages(
        self,
        page_number: str,
        app: str = "texttv-parser",
        include_plain_text: bool = False,
    ) -> list[TextTVPage]:
        """Fetch all subpages for a specific TextTV page number.

        The API returns a list of pages (subpages) for each page number.
        Most pages have 1 subpage, but some may have multiple versions/updates.

        Args:
            page_number: Page number (e.g., "100", "150")
            app: Application identifier for the API
            include_plain_text: Include plain text content from API (sets includePlainTextContent=1)

        Returns:
            List of TextTVPage objects (empty list if not found)
        """
        url = f"{self.base_url}/{page_number}"
        params = {"app": app}
        if include_plain_text:
            params["includePlainTextContent"] = "1"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse the response - API returns a list of pages (subpages)
            if isinstance(data, list):
                pages = []
                for page_data in data:
                    try:
                        pages.append(TextTVPage.model_validate(page_data))
                    except Exception as e:
                        print(f"Error parsing subpage: {e}")
                return pages
            elif isinstance(data, dict):
                # Single page as dict (fallback)
                return [TextTVPage.model_validate(data)]
            else:
                print(f"Unexpected data format for page {page_number}")
                return []

        except httpx.HTTPError as e:
            print(f"HTTP error fetching page {page_number}: {e}")
            return []
        except Exception as e:
            print(f"Error parsing page {page_number}: {e}")
            return []

    async def get_page_range(
        self, start_page: str, end_page: str
    ) -> Dict[str, TextTVPage]:
        """Fetch multiple pages in a range in parallel.

        Args:
            start_page: Starting page number
            end_page: Ending page number

        Returns:
            Dictionary mapping page numbers to TextTVPage objects
        """
        start_num = int(start_page)
        end_num = int(end_page)

        # Create tasks for all pages
        page_numbers = [str(page_num) for page_num in range(start_num, end_num + 1)]
        tasks = [self.get_page(page_num) for page_num in page_numbers]

        # Fetch all pages concurrently
        pages = await asyncio.gather(*tasks)

        # Build results dictionary, filtering out None values
        results = {}
        for page_num, page in zip(page_numbers, pages):
            if page:
                results[page_num] = page

        return results

    def parse_from_file(self, file_path: str) -> Optional[TextTVPage]:
        """Parse TextTV data from a local JSON file.

        Expects texttv.nu API format: [{...}] or {...}

        Args:
            file_path: Path to the JSON file

        Returns:
            TextTVPage object or None if parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # API returns a list with one page
            if isinstance(data, list) and len(data) > 0:
                return TextTVPage.model_validate(data[0])
            elif isinstance(data, dict):
                return TextTVPage.model_validate(data)
            else:
                print(f"Unknown format in {file_path}")
                return None

        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None

    async def search_pages(
        self, query: str, page_range: tuple = (100, 199)
    ) -> Dict[str, TextTVPage]:
        """Search for pages containing specific text.

        Args:
            query: Text to search for
            page_range: Tuple of (start_page, end_page) to search in

        Returns:
            Dictionary of pages containing the query text
        """
        start_page, end_page = page_range
        all_pages = await self.get_page_range(str(start_page), str(end_page))

        matching_pages = {}
        query_lower = query.lower()

        for page_num, page in all_pages.items():
            clean_text = page.get_clean_text().lower()
            if query_lower in clean_text:
                matching_pages[page_num] = page

        return matching_pages


# Synchronous wrapper for simple usage
class SyncTextTVParser:
    """Synchronous wrapper for TextTVParser."""

    def __init__(self, base_url: str = "https://api.texttv.nu/api/get"):
        self.base_url = base_url

    def get_page(
        self,
        page_number: str,
        app: str = "texttv-parser",
        include_plain_text: bool = False,
    ) -> Optional[TextTVPage]:
        """Synchronously fetch a TextTV page.

        Args:
            page_number: Page number (e.g., "100", "150")
            app: Application identifier for the API
            include_plain_text: Include plain text content from API (sets includePlainTextContent=1)

        Returns:
            TextTVPage object or None if not found
        """

        async def _get_page():
            async with TextTVParser(self.base_url) as parser:
                return await parser.get_page(page_number, app, include_plain_text)

        return asyncio.run(_get_page())

    def parse_from_file(self, file_path: str) -> Optional[TextTVPage]:
        """Parse TextTV data from a local JSON file."""
        parser = TextTVParser(self.base_url)
        return parser.parse_from_file(file_path)
