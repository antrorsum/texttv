"""Advanced usage examples for TextTV Parser."""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from src.texttv_parser import TextTVParser, SyncTextTVParser
from src.texttv_parser.models import TextTVPage


def example_basic_file_parsing():
    """Basic example: Parse a local file."""
    print("=" * 60)
    print("Example 1: Basic File Parsing")
    print("=" * 60)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        print(f"✓ Successfully parsed page {page.num}")
        print(f"  Title: {page.title}")
        print(f"  Updated: {datetime.fromtimestamp(page.date_updated_unix)}")
        print(f"  Next page: {page.next_page}")
        print(f"  Content items: {len(page.content)}")
        print()
    else:
        print("✗ Failed to parse file")
    print()


def example_text_extraction():
    """Example: Extract and clean text."""
    print("=" * 60)
    print("Example 2: Text Extraction and Cleaning")
    print("=" * 60)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        # Show HTML content preview
        html_content = "".join(page.content)
        print(f"HTML content length: {len(html_content)} characters")
        print(f"HTML preview: '{html_content[:100]}...'")
        print()

        # Get cleaned content
        clean_text = page.get_clean_text()
        clean_lines = [line for line in clean_text.split("\n") if line]
        print(f"Cleaned content lines: {len(clean_lines)}")
        print(f"First clean line: '{clean_lines[0]}'")
        print()

        # Show comparison
        print("Full cleaned text:")
        print("-" * 60)
        print(clean_text)
        print("-" * 60)
    print()


def example_export_to_json():
    """Example: Export cleaned data to JSON."""
    print("=" * 60)
    print("Example 3: Export to JSON")
    print("=" * 60)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        output_data = {
            "metadata": {
                "page_number": page.num,
                "title": page.title,
                "updated": datetime.fromtimestamp(page.date_updated_unix).isoformat(),
                "next_page": page.next_page,
                "prev_page": page.prev_page,
                "exported_at": datetime.now().isoformat()
            },
            "content": {
                "cleaned_text": page.get_clean_text(),
                "word_count": len(page.get_clean_text().split()),
                "line_count": len([l for l in page.get_clean_text().split("\n") if l])
            }
        }

        output_file = "output_example.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported to {output_file}")
        print(f"  Word count: {output_data['content']['word_count']}")
        print(f"  Line count: {output_data['content']['line_count']}")
    print()


async def example_async_operations():
    """Example: Async operations for better performance."""
    print("=" * 60)
    print("Example 4: Async Operations")
    print("=" * 60)

    async with TextTVParser() as parser:
        # Parse from file (sync operation but in async context)
        page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

        if page:
            print(f"✓ Parsed page {page.num} asynchronously")

            # Simulate processing multiple pages
            print("\nSimulating batch processing...")
            tasks = []
            for i in range(3):
                # In real use, you'd fetch different pages
                print(f"  • Processing page simulation {i+1}/3")

            print("✓ Batch processing complete")
    print()


def example_content_analysis():
    """Example: Analyze content structure."""
    print("=" * 60)
    print("Example 5: Content Analysis")
    print("=" * 60)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        # Analyze HTML content
        html_content = "".join(page.content)
        print("Content analysis:")
        print(f"  • Total HTML length: {len(html_content)} characters")

        # Analyze cleaned text
        clean_text = page.get_clean_text()
        words = clean_text.split()
        lines = [l for l in clean_text.split("\n") if l]

        print(f"  • Cleaned text length: {len(clean_text)} characters")
        print(f"  • Word count: {len(words)}")
        print(f"  • Line count: {len(lines)}")
        print(f"  • Avg word length: {sum(len(w) for w in words) / len(words) if words else 0:.1f}")
        print(f"  • Avg line length: {sum(len(l) for l in lines) / len(lines) if lines else 0:.1f}")
    print()


def example_custom_processing():
    """Example: Custom text processing."""
    print("=" * 60)
    print("Example 6: Custom Processing")
    print("=" * 60)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        clean_text = page.get_clean_text()

        # Extract lines with numbers (page references)
        lines = clean_text.split("\n")
        ref_lines = [line for line in lines if any(c.isdigit() for c in line)]

        print(f"Lines with numbers: {len(ref_lines)}")
        for line in ref_lines[:5]:  # Show first 5
            print(f"  • {line}")

        print()

        # Find the longest words
        words = clean_text.split()
        long_words = sorted(set(words), key=len, reverse=True)[:5]

        print("Longest words:")
        for word in long_words:
            print(f"  • {word} ({len(word)} chars)")
    print()


def example_error_handling():
    """Example: Proper error handling."""
    print("=" * 60)
    print("Example 7: Error Handling")
    print("=" * 60)

    parser = SyncTextTVParser()

    # Try to parse non-existent file
    print("Attempting to parse non-existent file...")
    page = parser.parse_from_file("nonexistent.txt")

    if page is None:
        print("✓ Correctly handled missing file")
    else:
        print("✗ Unexpected result")

    # Parse valid file
    print("\nAttempting to parse valid file...")
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        print(f"✓ Successfully parsed page {page.num}")
        print(f"  Title: {page.title}")

        # Safe access to cleaned text
        try:
            clean_text = page.get_clean_text()
            print(f"  Text length: {len(clean_text)} characters")
        except Exception as e:
            print(f"✗ Error getting clean text: {e}")
    else:
        print("✗ Failed to parse valid file")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "TextTV Parser - Advanced Examples" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Run all examples
    example_basic_file_parsing()
    example_text_extraction()
    example_export_to_json()
    asyncio.run(example_async_operations())
    example_content_analysis()
    example_custom_processing()
    example_error_handling()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
