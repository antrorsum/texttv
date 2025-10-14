"""Command-line interface for TextTV Parser."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .parser import TextTVParser, SyncTextTVParser

app = typer.Typer(
    name="texttv",
    help="Parse and clean data from Sweden SVT TextTV REST API"
)
console = Console()


@app.command()
def get_page(
    page_number: str = typer.Argument(..., help="Page number (e.g., '100')"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save to file"),
    clean_only: bool = typer.Option(False, "--clean", "-c", help="Show only cleaned text"),
    plain_text: bool = typer.Option(False, "--plain-text", "-p", help="Show API plain text (requires includePlainTextContent=1)"),
    include_plain: bool = typer.Option(False, "--include-plain", help="Include plain text in API request (includePlainTextContent=1)"),
):
    """Fetch and display a TextTV page from texttv.nu API."""
    parser = SyncTextTVParser()

    with console.status(f"Fetching page {page_number}..."):
        page = parser.get_page(page_number, include_plain_text=include_plain)

    if not page:
        console.print(f"[red]Failed to fetch page {page_number}[/red]")
        raise typer.Exit(1)

    if plain_text:
        # Show API plain text
        api_plain = page.get_plain_text()
        if api_plain:
            console.print(Panel(api_plain, title=f"Page {page_number} - {page.title} (API Plain Text)"))
        else:
            console.print(f"[yellow]No plain text available. Use --include-plain to request it from API.[/yellow]")
    elif clean_only:
        text = page.get_clean_text()
        console.print(Panel(text, title=f"Page {page_number} - {page.title}"))
    else:
        # Display full page info
        from datetime import datetime
        table = Table(title=f"TextTV Page {page_number}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Title", page.title)
        table.add_row("Updated", datetime.fromtimestamp(page.date_updated_unix).strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Next Page", page.next_page or "N/A")
        table.add_row("Prev Page", page.prev_page or "N/A")

        # Show if plain text is available
        if page.get_plain_text():
            table.add_row("API Plain Text", "Available")

        console.print(table)
        console.print("\n")
        console.print(Panel(page.get_clean_text(), title="Cleaned Text"))

    if output:
        from datetime import datetime
        output_data = {
            "page_number": page_number,
            "title": page.title,
            "cleaned_text": page.get_clean_text(),
            "updated": datetime.fromtimestamp(page.date_updated_unix).isoformat(),
            "next_page": page.next_page,
            "prev_page": page.prev_page
        }

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]Saved to {output}[/green]")


@app.command()
def parse_file(
    file_path: Path = typer.Argument(..., help="Path to JSON file"),
    clean_only: bool = typer.Option(False, "--clean", "-c", help="Show only cleaned text"),
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
    
    if clean_only:
        console.print(page.get_clean_text())
    else:
        console.print(Panel(page.get_clean_text(), title=f"Page {page.num} - {page.title}"))


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
        highlighted_text = clean_text.replace(
            query.lower(), 
            f"[bold yellow]{query.lower()}[/bold yellow]"
        ).replace(
            query.upper(),
            f"[bold yellow]{query.upper()}[/bold yellow]"
        ).replace(
            query.capitalize(),
            f"[bold yellow]{query.capitalize()}[/bold yellow]"
        )
        
        console.print(Panel(
            highlighted_text,
            title=f"Page {page_num} - {page.title}",
            border_style="blue"
        ))
        console.print()


if __name__ == "__main__":
    app()