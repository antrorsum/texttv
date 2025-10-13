# TextTV API Format

The TextTV Parser supports the **texttv.nu API format** used by Swedish TextTV APIs.

## Real TextTV API (texttv.nu)

This is the **actual format** used by Swedish TextTV APIs like `https://api.texttv.nu/api/get/100`.

### Structure
```json
[
  {
    "num": "100",
    "title": "Hamas har frigivit samtliga ur gisslan",
    "content": ["<div class=\"root\">...HTML content...</div>"],
    "content_plain": [],
    "next_page": "101",
    "prev_page": "100",
    "date_updated_unix": 1760375163,
    "permalink": "https://texttv.nu/100/start-36750942",
    "id": "36750942",
    "breadcrumbs": []
  }
]
```

### Characteristics
- Returns an **array** of page objects
- Content is **HTML** in the `content` field
- Uses `num` instead of `number`
- Timestamp is Unix time in `date_updated_unix`
- Includes navigation (`next_page`, `prev_page`)

### How to Get Data
```bash
# Using curl
curl "https://api.texttv.nu/api/get/100?app=yourapp" > page100.json

# Using wget
wget "https://api.texttv.nu/api/get/100?app=yourapp" -O page100.json

# Using httpx in Python
import httpx
response = httpx.get("https://api.texttv.nu/api/get/100?app=yourapp")
data = response.json()
```

## Working with Real API

### Download and Parse
```bash
# 1. Download from real API
curl "https://api.texttv.nu/api/get/100?app=texttv-parser" > news.json

# 2. Parse with our tool
uv run texttv parse-file news.json --clean
```

### Python Example
```python
import httpx
from src.texttv_parser import TextTVParser

async def fetch_and_parse():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.texttv.nu/api/get/100",
            params={"app": "texttv-parser"}
        )
        data = response.json()
    
    parser = TextTVParser()
    page = parser.parse_real_api_page(data)
    
    print(page.title)
    print(page.get_clean_text())
```

## Text Cleaning

The parser converts TextTV pages to a `TextTVPage` object that provides:

```python
# Get cleaned, readable text
clean_text = page.get_clean_text()

# Access metadata
print(f"Page: {page.num}")
print(f"Title: {page.title}")
print(f"Updated: {page.date_updated_unix}")
```

### Cleaning Process
1. **Extract text** from HTML
2. **Remove headers** (SVT TEXT, page numbers)
3. **Remove navigation** elements
4. **Clean whitespace** and empty lines
5. **Remove duplicates** (consecutive identical lines)

## Example: Complete Workflow

```python
#!/usr/bin/env python3
"""Fetch, parse, and save TextTV page."""

import httpx
import json
from src.texttv_parser import SyncTextTVParser

# 1. Fetch from real API
response = httpx.get(
    "https://api.texttv.nu/api/get/100",
    params={"app": "my-texttv-app"}
)

# 2. Save raw data
with open("page100_raw.json", "w") as f:
    json.dump(response.json(), f, indent=2)

# 3. Parse it
parser = SyncTextTVParser()
page = parser.parse_from_file("page100_raw.json")

# 4. Save cleaned text
with open("page100_clean.txt", "w") as f:
    f.write(page.get_clean_text())

print(f"✓ Fetched and parsed page {page.num}: {page.title}")
```

## API Endpoints

### texttv.nu API
- **Base**: `https://api.texttv.nu/api/get/`
- **Page**: `https://api.texttv.nu/api/get/{page_number}`
- **Query params**: `?app=yourappname` (optional but recommended)

### Common Pages
- **100-149**: News (Nyheter)
- **150-179**: Sports (Sport)
- **200-249**: Economy (Ekonomi)
- **300-399**: Weather (Väder)
- **400-499**: Lottery (Lotto)

## Notes

- The real API returns HTML with CSS classes for styling
- Some content includes images (background images in spans)
- Links are preserved as `<a href="/page">` elements
- The parser handles Swedish characters (å, ä, ö) correctly
- Data is converted to UTF-8 encoding

## Troubleshooting

### Empty or Garbled Text
- Check that the JSON file is valid
- Ensure UTF-8 encoding
- Verify the API response structure

### Missing Content
- Some pages may have minimal content
- Graphics-heavy pages may have less text
- Check `page.content` to see raw data

## Contributing

To add support for another API format:

1. Create a new model in `models.py`
2. Add detection logic in `parser.py`
3. Implement conversion to `TextTVPage`
4. Add tests in `tests/test_parser.py`

---

**Status**: ✅ Real API format fully supported!
