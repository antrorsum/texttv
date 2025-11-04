"""Command-line interface for TextTV Parser."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import readchar

from .parser import TextTVParser, SyncTextTVParser

app = typer.Typer(
    name="texttv",
    help="Parse and clean data from Sweden SVT TextTV REST API. Default: fetches page 100."
)
console = Console()


@app.command(name="get-page")
def get_page(
    page_number: str = typer.Argument("100", help="Page number to fetch"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save to file"),
    full: bool = typer.Option(
        False, "--full", "-f", help="Show full page info with table"
    ),
    plain_text: bool = typer.Option(
        False,
        "--plain-text",
        "-p",
        help="Show API plain text",
    ),
    include_plain: bool = typer.Option(
        False,
        "--include-plain",
        help="Include plain text in API request (auto-enabled with --plain-text)",
    ),
    colored: bool = typer.Option(
        False, "--colored", help="Show colored TextTV display with ANSI codes"
    ),
    compact: bool = typer.Option(
        False,
        "--compact",
        help="Show compact text (uppercase, limited charset, no padding)",
    ),
):
    """Fetch and display a TextTV page from texttv.nu API."""
    parser = SyncTextTVParser()

    # Auto-enable include_plain if plain_text is requested
    if plain_text and not include_plain:
        include_plain = True

    with console.status(f"Fetching page {page_number}..."):
        page = parser.get_page(page_number, include_plain_text=include_plain)

    if not page:
        console.print(f"[red]Failed to fetch page {page_number}[/red]")
        raise typer.Exit(1)

    if colored:
        # Show colored TextTV display
        colored_text = page.get_colored_text()
        # Use built-in print() to preserve ANSI codes (Rich escapes them)
        print(colored_text)
    elif compact:
        # Show compact text
        compact_text = page.get_compact_text()
        console.print(
            Panel(compact_text, title=f"Page {page_number} - {page.title} (Compact)")
        )
    elif plain_text:
        # Show API plain text
        api_plain = page.get_plain_text()
        if api_plain:
            console.print(
                Panel(
                    api_plain,
                    title=f"Page {page_number} - {page.title} (API Plain Text)",
                )
            )
        else:
            console.print(
                "[yellow]No plain text available.[/yellow]"
            )
    elif full:
        # Display full page info
        from datetime import datetime

        table = Table(title=f"TextTV Page {page_number}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Title", page.title)
        table.add_row(
            "Updated",
            datetime.fromtimestamp(page.date_updated_unix).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        table.add_row("Next Page", page.next_page or "N/A")
        table.add_row("Prev Page", page.prev_page or "N/A")

        # Show if plain text is available
        if page.get_plain_text():
            table.add_row("API Plain Text", "Available")

        console.print(table)
        console.print("\n")
        console.print(Panel(page.get_clean_text(), title="Cleaned Text"))
    else:
        # Default: show clean text only
        text = page.get_clean_text()
        console.print(Panel(text, title=f"Page {page_number} - {page.title}"))


    if output:
        from datetime import datetime

        output_data = {
            "page_number": page_number,
            "title": page.title,
            "cleaned_text": page.get_clean_text(),
            "updated": datetime.fromtimestamp(page.date_updated_unix).isoformat(),
            "next_page": page.next_page,
            "prev_page": page.prev_page,
        }

        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]Saved to {output}[/green]")


@app.command()
def parse_file(
    file_path: Path = typer.Argument(..., help="Path to JSON file"),
    clean_only: bool = typer.Option(
        False, "--clean", "-c", help="Show only cleaned text"
    ),
    colored: bool = typer.Option(
        False, "--colored", help="Show colored TextTV display with ANSI codes"
    ),
    compact: bool = typer.Option(
        False,
        "--compact",
        help="Show compact text (uppercase, limited charset, no padding)",
    ),
):
    """Parse TextTV data from a local JSON file."""
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    parser = SyncTextTVParser()
    page = parser.parse_from_file(str(file_path))

    if not page:
        console.print(f"[red]Failed to parse file: {file_path}[/red]")
        raise typer.Exit(1)

    if colored:
        # Show colored TextTV display
        colored_text = page.get_colored_text()
        # Use built-in print() to preserve ANSI codes (Rich escapes them)
        print(colored_text)
    elif compact:
        # Show compact text
        compact_text = page.get_compact_text()
        console.print(
            Panel(compact_text, title=f"Page {page.num} - {page.title} (Compact)")
        )
    elif clean_only:
        console.print(page.get_clean_text())
    else:
        console.print(
            Panel(page.get_clean_text(), title=f"Page {page.num} - {page.title}")
        )


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    start_page: int = typer.Option(100, "--start", help="Start page number"),
    end_page: int = typer.Option(199, "--end", help="End page number"),
):
    """Search for text across multiple TextTV pages."""

    async def _search():
        async with TextTVParser() as parser:
            with console.status(f"Searching pages {start_page}-{end_page}..."):
                results = await parser.search_pages(query, (start_page, end_page))
            return results

    results = asyncio.run(_search())

    if not results:
        console.print(f"[yellow]No results found for '{query}'[/yellow]")
        return

    console.print(f"[green]Found {len(results)} pages containing '{query}'[/green]\n")

    for page_num, page in results.items():
        clean_text = page.get_clean_text()
        # Highlight the search term
        highlighted_text = (
            clean_text.replace(
                query.lower(), f"[bold yellow]{query.lower()}[/bold yellow]"
            )
            .replace(query.upper(), f"[bold yellow]{query.upper()}[/bold yellow]")
            .replace(
                query.capitalize(), f"[bold yellow]{query.capitalize()}[/bold yellow]"
            )
        )

        console.print(
            Panel(
                highlighted_text,
                title=f"Page {page_num} - {page.title}",
                border_style="blue",
            )
        )
        console.print()


@app.command()
def browse(
    start_page: str = typer.Argument("100", help="Starting page number"),
):
    """Interactive TextTV browser with arrow key navigation.

    Navigation:
    - Left/Right arrows: Change page number
    - Up/Down arrows: Navigate subpages
    - q: Quit
    """

    def clear_screen():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_page(page, page_num, subpage_idx):
        """Display a single subpage with navigation info."""
        clear_screen()

        if not page:
            print(f"Page {page_num} not found or empty")
            print("\n[←/→] Page  [↑/↓] Subpage  [q] Quit")
            return

        # Get total subpages count
        total_subpages = page.get_subpage_count()

        # Display colored TextTV output for the specific subpage
        colored_text = page.get_colored_text(subpage_index=subpage_idx)
        print(colored_text)

        # Display navigation info
        subpage_info = f" (subpage {subpage_idx + 1}/{total_subpages})" if total_subpages > 1 else ""
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Page {page_num}{subpage_info}")
        print(f"[←/→] Page  [↑/↓] Subpage  [q] Quit")

    async def browse_loop(start_page_num):
        """Main browsing loop."""
        current_page = int(start_page_num)
        current_subpage = 0

        async with TextTVParser() as parser:
            # Fetch initial page
            page = await parser.get_page(str(current_page))
            display_page(page, current_page, current_subpage)

            while True:
                try:
                    # Read key input
                    key = readchar.readkey()

                    # Handle quit
                    if key.lower() == 'q':
                        break

                    # Handle arrow keys
                    if key == readchar.key.LEFT:
                        # Previous page
                        if current_page > 100:
                            current_page -= 1
                            current_subpage = 0
                            page = await parser.get_page(str(current_page))
                            display_page(page, current_page, current_subpage)

                    elif key == readchar.key.RIGHT:
                        # Next page
                        if current_page < 999:
                            current_page += 1
                            current_subpage = 0
                            page = await parser.get_page(str(current_page))
                            display_page(page, current_page, current_subpage)

                    elif key == readchar.key.UP:
                        # Previous subpage (within content array)
                        if page and current_subpage > 0:
                            current_subpage -= 1
                            display_page(page, current_page, current_subpage)

                    elif key == readchar.key.DOWN:
                        # Next subpage (within content array)
                        if page:
                            total_subpages = page.get_subpage_count()
                            if current_subpage < total_subpages - 1:
                                current_subpage += 1
                                display_page(page, current_page, current_subpage)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    # Show error but continue
                    print(f"\nError: {e}")
                    print("Press any key to continue...")
                    readchar.readkey()
                    display_page(page, current_page, current_subpage)

        # Clear screen on exit
        clear_screen()
        console.print("[green]Exited TextTV browser[/green]")

    # Run the async browse loop
    asyncio.run(browse_loop(start_page))


def cli():
    """Main CLI entry point."""
    import sys

    # Don't insert default command if --help is present
    if '--help' not in sys.argv and '-h' not in sys.argv:
        # If no command is given (only options or just 'texttv'), default to get-page
        if len(sys.argv) == 1 or (len(sys.argv) > 1 and not any(arg in ['get-page', 'parse-file', 'search', 'browse'] for arg in sys.argv)):
            # Check if first non-option arg looks like a page number or if it's just options
            has_subcommand = any(arg in ['get-page', 'parse-file', 'search', 'browse'] for arg in sys.argv[1:])
            if not has_subcommand:
                # Insert 'get-page' as the command
                sys.argv.insert(1, 'get-page')

    app()


if __name__ == "__main__":
    cli()
