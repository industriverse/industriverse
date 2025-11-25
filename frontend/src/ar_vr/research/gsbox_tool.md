# gsbox - 3DGS Format Conversion Tool

**Repository:** https://github.com/gotoeasy/gsbox  
**Latest Version:** v4.4.0  
**License:** GPL-3.0  
**Language:** Go (cross-platform)

---

## Overview

Cross-platform command-line tool for 3D Gaussian Splatting, focusing on format conversion and optimization.

---

## Features

1. **Format Conversion:** `.ply`, `.splat`, `.spx`, `.spz`, `.sog`, `.ksplat`
2. **File Information:** View metadata for all supported formats
3. **Data Transformation:** Rotation, Scale, Translation
4. **Model Merging:** Combine multiple model files into one

---

## Format Support Matrix

| Format | Read | Write | Reference |
|--------|------|-------|-----------|
| `.ply` | ☑ | ☑ | Standard point cloud |
| `.compressed.ply` | ☑ | ☑ | Compressed point cloud |
| `.splat` | ☑ | ☑ | Gaussian Splatting |
| `.spx` | ☑ | ☑ | Reall3D format (flexible, expandable) |
| `.spz` | ☑ | ☑ | Compressed Gaussian Splatting |
| `.ksplat` | ☑ | ☑ (v4.2.0+) | Kerbl Gaussian Splatting |
| `.sog` | ☑ | ☑ | Structured Gaussian Splatting |

---

## Installation

### Binary Download (Recommended)
```bash
# Download from GitHub Releases
# https://github.com/gotoeasy/gsbox/releases

# Linux/macOS
wget https://github.com/gotoeasy/gsbox/releases/download/v4.4.0/gsbox-linux-amd64
chmod +x gsbox-linux-amd64
sudo mv gsbox-linux-amd64 /usr/local/bin/gsbox

# Windows
# Download gsbox-windows-amd64.exe from releases
```

### Build from Source
```bash
git clone https://github.com/gotoeasy/gsbox.git
cd gsbox
go build -o gsbox main.go
```

---

## Usage

### Basic Conversion: .ply → .spx

```bash
gsbox p2x -i /path/to/input.ply -o /path/to/output.spx
```

### Advanced Conversion with Options

```bash
# Convert .ply to .spx with custom settings
gsbox p2x \
  -i /path/to/input.ply \
  -o /path/to/output.spx \
  -c "Shadow Twin: motor_001" \
  -q 7 \
  -bs 65536 \
  -ct 0 \
  -sh 3
```

**Options Explained:**
- `-c`: Comment (metadata)
- `-q`: Quality (1–9, default 5)
- `-bs`: Block size (64–1048576, default 65536)
- `-ct`: Compression type (0=gzip, 1=xz)
- `-sh`: SH degree (0–3, default from input)

---

## Command Reference

### Conversion Commands

| Command | Description |
|---------|-------------|
| `p2x`, `ply2spx` | Convert .ply to .spx |
| `p2s`, `ply2splat` | Convert .ply to .splat |
| `p2z`, `ply2spz` | Convert .ply to .spz |
| `p2g`, `ply2sog` | Convert .ply to .sog |
| `x2p`, `spx2ply` | Convert .spx to .ply |
| `x2s`, `spx2splat` | Convert .spx to .splat |
| `x2z`, `spx2spz` | Convert .spx to .spz |

### Utility Commands

| Command | Description |
|---------|-------------|
| `info <file>` | Display model file information |
| `join` | Join multiple model files into one |
| `ps`, `printsplat` | Print data to text file (splat format layout) |

---

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `-i`, `--input <file>` | Input file path | Required |
| `-o`, `--output <file>` | Output file path | Required |
| `-q`, `--quality <num>` | Quality (1–9) for spx/spz/sog | 5 |
| `-ct`, `--compression-type <type>` | Compression type (0=gzip, 1=xz) | 0 (gzip) |
| `-c`, `--comment <text>` | Comment for ply/spx output | - |
| `-a`, `--alpha <num>` | Minimum alpha (0–255) to filter output | - |
| `-bs`, `--block-size <num>` | Block size (64–1048576) for spx | 65536 |
| `-bf`, `--block-format <num>` | Block data format (19–20) for spx | 19 |
| `-sh`, `--shDegree <num>` | SH degree (0–3) for output | From input |
| `-f1`, `--is-inverted <bool>` | Header flag1 (IsInverted) for spx | false |

### Transformation Options

| Option | Description |
|--------|-------------|
| `-rx`, `--rotateX <num>` | Rotation angle (degrees) about X-axis |
| `-ry`, `--rotateY <num>` | Rotation angle (degrees) about Y-axis |
| `-rz`, `--rotateZ <num>` | Rotation angle (degrees) about Z-axis |
| `-s`, `--scale <num>` | Uniform scaling factor (0.001–1000) |
| `-tx`, `--translateX <num>` | Translation value about X-axis |
| `-ty`, `--translateY <num>` | Translation value about Y-axis |
| `-tz`, `--translateZ <num>` | Translation value about Z-axis |
| `-to`, `--transform-order <RST>` | Transform order (RST/RTS/SRT/STR/TRS/TSR) |

---

## Production Pipeline Integration

### Shadow Twin → .spx Workflow

```bash
#!/bin/bash
# convert_shadow_twin_to_spx.sh

SHADOW_TWIN_ID="$1"
INPUT_PLY="/tmp/shadow_twin_3dgs/${SHADOW_TWIN_ID}/model/point_cloud/iteration_30000/point_cloud.ply"
OUTPUT_SPX="/tmp/shadow_twin_3dgs/${SHADOW_TWIN_ID}/${SHADOW_TWIN_ID}.spx"

# Convert .ply to .spx with production settings
gsbox p2x \
  -i "$INPUT_PLY" \
  -o "$OUTPUT_SPX" \
  -c "Shadow Twin: ${SHADOW_TWIN_ID}" \
  -q 7 \
  -bs 65536 \
  -ct 0 \
  -sh 3

# Verify output
if [ -f "$OUTPUT_SPX" ]; then
  echo "✅ Conversion successful: $OUTPUT_SPX"
  gsbox info -i "$OUTPUT_SPX"
else
  echo "❌ Conversion failed"
  exit 1
fi
```

### Python Integration

```python
import subprocess
from pathlib import Path

def convert_ply_to_spx(
    input_ply: str,
    output_spx: str,
    comment: str = "",
    quality: int = 7,
    sh_degree: int = 3
) -> bool:
    """Convert .ply to .spx using gsbox"""
    
    cmd = [
        "gsbox", "p2x",
        "-i", input_ply,
        "-o", output_spx,
        "-q", str(quality),
        "-sh", str(sh_degree)
    ]
    
    if comment:
        cmd.extend(["-c", comment])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Converted: {output_spx}")
        return True
    else:
        print(f"❌ Conversion failed: {result.stderr}")
        return False
```

---

## Examples

### Example 1: Basic Conversion
```bash
gsbox p2x -i input.ply -o output.spx
```

### Example 2: High-Quality Conversion
```bash
gsbox p2x -i input.ply -o output.spx -q 9 -c "High quality model"
```

### Example 3: Remove SH Coefficients (Smaller File)
```bash
gsbox p2x -i input.ply -o output.spx -sh 0 -c "No SH coefficients"
```

### Example 4: Transform + Convert
```bash
gsbox p2x -i input.ply -o output.spx -rz 90 -s 0.5 -tx 1.0 -to TRS
```

### Example 5: View File Information
```bash
gsbox info -i model.spx
```

### Example 6: Merge Multiple Models
```bash
gsbox join -i model1.ply -i model2.splat -i model3.spx -o merged.spx
```

---

## Production Best Practices

1. **Quality Setting:** Use `-q 7` for production (balance between size and quality)
2. **Compression:** Use gzip (`-ct 0`) for better compatibility
3. **SH Degree:** Match training configuration (`-sh 3` for full SH)
4. **Block Size:** Use default 65536 for optimal streaming
5. **Comments:** Always add metadata (`-c "Shadow Twin: motor_001"`)
6. **Validation:** Run `gsbox info` after conversion to verify
7. **Error Handling:** Check return code and stderr in automated pipelines

---

## Troubleshooting

### Issue: "Command not found"
**Solution:** Ensure gsbox is in PATH or use full path

### Issue: "Invalid input file"
**Solution:** Verify .ply file is valid (check with `gsbox info`)

### Issue: "Conversion failed"
**Solution:** Check disk space, file permissions, and input file integrity

### Issue: "Output file too large"
**Solution:** Reduce quality (`-q 5`), remove SH (`-sh 0`), or filter alpha (`-a 128`)

---

**Status:** gsbox tool documentation complete. Ready for production integration.
