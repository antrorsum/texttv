"""Pydantic models for TextTV data structures."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import re


class TextTVPage(BaseModel):
    """TextTV page from the texttv.nu API."""
    num: str = Field(..., description="Page number")
    title: str = Field(..., description="Page title")
    content: List[str] = Field(..., description="HTML content array")
    content_plain: List[str] = Field(default_factory=list, description="Plain text content")
    next_page: Optional[str] = Field(None, description="Next page number")
    prev_page: Optional[str] = Field(None, description="Previous page number")
    date_updated_unix: int = Field(..., description="Unix timestamp")
    permalink: str = Field(..., description="Permalink URL")
    id: str = Field(..., description="Page ID")
    breadcrumbs: List = Field(default_factory=list, description="Navigation breadcrumbs")
    
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
                if re.match(r'^\d{3}$', line):  # Skip lone page numbers
                    continue
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