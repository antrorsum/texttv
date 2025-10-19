"""Pydantic models for TextTV data structures."""

from typing import List, Optional
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from .terminal_renderer import TerminalRenderer


class TextTVPage(BaseModel):
    """TextTV page from the texttv.nu API."""

    num: str = Field(..., description="Page number")
    title: str = Field(..., description="Page title")
    content: List[str] = Field(..., description="HTML content array")
    content_plain: List[str] = Field(
        default_factory=list,
        description="Plain text content from API (when includePlainTextContent=1)",
    )
    next_page: Optional[str] = Field(None, description="Next page number")
    prev_page: Optional[str] = Field(None, description="Previous page number")
    date_updated_unix: int = Field(..., description="Unix timestamp")
    permalink: str = Field(..., description="Permalink URL")
    id: str = Field(..., description="Page ID")
    breadcrumbs: List = Field(
        default_factory=list, description="Navigation breadcrumbs"
    )

    def get_plain_text(self) -> Optional[str]:
        """Get plain text content from API if available.

        This returns the plain text provided by the API when using
        includePlainTextContent=1 parameter. Returns None if not available.

        Returns:
            Plain text string or None if content_plain is empty
        """
        if not self.content_plain:
            return None
        return "\n".join(self.content_plain).strip()

    def get_clean_text(self) -> str:
        """Extract and clean text from HTML content."""
        if not self.content:
            return ""

        # Parse HTML content
        html_content = "".join(self.content)
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up the text
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                # Skip common navigation patterns
                # Note: We don't skip 3-digit numbers anymore as they are reference links
                if "SVT Text" in line and "toprow" in html_content:
                    continue
                lines.append(line)

        # Remove duplicate consecutive lines
        cleaned_lines = []
        prev_line = None
        for line in lines:
            if line != prev_line:
                cleaned_lines.append(line)
            prev_line = line

        return "\n".join(cleaned_lines).strip()

    def get_colored_text(self, use_bold: bool = True) -> str:
        """Get colored terminal output with ANSI codes.

        This renders the TextTV page as it would appear on a real TextTV display,
        with colored backgrounds and text using ANSI escape sequences.

        Args:
            use_bold: Use bold text for double-height headings

        Returns:
            Colored text string with ANSI escape codes for terminal display
        """
        if not self.content:
            return ""

        renderer = TerminalRenderer(use_bold_for_double_height=use_bold)
        html_content = "".join(self.content)
        return renderer.render_html(html_content)

    def get_compact_text(self) -> str:
        r"""Get compact text with limited character set for efficient transmission.

        Supports:
        - Uppercase letters A-Z
        - Numbers 0-9
        - Space
        - Common punctuation: ./?+-`~!@#$%^&*()_=[]\{}|;':",&<>
        - Extended Latin-1: ¡¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ
          (includes Swedish Å, Ä, Ö)

        This method:
        1. Starts with clean text (get_clean_text())
        2. Converts to uppercase
        3. Replaces unsupported characters with safe alternatives
        4. Removes padding/duplicates for compact transmission

        Returns:
            Compact text string (uppercase, limited character set)
        """
        # Start with clean text
        text = self.get_clean_text()
        if not text:
            return ""

        # Define JS8Call supported character set
        # Based on JS8Call documentation: uppercase ASCII, numbers, punctuation, Latin-1 extended
        js8call_chars = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
            r" ./?+-`~!@#$%^&*()_=[]\{}|;:'\"&<>,"
            "¡¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
        )

        # Character mapping for common Swedish characters (lowercase to uppercase)
        char_map = {
            "å": "Å",
            "ä": "Ä",
            "ö": "Ö",
            "à": "À",
            "á": "Á",
            "â": "Â",
            "ã": "Ã",
            "æ": "Æ",
            "ç": "Ç",
            "è": "È",
            "é": "É",
            "ê": "Ê",
            "ë": "Ë",
            "ì": "Ì",
            "í": "Í",
            "î": "Î",
            "ï": "Ï",
            "ð": "Ð",
            "ñ": "Ñ",
            "ò": "Ò",
            "ó": "Ó",
            "ô": "Ô",
            "õ": "Õ",
            "ø": "Ø",
            "ù": "Ù",
            "ú": "Ú",
            "û": "Û",
            "ü": "Ü",
            "ý": "Ý",
            "þ": "Þ",
            # Common replacements for unsupported characters
            "\u2013": "-",  # en dash to hyphen
            "\u2014": "-",  # em dash to hyphen
            "\u201c": '"',  # left double quote to straight quote
            "\u201d": '"',  # right double quote to straight quote
            "\u2018": "'",  # left single quote to apostrophe
            "\u2019": "'",  # right single quote to apostrophe
            "\u2026": "...",  # horizontal ellipsis to three periods
        }

        # Process text
        result_lines = []
        for line in text.split("\n"):
            # First apply character mapping
            processed_line = ""
            for char in line:
                # Map special characters
                if char in char_map:
                    processed_line += char_map[char]
                else:
                    processed_line += char

            # Convert to uppercase
            processed_line = processed_line.upper()

            # Filter to only JS8Call-supported characters
            filtered_line = ""
            for char in processed_line:
                if char in js8call_chars:
                    filtered_line += char
                # If character not supported, skip it (already removed dashes, quotes, etc. in mapping)

            # Only add non-empty lines
            if filtered_line.strip():
                result_lines.append(filtered_line.strip())

        # Always apply compact mode
        result_lines = self._compact_lines(result_lines)

        return "\n".join(result_lines)

    def _compact_lines(self, lines: list[str]) -> list[str]:
        """Remove padding characters from text for compact transmission.

        Removes:
        - Multiple consecutive spaces (keeps single space)
        - Repeated padding dots (e.g., "..." becomes ".")
        - Repeated padding dashes/hyphens

        Preserves:
        - All letters and numbers (content)
        - Single spaces between words
        - Punctuation that's part of content

        Args:
            lines: List of text lines to compact

        Returns:
            Compacted lines with padding removed
        """
        import re

        compacted = []
        for line in lines:
            # Replace multiple consecutive spaces with single space
            line = re.sub(r" {2,}", " ", line)

            # Replace multiple consecutive dots with single dot (padding removal)
            # But keep intentional ellipsis (already converted from …)
            line = re.sub(r"\.{2,}", ".", line)

            # Replace multiple consecutive hyphens/dashes with single dash
            line = re.sub(r"-{2,}", "-", line)

            # Remove trailing/leading padding characters
            line = line.strip(" .-")

            if line:
                compacted.append(line)

        return compacted
