#!/usr/bin/env python3
"""
Download and parse real TextTV data from texttv.nu API

Usage:
    uv run python fetch_real_data.py 100
    uv run python fetch_real_data.py 150 --save
"""

import sys
import json
import httpx
from datetime import datetime
from pathlib import Path
from texttv import SyncTextTVParser


def fetch_page(page_number: str, save: bool = False):
    """Fetch and parse a TextTV page from the real API."""
    url = f"https://api.texttv.nu/api/get/{page_number}"
    params = {"app": "texttv-parser"}
    
    print(f"📡 Fetching page {page_number} from texttv.nu...")
    
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        # Save raw data if requested
        if save:
            filename = f"page{page_number}_raw.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved raw data to {filename}")
        
        # Parse the data (save to temp file first)
        print("🔄 Parsing...")
        temp_file = Path(f".temp_page{page_number}.json")
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            
            parser = SyncTextTVParser()
            page = parser.parse_from_file(str(temp_file))
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
        
        if not page:
            print("❌ Failed to parse page")
            return
        
        # Display results
        print("\n" + "="*70)
        print(f"📄 Page {page.num}: {page.title}")
        print(f"🕒 Updated: {datetime.fromtimestamp(page.date_updated_unix).strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print("\n" + page.get_clean_text())
        print("\n" + "="*70)
        
        # Save cleaned text if requested
        if save:
            filename = f"page{page_number}_clean.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(page.get_clean_text())
            print(f"💾 Saved cleaned text to {filename}")
        
        print(f"\n✅ Successfully fetched and parsed page {page_number}")
        
    except httpx.HTTPError as e:
        print(f"❌ HTTP error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python fetch_real_data.py <page_number> [--save]")
        print("\nExamples:")
        print("  python fetch_real_data.py 100")
        print("  python fetch_real_data.py 150 --save")
        print("\nCommon pages:")
        print("  100-149: News (Nyheter)")
        print("  150-179: Sports (Sport)")
        print("  200-249: Economy (Ekonomi)")
        print("  300-399: Weather (Väder)")
        sys.exit(1)
    
    page_number = sys.argv[1]
    save = "--save" in sys.argv or "-s" in sys.argv
    
    fetch_page(page_number, save)


if __name__ == "__main__":
    main()
