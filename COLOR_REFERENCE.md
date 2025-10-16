# TextTV Color Reference

## Current Color Mappings

### Background Colors
**IMPORTANT**: `Bl` = Black (two letters), `B` = Blue (single letter)

- `bgBl` → Black background (ANSI 40m) - Used for toprow and main page background
- `bgB` → Blue background (ANSI 44m)
- `bgW` → White background (ANSI 47m)
- `bgR` → Red background (ANSI 41m)
- `bgG` → Green background (ANSI 42m)
- `bgY` → Yellow background (ANSI 43m)
- `bgC` → Cyan background (ANSI 46m)
- `bgM` → Magenta background (ANSI 45m)

### Foreground Colors
- `W` → White text (ANSI 37m)
- `Y` → Yellow text (ANSI 33m)
- `C` → Cyan text (ANSI 36m)
- `R` → Red text (ANSI 31m)
- `G` → Green text (ANSI 32m)
- `B` → Black text (ANSI 30m)
- `M` → Magenta text (ANSI 35m)
- `bl` → Blue text (ANSI 34m)

## TextTV Page Structure

### Toprow (Header)
- Background: `bgBl` (black)
- Text colors: `W` (white) for page number and timestamp, `Y` (yellow) for "SVT Text"
- Example: `<span class="bgBl W">100 </span><span class="bgBl Y">SVT Text </span>`

### Main Content Area
- Default background: `bgBl` (black)
- Headlines: `bgBl Y` (yellow text on black)
- Secondary text: `bgBl C` (cyan text on black)
- Normal text: `bgBl W` (white text on black)

### Graphics
- Use `bgImg` class with various background colors
- Weather maps use combinations of `bgB` (blue), `bgW` (white), `bgR` (red), `bgY` (yellow) etc.

## Adjusting Colors

If the colors don't match what you expect, you can modify the ANSI codes in:
`src/texttv/terminal_renderer.py`

For example, to make the blue background darker/lighter, adjust:
```python
BG_BLUE = '\033[44m'  # Standard ANSI blue
# Or use 256-color mode:
# BG_BLUE = '\033[48;5;21m'  # Darker blue (color 21)
```

## Testing

Test colors with:
```bash
# Page 100 - News with graphics
uv run texttv get-page 100 --colored

# Page 401 - Weather with lots of colored graphics
uv run texttv get-page 401 --colored

# Local file
uv run texttv parse-file index.txt --colored
```
