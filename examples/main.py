"""Main entry point for TextTV Parser demonstration."""

from pathlib import Path
from src.texttv_parser.parser import SyncTextTVParser


def main():
    """Demonstrate basic TextTV parsing functionality."""
    print("TextTV Parser - Sweden SVT TextTV API Parser")
    print("=" * 50)

    # Parse the sample file (in parent directory)
    index_file = Path(__file__).parent.parent / "index.txt"
    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(index_file))

    if page:
        from datetime import datetime
        print(f"\nParsed page: {page.num}")
        print(f"Title: {page.title}")
        print(f"Last updated: {datetime.fromtimestamp(page.date_updated_unix)}")
        print(f"Next page: {page.next_page}")
        print(f"Content items: {len(page.content)}")
        
        print("\n" + "="*50)
        print("CLEANED TEXT:")
        print("="*50)
        print(page.get_clean_text())
        
    else:
        print("Failed to parse sample file")
    
    print("\n" + "="*50)
    print("Usage examples:")
    print("  uv run texttv get-page 100")
    print("  uv run texttv parse-file ../index.txt --clean")
    print("  uv run texttv search 'klimat' --start 100 --end 110")


if __name__ == "__main__":
    main()
