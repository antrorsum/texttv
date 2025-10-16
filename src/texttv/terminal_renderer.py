"""Terminal renderer for TextTV pages with ANSI color support."""

from typing import Optional
from bs4 import BeautifulSoup


class TerminalRenderer:
    """Renders TextTV HTML content with ANSI colors for terminal display."""

    # ANSI color codes
    # Foreground colors
    FG_BLACK = '\033[30m'
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE = '\033[34m'
    FG_MAGENTA = '\033[35m'
    FG_CYAN = '\033[36m'
    FG_WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Styles
    BOLD = '\033[1m'
    RESET = '\033[0m'

    # TextTV class to ANSI mapping
    # Background colors (bg*)
    # Note: Bl = Black (two letters), B = Blue (single letter)
    BG_MAP = {
        'bgBl': BG_BLACK,     # Background Black (Bl = Black)
        'bgB': BG_BLUE,       # Background Blue (B = Blue)
        'bgW': BG_WHITE,      # Background White
        'bgR': BG_RED,        # Background Red
        'bgG': BG_GREEN,      # Background Green
        'bgY': BG_YELLOW,     # Background Yellow
        'bgC': BG_CYAN,       # Background Cyan
        'bgM': BG_MAGENTA,    # Background Magenta
    }

    # Foreground colors (single letter or lowercase combinations)
    FG_MAP = {
        'W': FG_WHITE,
        'Y': FG_YELLOW,
        'C': FG_CYAN,
        'R': FG_RED,
        'G': FG_GREEN,
        'B': FG_BLACK,
        'M': FG_MAGENTA,
        'bl': FG_BLUE,      # Blue foreground (lowercase)
    }

    def __init__(self, use_bold_for_double_height: bool = True):
        """Initialize the terminal renderer.

        Args:
            use_bold_for_double_height: Use bold text for double-height lines
        """
        self.use_bold_for_double_height = use_bold_for_double_height

    def _get_ansi_codes(self, classes: list[str]) -> str:
        """Convert CSS classes to ANSI color codes.

        Args:
            classes: List of CSS class names

        Returns:
            ANSI escape sequence string
        """
        codes = []

        # Check for background color
        for cls in classes:
            if cls in self.BG_MAP:
                codes.append(self.BG_MAP[cls])
                break

        # Check for foreground color
        for cls in classes:
            if cls in self.FG_MAP:
                codes.append(self.FG_MAP[cls])
                break

        # Check for double-height (DH)
        if self.use_bold_for_double_height and 'DH' in classes:
            codes.append(self.BOLD)

        return ''.join(codes)

    def render_html(self, html_content: str) -> str:
        """Render HTML content with ANSI colors.

        Args:
            html_content: HTML string from TextTV API

        Returns:
            Colored text string for terminal display
        """
        # Use 'lxml' parser to preserve whitespace (HTML parser collapses spaces)
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Find all line spans
        lines = soup.find_all('span', class_='line')

        output_lines = []
        for line_span in lines:
            line_text = self._render_line(line_span)
            output_lines.append(line_text)

        return '\n'.join(output_lines)

    def _render_line(self, line_span) -> str:
        """Render a single line span.

        Args:
            line_span: BeautifulSoup span element with class='line'

        Returns:
            Colored line string (exactly 40 characters wide)
        """
        import re

        result = []
        char_count = 0  # Track actual character count (without ANSI codes)
        last_bg_code = self.BG_BLACK  # Default background (TextTV standard black)

        # Process all child spans
        for span in line_span.find_all('span', recursive=False):
            classes = span.get('class', [])

            # Get ANSI codes for this span
            ansi_codes = self._get_ansi_codes(classes)

            # Remember the last background color for padding
            for cls in classes:
                if cls in self.BG_MAP:
                    last_bg_code = self.BG_MAP[cls]
                    break

            # Handle image spans (bgImg) - they're graphical elements
            if 'bgImg' in classes:
                # For images, use Unicode block character to represent graphics
                # These are custom 13x16 pixel GIF characters from TextTV
                # We use █ (full block) to show there's graphical content
                result.append(f"{ansi_codes}█{self.RESET}")
                char_count += 1
                continue

            # Get all text content in order, preserving links and spacing
            # Note: BeautifulSoup collapses multiple consecutive spaces to single space
            # This is a limitation of HTML parsing - proper fix would require custom parser
            text_parts = []
            for child in span.children:
                if isinstance(child, str):
                    # Direct text node
                    text_parts.append(child)
                elif child.name == 'a':
                    # Link - get its text
                    text_parts.append(child.get_text())
                else:
                    # Other tags - get their text recursively
                    text_parts.append(child.get_text())

            text = ''.join(text_parts)

            # IMPORTANT: Always append the text, even if it's just spaces
            # TextTV uses spaces for positioning and they must be preserved
            result.append(f"{ansi_codes}{text}{self.RESET}")
            char_count += len(text)

        # Pad the line to exactly 40 characters if needed
        # Use the last background color to maintain visual continuity
        if char_count < 40:
            padding = ' ' * (40 - char_count)
            result.append(f"{last_bg_code}{padding}{self.RESET}")

        return ''.join(result)

    def render_page(self, html_content: str, width: int = 80) -> str:
        """Render a complete TextTV page.

        Args:
            html_content: HTML string from TextTV API
            width: Terminal width (default 80)

        Returns:
            Colored page string ready for display
        """
        rendered = self.render_html(html_content)

        # Ensure lines don't exceed width
        # Note: This is tricky with ANSI codes, so we'll keep it simple for now
        return rendered
