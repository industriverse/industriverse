#!/usr/bin/env python3
"""
Automated script to fix bare except clauses with specific exception types.
Week 17 Day 5: Error Handling Improvements

This script systematically replaces bare `except:` clauses with specific
exception types based on the operation being performed.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Mapping of file patterns to exception fixes
EXCEPTION_FIXES = [
    # =========================================================================
    # Data Layer Files
    # =========================================================================

    # storage_management_system.py - Line 656 (pd.to_datetime)
    {
        "file": "src/data_layer/src/storage_management/storage_management_system.py",
        "find": r"(\s+)try:\s+pd\.to_datetime\(sample_df\[col\]\)\s+datetime_cols\.append\(col\)\s+except:\s+pass",
        "replace": (
            r"\1try:\n"
            r"\1    pd.to_datetime(sample_df[col])\n"
            r"\1    datetime_cols.append(col)\n"
            r"\1except (ValueError, TypeError, KeyError):\n"
            r"\1    # ValueError: invalid date format\n"
            r"\1    # TypeError: incompatible type for datetime conversion\n"
            r"\1    # KeyError: column doesn't exist\n"
            r"\1    pass"
        )
    },

    # storage_management_system.py - Line 675 (JSON parsing)
    {
        "file": "src/data_layer/src/storage_management/storage_management_system.py",
        "old_text": """                    return "image"
                else:
                    return "json"
            except:
                return "json"
        else:""",
        "new_text": """                    return "image"
                else:
                    return "json"
            except (json.JSONDecodeError, FileNotFoundError, PermissionError, KeyError, TypeError):
                # JSONDecodeError: invalid JSON format
                # FileNotFoundError: file doesn't exist
                # PermissionError: can't read file
                # KeyError: unexpected data structure
                # TypeError: data is not indexable
                return "json"
        else:"""
    },

    # storage_management_system.py - Line 731 (Database query)
    {
        "file": "src/data_layer/src/storage_management/storage_management_system.py",
        "old_text": """                    return str(int(result[0]) + 1)
                else:
                    return "1"
            except:
                # Fallback to timestamp
                return datetime.now().strftime("%Y%m%d%H%M%S")""",
        "new_text": """                    return str(int(result[0]) + 1)
                else:
                    return "1"
            except (sqlite3.Error, TypeError, ValueError, IndexError):
                # sqlite3.Error: database error
                # TypeError: result[0] is None
                # ValueError: can't cast to int
                # IndexError: result is empty
                # Fallback to timestamp
                return datetime.now().strftime("%Y%m%d%H%M%S")"""
    },

    # storage_management_system.py - Line 758 (Version parsing)
    {
        "file": "src/data_layer/src/storage_management/storage_management_system.py",
        "old_text": """                # Default to 0.1.0
                return "0.1.0"
            except:
                # Fallback to 0.1.0
                return "0.1.0"

        return "0.1.0"  # Should never reach here""",
        "new_text": """                # Default to 0.1.0
                return "0.1.0"
            except (sqlite3.Error, IndexError, TypeError):
                # sqlite3.Error: database error
                # IndexError: result is empty
                # TypeError: invalid type conversion
                # Fallback to 0.1.0
                return "0.1.0"

        return "0.1.0"  # Should never reach here"""
    },

    # storage_management_system.py - Line 1543 (JSON parsing)
    {
        "file": "src/data_layer/src/storage_management/storage_management_system.py",
        "old_text": """                        try:
                            # Try to parse JSON
                            metadata[key] = json.loads(value)
                        except:
                            metadata[key] = value""",
        "new_text": """                        try:
                            # Try to parse JSON
                            metadata[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            # JSONDecodeError: invalid JSON
                            # TypeError: value is not a string
                            metadata[key] = value"""
    },

    # =========================================================================
    # Protocol Layer Files
    # =========================================================================

    # opcua_adapter.py - Lines 460, 465 (OPC UA operations)
    {
        "file": "src/protocol_layer/industrial/adapters/opcua/opcua_adapter.py",
        "old_text": """                try:
                    result["timestamp"] = await node.get_value_timestamp()
                except:
                    pass

                try:
                    result["description"] = (await node.get_description()).Text
                except:
                    pass""",
        "new_text": """                try:
                    result["timestamp"] = await node.get_value_timestamp()
                except (AttributeError, asyncio.TimeoutError) as e:
                    # AttributeError: node doesn't support timestamps
                    # TimeoutError: request timed out
                    pass

                try:
                    result["description"] = (await node.get_description()).Text
                except (AttributeError, asyncio.TimeoutError) as e:
                    # AttributeError: node doesn't have description
                    # TimeoutError: request timed out
                    pass"""
    },

    # modbus_adapter.py - Line 955 (Modbus identification)
    {
        "file": "src/protocol_layer/industrial/adapters/modbus/modbus_adapter.py",
        "old_text": """                if not result.isError():
                    for key, value in result.information.items():
                        identification[key] = value.decode('utf-8', errors='replace')
            except:
                identification = {}""",
        "new_text": """                if not result.isError():
                    for key, value in result.information.items():
                        identification[key] = value.decode('utf-8', errors='replace')
            except (AttributeError, UnicodeDecodeError, KeyError):
                # AttributeError: result.information doesn't exist
                # UnicodeDecodeError: can't decode bytes
                # KeyError: missing expected keys
                identification = {}"""
    },

    # mqtt_adapter.py - Line 639 (MQTT unsubscribe)
    {
        "file": "src/protocol_layer/industrial/adapters/mqtt/mqtt_adapter.py",
        "old_text": """            # Try to unsubscribe
            try:
                await self.unsubscribe(subscription_id)
            except:
                pass""",
        "new_text": """            # Try to unsubscribe
            try:
                await self.unsubscribe(subscription_id)
            except (KeyError, asyncio.TimeoutError, ConnectionError):
                # KeyError: subscription doesn't exist
                # TimeoutError: unsubscribe timed out
                # ConnectionError: not connected to broker
                pass"""
    },

    # =========================================================================
    # Deployment Operations Layer Files
    # =========================================================================

    # template_import_export_manager.py - Line 342 (Format detection)
    {
        "file": "src/deployment_operations_layer/template/template_import_export_manager.py",
        "old_text": """                        return "json"
                    elif content.strip().startswith("---") or ":" in content:
                        return "yaml"
            except:
                pass""",
        "new_text": """                        return "json"
                    elif content.strip().startswith("---") or ":" in content:
                        return "yaml"
            except (UnicodeDecodeError, AttributeError):
                # UnicodeDecodeError: file is not UTF-8
                # AttributeError: file_obj doesn't have read()
                pass"""
    },
]


def apply_fixes(dry_run: bool = False) -> int:
    """
    Apply all exception handling fixes.

    Args:
        dry_run: If True, only print what would be changed

    Returns:
        Number of files modified
    """
    modified_count = 0

    for fix in EXCEPTION_FIXES:
        file_path = Path(fix["file"])

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        try:
            content = file_path.read_text()
            original_content = content

            # Apply replacement
            if "old_text" in fix:
                # Simple text replacement
                if fix["old_text"] in content:
                    content = content.replace(fix["old_text"], fix["new_text"])
                else:
                    print(f"⚠️  Pattern not found in {file_path}")
                    continue
            elif "find" in fix:
                # Regex replacement
                content = re.sub(fix["find"], fix["replace"], content, flags=re.MULTILINE)

            # Check if anything changed
            if content == original_content:
                print(f"⚠️  No changes made to {file_path}")
                continue

            if dry_run:
                print(f"✓ Would modify: {file_path}")
            else:
                file_path.write_text(content)
                print(f"✓ Modified: {file_path}")
                modified_count += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            continue

    return modified_count


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix bare except clauses with specific exception types"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Week 17 Day 5: Fixing Bare Except Clauses")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    modified_count = apply_fixes(dry_run=args.dry_run)

    print()
    print("=" * 70)
    if args.dry_run:
        print(f"Would modify {modified_count} files")
    else:
        print(f"✓ Successfully modified {modified_count} files")
    print("=" * 70)

    return 0 if modified_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
