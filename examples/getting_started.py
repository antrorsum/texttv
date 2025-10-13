#!/usr/bin/env python3
"""
TextTV Parser - Interactive Getting Started Guide

Run this script to explore the TextTV Parser features interactively.
"""

import sys
from pathlib import Path
from datetime import datetime
from texttv import SyncTextTVParser


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    """Print a section header."""
    print(f"\n→ {text}")
    print("-" * 70)


def demo_basic_parsing():
    """Demonstrate basic parsing."""
    print_header("1. BASIC PARSING")

    print_section("Parsing the sample index.txt file...")

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        print(f"✓ Page Number: {page.num}")
        print(f"✓ Title: {page.title}")
        print(f"✓ Updated: {datetime.fromtimestamp(page.date_updated_unix)}")
        print(f"✓ Next Page: {page.next_page}")
        print(f"✓ Content Items: {len(page.content)}")
    else:
        print("✗ Failed to parse file")
        return False

    return True


def demo_text_cleaning():
    """Demonstrate text cleaning."""
    print_header("2. TEXT CLEANING")

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

    if page:
        print_section("HTML content preview:")
        html_preview = page.content[0][:200] if page.content else ""
        print(f"  '{html_preview}...'")

        print_section("Cleaned text:")
        clean_text = page.get_clean_text()
        print(clean_text)

        print_section("Statistics:")
        words = clean_text.split()
        lines = [l for l in clean_text.split("\n") if l]
        print(f"  • Words: {len(words)}")
        print(f"  • Lines: {len(lines)}")
        print(f"  • Characters: {len(clean_text)}")


def demo_cli_commands():
    """Show available CLI commands."""
    print_header("3. CLI COMMANDS")

    commands = [
        ("Parse a file", "uv run texttv parse-file ../index.txt"),
        ("Show clean text only", "uv run texttv parse-file ../index.txt --clean"),
        ("Get help", "uv run texttv --help"),
        ("Fetch live page", "uv run texttv get-page 100"),
        ("Search pages", "uv run texttv search 'klimat' --start 100 --end 110"),
    ]

    print_section("Available commands:")
    for desc, cmd in commands:
        print(f"\n  {desc}:")
        print(f"    $ {cmd}")


def demo_python_api():
    """Show Python API usage."""
    print_header("4. PYTHON API")

    print_section("Synchronous Usage:")
    print("""
from texttv import SyncTextTVParser

parser = SyncTextTVParser()
page = parser.parse_from_file(str(Path(__file__).parent.parent / "index.txt"))

if page:
    print(f"Title: {page.title}")
    print(page.get_clean_text())
""")

    print_section("Asynchronous Usage:")
    print("""
import asyncio
from texttv import TextTVParser

async def main():
    async with TextTVParser() as parser:
        page = await parser.get_page("100")
        print(page.get_clean_text())

asyncio.run(main())
""")


def demo_examples():
    """Show available examples."""
    print_header("5. EXAMPLE SCRIPTS")

    examples = [
        ("main.py", "Basic demo with sample data", "uv run python examples/main.py"),
        ("examples.py", "Sync and async usage patterns", "uv run python examples/examples.py"),
        ("advanced_examples.py", "7 advanced examples", "uv run python examples/advanced_examples.py"),
    ]

    print_section("Try these examples:")
    for filename, description, command in examples:
        print(f"\n  {filename}: {description}")
        print(f"    $ {command}")


def demo_documentation():
    """Show documentation files."""
    print_header("6. DOCUMENTATION")

    docs = [
        ("README.md", "Main documentation with features and usage"),
        ("QUICKSTART.md", "Step-by-step quick start guide"),
        ("DEVELOPMENT.md", "Architecture and development notes"),
        ("PROJECT_SUMMARY.md", "Comprehensive project overview"),
    ]

    print_section("Read the docs:")
    for filename, description in docs:
        print(f"  • {filename}: {description}")


def main():
    """Run the interactive guide."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Welcome to TextTV Parser!" + " " * 28 + "║")
    print("║" + " " * 12 + "Sweden SVT TextTV REST API Parser" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run demonstrations
    if not demo_basic_parsing():
        print("\n✗ Error: Could not parse sample file. Make sure index.txt exists.")
        sys.exit(1)

    demo_text_cleaning()
    demo_cli_commands()
    demo_python_api()
    demo_examples()
    demo_documentation()

    # Final message
    print_header("NEXT STEPS")
    print("""
  1. Try the CLI commands above
  2. Run the example scripts
  3. Read the documentation
  4. Explore the source code in src/texttv/
  5. Run the tests: uv run pytest
  6. Build your own TextTV applications!

  Questions? Check README.md or QUICKSTART.md

  Happy parsing! 🎉
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
