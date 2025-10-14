"""Pydantic models for TextTV data structures."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup


class TextTVPage(BaseModel):
    """TextTV page from the texttv.nu API."""
    num: str = Field(..., description="Page number")
    title: str = Field(..., description="Page title")
    content: List[str] = Field(..., description="HTML content array")
    content_plain: List[str] = Field(default_factory=list, description="Plain text content from API (when includePlainTextContent=1)")
    next_page: Optional[str] = Field(None, description="Next page number")
    prev_page: Optional[str] = Field(None, description="Previous page number")
    date_updated_unix: int = Field(..., description="Unix timestamp")
    permalink: str = Field(..., description="Permalink URL")
    id: str = Field(..., description="Page ID")
    breadcrumbs: List = Field(default_factory=list, description="Navigation breadcrumbs")

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
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up the text
        lines = []
        for line in text.split('\n'):
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