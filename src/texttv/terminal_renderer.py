"""Terminal renderer for TextTV pages with ANSI color support.

This module converts TextTV HTML content to ANSI-colored terminal output,
preserving the authentic teletext display format (40 columns × 24 rows).

Key Features:
- Preserves exact whitespace and spacing using non-breaking space placeholders
- Maps TextTV CSS classes to ANSI color codes (both standard and bright variants)
- Handles B/bl color distinction (B=Blue, bl=Black)
- Auto-matches foreground to background for solid color blocks (bgImg)
- Supports Unicode mosaic characters (U+1FB00-U+1FB3B) for graphics
- Uses standard red (not bright) for weather maps and other displays

Color System:
- Background classes: bgBl (Black), bgB (Blue), bgW (White), bgR (Red), etc.
- Foreground classes: W (White), Y (Yellow), C (Cyan), R (Red), B (Blue), bl (Black)
- CRITICAL: "B" (capital, 1 letter) = Blue foreground
            "bl" (lowercase, 2 letters) = Black foreground
            "Bl" in "bgBl" (2 letters) = Black background
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


class TerminalRenderer:
    """Renders TextTV HTML content with ANSI colors for terminal display.

    This renderer handles all the special requirements of TextTV formatting:

    1. Whitespace Preservation:
       - HTML parsers collapse multiple spaces to single space
       - Solution: Replace spaces with non-breaking space (U+00A0) before parsing
       - Restore spaces after rendering

    2. Color Mapping:
       - TextTV uses CSS classes like "bgBl", "bgB", "W", "Y", "B", "bl"
       - Maps to ANSI codes (standard 30-37/40-47 or bright 90-97/100-107)
       - CRITICAL: "B" (capital) = Blue FG, "bl" (lowercase) = Black FG
       - Exception: Red uses standard (31/41) not bright (91/101) for weather maps

    3. Solid Color Blocks:
       - bgImg spans with only background color need matching foreground
       - Auto-sets foreground to match background to prevent white blocks
       - Example: bgR alone gets R foreground for solid red blocks

    4. Graphics:
       - Uses Unicode mosaic characters (U+1FB00-U+1FB3B) for teletext graphics
       - Maps GIF IDs to appropriate characters via gif_char_mapping.json
       - Fallback to full block (█) if no mapping found
    """

    # ANSI color codes
    # Foreground colors (standard)
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"

    # Foreground colors (bright variants)
    FG_BRIGHT_BLACK = "\033[90m"
    FG_BRIGHT_RED = "\033[91m"
    FG_BRIGHT_GREEN = "\033[92m"
    FG_BRIGHT_YELLOW = "\033[93m"
    FG_BRIGHT_BLUE = "\033[94m"
    FG_BRIGHT_MAGENTA = "\033[95m"
    FG_BRIGHT_CYAN = "\033[96m"
    FG_BRIGHT_WHITE = "\033[97m"

    # Background colors (standard)
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Background colors (bright variants)
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    # Styles
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # TextTV class to ANSI mapping
    # Background colors (bg*)
    # Note: Bl = Black (two letters), B = Blue (single letter)
    BG_MAP = {
        "bgBl": BG_BLACK,  # Background Black (Bl = Black)
        "bgB": BG_BLUE,  # Background Blue (B = Blue)
        "bgW": BG_WHITE,  # Background White
        "bgR": BG_RED,  # Background Red
        "bgG": BG_GREEN,  # Background Green
        "bgY": BG_YELLOW,  # Background Yellow
        "bgC": BG_CYAN,  # Background Cyan
        "bgM": BG_MAGENTA,  # Background Magenta
    }

    # Foreground colors (single letter or lowercase combinations)
    # CRITICAL: "B" (capital) = Blue, "bl" (lowercase) = Black
    FG_MAP = {
        "W": FG_WHITE,
        "Y": FG_YELLOW,
        "C": FG_CYAN,
        "R": FG_RED,
        "G": FG_GREEN,
        "B": FG_BLUE,  # Blue foreground (capital B)
        "M": FG_MAGENTA,
        "bl": FG_BLACK,  # Black foreground (lowercase bl)
    }

    def __init__(self, use_bold_for_double_height: bool = True, use_bright_colors: bool = True):
        """Initialize the terminal renderer.

        Args:
            use_bold_for_double_height: Use bold text for double-height (DH) lines
            use_bright_colors: Use bright ANSI variants (90-97, 100-107) for better visibility.
                             Note: Red always uses standard (31/41) regardless of this setting,
                             as weather maps require darker red for proper display.
        """
        self.use_bold_for_double_height = use_bold_for_double_height
        self.use_bright_colors = use_bright_colors

        # Load GIF character mapping
        mapping_path = Path(__file__).parent.parent.parent / "gif_char_mapping.json"
        if mapping_path.exists():
            with open(mapping_path) as f:
                self.gif_char_mapping = json.load(f)
        else:
            # Fallback to simple mapping if file doesn't exist
            self.gif_char_mapping = {}

        # Set up color mappings based on brightness preference
        if use_bright_colors:
            self._setup_bright_color_maps()
        else:
            self._setup_standard_color_maps()

    def _setup_standard_color_maps(self):
        """Setup standard ANSI color maps (30-37, 40-47).

        Uses standard ANSI colors for all TextTV classes.
        Good for terminals with custom color schemes.
        """
        self.bg_map_values = {
            "bgBl": self.BG_BLACK,
            "bgB": self.BG_BLUE,
            "bgW": self.BG_WHITE,
            "bgR": self.BG_RED,
            "bgG": self.BG_GREEN,
            "bgY": self.BG_YELLOW,
            "bgC": self.BG_CYAN,
            "bgM": self.BG_MAGENTA,
        }
        self.fg_map_values = {
            "W": self.FG_WHITE,
            "Y": self.FG_YELLOW,
            "C": self.FG_CYAN,
            "R": self.FG_RED,
            "G": self.FG_GREEN,
            "B": self.FG_BLUE,
            "M": self.FG_MAGENTA,
            "bl": self.FG_BLACK,
        }

    def _setup_bright_color_maps(self):
        """Setup bright ANSI color maps (90-97, 100-107) for better visibility.

        Uses bright ANSI colors for most TextTV classes to improve readability.
        Exception: Red uses standard (31/41) not bright (91/101) as weather maps
        and other pages need darker red for proper color representation.
        """
        self.bg_map_values = {
            "bgBl": self.BG_BLACK,  # Keep black as standard (bright black looks gray)
            "bgB": self.BG_BRIGHT_BLUE,
            "bgW": self.BG_BRIGHT_WHITE,
            "bgR": self.BG_RED,  # Use standard red (not bright) - weather maps need darker red
            "bgG": self.BG_BRIGHT_GREEN,
            "bgY": self.BG_BRIGHT_YELLOW,
            "bgC": self.BG_BRIGHT_CYAN,
            "bgM": self.BG_BRIGHT_MAGENTA,
        }
        self.fg_map_values = {
            "W": self.FG_BRIGHT_WHITE,
            "Y": self.FG_BRIGHT_YELLOW,
            "C": self.FG_BRIGHT_CYAN,
            "R": self.FG_RED,  # Use standard red (not bright) - weather maps need darker red
            "G": self.FG_BRIGHT_GREEN,
            "B": self.FG_BRIGHT_BLUE,
            "M": self.FG_BRIGHT_MAGENTA,
            "bl": self.FG_BLACK,  # Keep black as standard
        }

    def _get_ansi_codes(self, classes: list[str]) -> str:
        """Convert CSS classes to ANSI color codes.

        Handles TextTV CSS classes and converts them to appropriate ANSI codes:
        - Background classes (bgBl, bgB, bgW, bgR, etc.) → background colors
        - Foreground classes (W, Y, C, R, B, bl) → foreground colors
        - Double-height (DH) → bold text (if enabled)
        - Solid color blocks: Auto-matches foreground to background for bgImg

        Args:
            classes: List of CSS class names from TextTV HTML

        Returns:
            ANSI escape sequence string (e.g., "\\033[41m\\033[91m" for red bg+fg)
        """
        codes = []
        bg_color = None
        fg_color = None

        # Check for background color
        for cls in classes:
            if cls in self.bg_map_values:
                bg_color = cls
                codes.append(self.bg_map_values[cls])
                break

        # Check for foreground color
        for cls in classes:
            if cls in self.fg_map_values:
                fg_color = cls
                codes.append(self.fg_map_values[cls])
                break

        # IMPORTANT: For bgImg spans with only background color (no foreground),
        # set foreground to match background for solid color blocks
        # This prevents white blocks appearing instead of colored blocks
        if "bgImg" in classes and bg_color and not fg_color:
            # Map background color to matching foreground color
            bg_to_fg_map = {
                "bgR": "R",
                "bgB": "B",
                "bgG": "G",
                "bgY": "Y",
                "bgC": "C",
                "bgM": "M",
                "bgW": "W",
                "bgBl": "bl",
            }
            if bg_color in bg_to_fg_map:
                matching_fg = bg_to_fg_map[bg_color]
                if matching_fg in self.fg_map_values:
                    codes.append(self.fg_map_values[matching_fg])

        # Check for double-height (DH)
        if self.use_bold_for_double_height and "DH" in classes:
            codes.append(self.BOLD)

        return "".join(codes)

    def render_html(self, html_content: str) -> str:
        """Render HTML content with ANSI colors.

        CRITICAL: Preserves exact whitespace using non-breaking space placeholders.
        HTML parsers (including lxml) collapse multiple consecutive spaces to single
        space, which breaks TextTV formatting. This method replaces spaces with
        non-breaking space (U+00A0) before parsing, then restores them after rendering.

        Args:
            html_content: HTML string from TextTV API (contains div with span.line elements)

        Returns:
            Colored text string for terminal display with ANSI escape codes
        """
        # CRITICAL: HTML parsers collapse multiple consecutive spaces to single space
        # To preserve TextTV's exact spacing, we replace spaces with a placeholder
        # before parsing, then restore them after extracting text
        # Use non-breaking space (U+00A0) which HTML parsers preserve
        SPACE_PLACEHOLDER = "\u00A0"  # Non-breaking space

        # Replace all spaces in text content (but not in attributes) with placeholder
        # This regex matches spaces that are NOT inside HTML tags
        import re
        html_preserved = re.sub(r'>([^<]*)<',
                                lambda m: '>' + m.group(1).replace(' ', SPACE_PLACEHOLDER) + '<',
                                html_content)

        # Use 'lxml' parser
        soup = BeautifulSoup(html_preserved, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Find all line spans
        lines = soup.find_all("span", class_="line")

        output_lines = []
        for line_span in lines:
            line_text = self._render_line(line_span)
            output_lines.append(line_text)

        return "\n".join(output_lines)

    def _render_line(self, line_span) -> str:
        """Render a single line span with ANSI colors.

        Processes all child spans in the line, applying colors and handling:
        - Regular text spans with foreground/background colors
        - bgImg spans for graphics (uses Unicode mosaic characters)
        - Whitespace preservation (spaces are already non-breaking space placeholders)
        - Line padding to exactly 40 characters using last background color

        Args:
            line_span: BeautifulSoup span element with class='line'

        Returns:
            Colored line string (exactly 40 characters wide with ANSI escape codes)
        """
        SPACE_PLACEHOLDER = "\u00A0"  # Must match the placeholder in render_html (non-breaking space)

        result = []
        char_count = 0  # Track actual character count (without ANSI codes)
        last_bg_code = self.BG_BLACK  # Default background (TextTV standard black)

        # Process all child spans
        for span in line_span.find_all("span", recursive=False):
            classes = span.get("class", [])

            # Get ANSI codes for this span
            ansi_codes = self._get_ansi_codes(classes)

            # Remember the last background color for padding
            for cls in classes:
                if cls in self.bg_map_values:
                    last_bg_code = self.bg_map_values[cls]
                    break

            # Handle image spans (bgImg) - they're graphical elements
            if "bgImg" in classes:
                # Extract GIF ID from style attribute
                style = span.get("style", "")
                gif_id_match = re.search(r'chars/(\d+)\.gif', style)

                if gif_id_match and gif_id_match.group(1) in self.gif_char_mapping:
                    # Use mapped character for this specific GIF
                    char = self.gif_char_mapping[gif_id_match.group(1)]

                    # NOTE: Now using teletext mosaic characters (U+1FB00-U+1FB3B) from our
                    # mapping. These are designed to work with background colors - they show
                    # both the character pattern AND let the background show through.
                    # No conversion needed!
                else:
                    # Fallback to full block if no mapping found
                    char = "█"

                result.append(f"{ansi_codes}{char}{self.RESET}")
                char_count += 1
                continue

            # Get all text content in order, preserving links and spacing
            # NOTE: Spaces are preserved as \x00 placeholders from render_html
            text_parts = []
            for child in span.children:
                if isinstance(child, str):
                    # Direct text node
                    text_parts.append(child)
                elif child.name == "a":
                    # Link - get its text
                    text_parts.append(child.get_text())
                else:
                    # Other tags - get their text recursively
                    text_parts.append(child.get_text())

            text = "".join(text_parts)

            # IMPORTANT: Always append the text, even if it's just spaces (as \x00)
            # TextTV uses spaces for positioning and they must be preserved
            result.append(f"{ansi_codes}{text}{self.RESET}")
            char_count += len(text)  # \x00 counts as 1 character, same as space

        # Pad the line to exactly 40 characters if needed
        # Use the last background color to maintain visual continuity
        if char_count < 40:
            padding = SPACE_PLACEHOLDER * (40 - char_count)
            result.append(f"{last_bg_code}{padding}{self.RESET}")

        # Restore ALL space placeholders to actual spaces
        line_result = "".join(result)
        line_result = line_result.replace(SPACE_PLACEHOLDER, " ")

        return line_result

    def render_page(self, html_content: str, width: int = 80) -> str:
        """Render a complete TextTV page with ANSI colors.

        This is a convenience method that calls render_html(). The width parameter
        is currently unused as TextTV pages are fixed at 40 characters wide.

        Args:
            html_content: HTML string from TextTV API
            width: Terminal width (default 80, currently unused)

        Returns:
            Colored page string ready for terminal display (40 chars × 24 lines)
        """
        rendered = self.render_html(html_content)

        # Ensure lines don't exceed width
        # Note: This is tricky with ANSI codes, so we'll keep it simple for now
        return rendered
