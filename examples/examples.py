"""Example scripts demonstrating TextTV Parser usage."""

import asyncio
from pathlib import Path
from src.texttv_parser import TextTVParser, SyncTextTVParser


def example_sync_usage():
    """Example of synchronous API usage."""
    print("=== Synchronous API Example ===\n")

    # Create parser
    parser = SyncTextTVParser()

    # Parse from file
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))
    if page:
        print(f"Page: {page.num}")
        print(f"Title: {page.title}")
        print(f"\nCleaned text:\n{page.get_clean_text()}\n")


async def example_async_usage():
    """Example of asynchronous API usage."""
    print("=== Asynchronous API Example ===\n")

    async with TextTVParser() as parser:
        # Parse from file (also works async)
        page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))
        if page:
            print(f"Page: {page.num}")
            print(f"Title: {page.title}")
            print(f"Content items: {len(page.content)}")
            print(f"\nCleaned text:\n{page.get_clean_text()}\n")


async def example_batch_fetching():
    """Example of fetching multiple pages."""
    print("=== Batch Fetching Example ===\n")
    print("Note: This requires actual API access\n")
    
    # Example code (would need actual API endpoint):
    # async with TextTVParser() as parser:
    #     # Fetch multiple pages
    #     pages = await parser.get_page_range("100", "105")
    #     
    #     for page_num, page in pages.items():
    #         print(f"Page {page_num}: {page.title}")
    #         print(f"  {page.get_clean_text()[:100]}...")
    #         print()


def main():
    """Run all examples."""
    # Synchronous example
    example_sync_usage()
    
    # Asynchronous example
    asyncio.run(example_async_usage())
    
    # Batch fetching example
    asyncio.run(example_batch_fetching())


if __name__ == "__main__":
    main()
