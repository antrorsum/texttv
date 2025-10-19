"""TextTV Parser - A Python application to parse and clean data from Sweden SVT TextTV REST API."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parser import TextTVParser, SyncTextTVParser
from .models import TextTVPage

__all__ = ["TextTVParser", "SyncTextTVParser", "TextTVPage"]
