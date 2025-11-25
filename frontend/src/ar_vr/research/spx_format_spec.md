# .spx Format Specification (Version 3)

**Source:** https://github.com/reall3d-com/Reall3dViewer/blob/main/SPX_EN.md

---

## Overview

The `.spx` format is a 3DGS model format designed to be:
- **Flexible:** Optimized file header, flexible data blocks, effective compression
- **Extensible:** Open format with reserved fields for future expansion
- **Exclusive:** Custom format identifiers for proprietary data protection

---

## File Header (128 bytes)

Fixed-length header for format identification, containing bounding box data for sorting optimization and custom identifiers.

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–2 | ASCII | Magic | Fixed value `spx` |
| 3 | uint8 | Version | Current version: `2` |
| 4–7 | uint32 | Gaussian Count | Total number of Gaussian points |
| 8–11 | float32 | MinX | Bounding box minimum X coordinate |
| 12–15 | float32 | MaxX | Bounding box maximum X coordinate |
| 16–19 | float32 | MinY | Bounding box minimum Y coordinate |
| 20–23 | float32 | MaxY | Bounding box maximum Y coordinate |
| 24–27 | float32 | MinZ | Bounding box minimum Z coordinate |
| 28–31 | float32 | MaxZ | Bounding box maximum Z coordinate |
| 32–35 | float32 | Min Center Height | Min model center height (Y-axis) |
| 36–39 | float32 | Max Center Height | Max model center height (Y-axis) |
| 40–43 | uint32 | Creation Date | Date in `YYYYMMDD` format |
| 44–47 | uint32 | Creator ID | Unique value (0 reserved for official use) |
| 48–51 | uint32 | Exclusive ID | Non-zero for proprietary format (0 = public) |
| 52 | uint8 | SH degree | Allowed values: `0,1,2,3` |
| 53 | uint8 | Bit Flags | See below |
| 54–55 | uint16 | Reserved | Reserved |
| 56–63 | - | Reserved | Reserved |
| 64–123 | ASCII | Comment | Maximum 60 ASCII characters |
| 124–127 | uint32 | Checksum | Validates file integrity |

### Bit Flags (Byte 53)
- **bit 0:** Inverted flag (default 0)
- **bit 1–6:** Reserved
- **bit 7:** Large Scene flag (default 0)

---

## Data Blocks

Data blocks consist of a fixed header followed by customizable content.

### Data Block Structure

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Data Block Definition | Compression Flag (1bit) + Compression Type (3bit) + Data Block Length (28bit) |
| 4–n | bytes | Block Content | Actual data (format defined below) |

**Data Block Definition Breakdown:**
- **bit 0:** Compression Flag (0 = uncompressed, 1 = compressed)
- **bit 1–3:** Compression Type (0 = gzip, 1 = xz)
- **bit 4–31:** Data Block Length (28 bits)

### Data Block Content

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Count | Number of Gaussians in this block |
| 4–7 | uint32 | Format ID | Identifies block format |
| 8–n | bytes | Data | Structured per Format ID |

---

## Open Block Content Formats

**Reserved Range:** 0 to 65535 (open formats)  
**Other Values:** Exclusive formats

### Format 22: Basic Data (Optimized for Encoding/Decoding Performance)

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Gaussian Count | Number of Gaussians |
| 4–7 | uint32 | Format ID | `22` |
| 8–n | bytes | Data | x0...y0...z0...x1...y1...z1...x2...y2...z2...sx...sy...sz...r...g...b...a...rw...rx...ry...rz...p0...p1... |

**Data Fields:**
- `x, y, z`: Coordinates, 24-bit precision
- `sx, sy, sz`: Scale, 8-bit per axis
- `r, g, b, a`: Color, RGBA channels (8-bit each)
- `rw, rx, ry, rz`: Rotation, Quaternion components (8-bit each)
- `p0, p1`: Low and high bytes of palette index (omitted when no palette)

### Format 220: Basic Data (Optimized for Compression Ratio)

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Gaussian Count | Number of Gaussians |
| 4–7 | uint32 | Format ID | `220` (webp encoding) |
| 8–n | bytes | Data | length,webp([x0,y0,z0,255...]), length,webp([x1,y1,z1,255...]), ... |

**Data Fields (WebP encoded):**
- `x, y, z`: Coordinates, 24-bit precision
- `sx, sy, sz`: Scale, 8-bit per axis
- `r, g, b, a`: Color, RGBA channels (8-bit each)
- `r0, r1, r2, ri`: Rotation, Quaternion components (8-bit each), ri = max value index + 252
- `p0, p1`: Low and high bytes of palette index (omitted when no palette)

### Format 8: Palettes of SH (Auto-selected)

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Reserved | - |
| 4–7 | uint32 | Format ID | `8` (SH degree 1–3) |
| 8–n | bytes | Data | [sh0,sh1,sh2...sh14,sh0,sh1,sh2...sh14,...] |

**Data Fields:**
- `sh0–sh14`: Spherical harmonic coefficients (r,g,b,255), in pixel units

### Format 9: Palettes of SH (WebP Encoding, Auto-selected)

| Byte Offset | Type | Field Name | Description |
|-------------|------|------------|-------------|
| 0–3 | uint32 | Reserved | - |
| 4–7 | uint32 | Format ID | `9` (SH degree 1–3, webp) |
| 8–n | bytes | Data | webp([sh0,sh1,sh2...sh14,sh0,sh1,sh2...sh14,...]) |

**Data Fields:**
- `sh0–sh14`: Spherical harmonic coefficients (r,g,b,255), in pixel units

---

## Conversion Tool: gsbox

**Repository:** https://github.com/gotoeasy/gsbox

### Conversion Command
```bash
gsbox p2x -i /path/to/input.ply -o /path/to/output.spx
```

**Input:** `.ply` file (trained 3DGS model)  
**Output:** `.spx` file (compressed, optimized for web)

---

## Production Implementation Notes

1. **Use gsbox for conversion:** Don't implement .spx writer from scratch
2. **Verify checksum:** Validate file integrity after conversion
3. **Test compression:** Compare Format 22 vs 220 for file size
4. **Bounding box:** Required for sorting optimization in Reall3DViewer
5. **SH degree:** Match training configuration (0, 1, 2, or 3)
6. **Creator ID:** Use unique value to identify our models
7. **Comment field:** Add metadata (e.g., "Shadow Twin: motor_001")

---

## Historical Versions

- **SPX SPEC V2:** https://github.com/reall3d-com/Reall3dViewer/blob/main/spx-spec/v2/SPX_EN.md
- **SPX SPEC V1:** https://github.com/reall3d-com/Reall3dViewer/blob/main/spx-spec/v1/SPX_EN.md

---

**Status:** .spx format specification complete. Ready for production implementation.
