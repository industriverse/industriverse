# LCODE Glyph Library

**Version:** 1.0
**Status:** Active

LCODE is the Universal Machine Language of the Industriverse. It uses concise visual symbols ("Glyphs") to represent complex manufacturing intents.

## Standard Library

| Symbol | Name | Description | Parameter | Example |
| :--- | :--- | :--- | :--- | :--- |
| **⊽** | MILL | Subtractive manufacturing. Remove material. | Depth (mm) | `⊽0.5` (Cut 0.5mm) |
| **⊸** | ALIGN | Optical/Mechanical alignment. | Anchor Point | `⊸C` (Align Center) |
| **⊼** | EXPOSE | Lithographic exposure. | Wavelength/Type | `⊼13E` (EUV Exposure) |
| **⊿** | ALERT | Drift detection or condition trigger. | Condition Code | `⊿5P` (Alert if >5% Deviation) |
| **⋙** | REPEAT | Loop the previous operation. | Count | `⋙3` (Repeat 3 times) |

## Compiler Output (Industrial Bytecode)

The `LCODECompiler` translates these glyphs into a JSON structure:

```json
{
  "op_code": "MILL",
  "symbol": "⊽",
  "params": 0.5,
  "raw": "⊽0.5"
}
```
