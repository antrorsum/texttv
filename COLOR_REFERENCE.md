# TextTV Color Reference

## Overview
This document describes how TextTV CSS color classes are mapped to ANSI terminal colors in the renderer. The renderer uses **bright ANSI colors by default** for better visibility, with special handling for red colors and solid color blocks.

## Color Mappings (Bright Mode - Default)

### Background Colors
**IMPORTANT**: `Bl` = Black (two letters), `B` = Blue (single letter)

| CSS Class | Color | Standard ANSI | Bright ANSI | Renderer Uses | Notes |
|-----------|-------|---------------|-------------|---------------|-------|
| `bgBl` | Black | 40m | 100m | **40m** (standard) | Main page background |
| `bgB` | Blue | 44m | 104m | **104m** (bright) | SVT logo, weather water |
| `bgW` | White | 47m | 107m | **107m** (bright) | SVT logo, clouds |
| `bgR` | Red | 41m | 101m | **41m** (standard) | Weather map - darker red |
| `bgG` | Green | 42m | 102m | **102m** (bright) | |
| `bgY` | Yellow | 43m | 103m | **103m** (bright) | Decorative lines |
| `bgC` | Cyan | 46m | 106m | **106m** (bright) | |
| `bgM` | Magenta | 45m | 105m | **105m** (bright) | |

### Foreground Colors
**CRITICAL**: `B` (capital) = Blue FG, `bl` (lowercase) = Black FG - opposite of background naming!

| CSS Class | Color | Standard ANSI | Bright ANSI | Renderer Uses | Notes |
|-----------|-------|---------------|-------------|---------------|-------|
| `W` | White | 37m | 97m | **97m** (bright) | Page numbers, normal text |
| `Y` | Yellow | 33m | 93m | **93m** (bright) | Headlines |
| `C` | Cyan | 36m | 96m | **96m** (bright) | Secondary text |
| `R` | Red | 31m | 91m | **31m** (standard) | Weather map - darker red |
| `G` | Green | 32m | 92m | **92m** (bright) | |
| `B` | Blue | 34m | 94m | **94m** (bright) | **Capital B = Blue FG** |
| `M` | Magenta | 35m | 95m | **95m** (bright) | |
| `bl` | Black | 30m | 90m | **30m** (standard) | **Lowercase bl = Black FG** |

## Special Rendering Rules

### 1. Solid Color Blocks (`bgImg` with only background color)
When a `bgImg` span has only a background color (no foreground color class), the renderer automatically sets the foreground to match the background to create solid color blocks.

**Example**:
```html
<span class="bgR bgImg" style="...">█</span>
```
→ Rendered as: `\033[41m\033[31m█` (red BG + red FG = solid red block)

**Why**: Without this, the terminal's default foreground (usually white) would make red blocks appear white.

### 2. Red Color Exception
Red uses **standard ANSI** (not bright) because:
- Weather maps need darker, brownish-red appearance
- Bright red (91m/101m) looks too vivid and incorrect
- Standard red (31m/41m) matches the original TextTV weather maps

### 3. Whitespace Preservation
The renderer preserves exact spacing from HTML by:
- Replacing spaces with non-breaking space (U+00A0) before parsing
- Restoring them after rendering
- This ensures perfect alignment of logos and graphics

## TextTV Page Structure

### Toprow (Header)
- Background: `bgBl` (black, 40m)
- Page number: `W` (bright white, 97m)
- "SVT Text": `Y` (bright yellow, 93m)
- Timestamp: `W` (bright white, 97m)

Example: `<span class="bgBl W">100 </span><span class="bgBl Y">SVT Text </span>`

### Main Content Area
- Default background: `bgBl` (black, 40m)
- Headlines: `Y` (bright yellow, 93m)
- Secondary text: `C` (bright cyan, 96m)
- Normal text: `W` (bright white, 97m)

### Graphics (`bgImg`)
- SVT logo (lines 2-5 of page 100): Blue/white mosaic characters
- Weather maps (page 401): Blue (water), white (clouds), red (warm areas), yellow (sun)
- Decorative lines: Yellow background with black foreground

## Adjusting Colors

### Disable Bright Colors
To use standard ANSI colors instead of bright:

```python
from texttv.terminal_renderer import TerminalRenderer

renderer = TerminalRenderer(use_bright_colors=False)
```

### Modify Color Codes
Edit `src/texttv/terminal_renderer.py` to change specific colors:

```python
# Example: Use 256-color mode for custom blue
BG_BLUE = '\033[48;5;21m'  # Darker blue (color 21)
FG_BLUE = '\033[38;5;39m'  # Lighter blue (color 39)
```

## Testing

Test color rendering with:

```bash
# Page 100 - News with SVT logo graphics
uv run texttv get-page 100 --colored

# Page 401 - Weather map with red/blue/white/yellow
uv run texttv get-page 401 --colored

# Local file
uv run texttv parse-file index.txt --colored

# Compare standard vs bright colors
python3 -c "
print('Standard blue: \033[44m    \033[0m')
print('Bright blue:   \033[104m    \033[0m')
print()
print('Standard red:  \033[41m    \033[0m')
print('Bright red:    \033[101m    \033[0m')
"
```

## Common Issues

### White blocks instead of colored blocks
**Problem**: `bgR bgImg` showing white instead of red
**Cause**: Missing automatic foreground color for solid blocks
**Status**: **Fixed** - Renderer now auto-sets matching foreground

### Wrong blue/black colors
**Problem**: Blue showing as black or vice versa
**Cause**: Confused `B` (blue FG) with `bl` (black FG)
**Solution**: Remember: Capital `B` = Blue, lowercase `bl` = Black

### Misaligned SVT logo
**Problem**: Logo spacing looks wrong
**Cause**: HTML parser collapsed multiple spaces
**Status**: **Fixed** - Whitespace preservation implemented

### Red too bright on weather map
**Problem**: Red section looks vivid instead of brownish
**Cause**: Using bright red instead of standard red
**Status**: **Fixed** - Red now uses standard ANSI (31m/41m)
