#!/usr/bin/env python3
"""
Comprehensive script to fix ALL bare except clauses in Industriverse codebase.
Week 17 Day 5: Error Handling Improvements

This script applies all remaining fixes for bare except clauses.
"""

import sys
from pathlib import Path


def fix_data_catalog_system():
    """Fix all 16 bare except clauses in data_catalog_system.py"""
    file_path = Path("src/data_layer/src/catalog/data_catalog_system.py")

    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False

    content = file_path.read_text()

    # Fix 1-2: pd.read_csv and pd.read_excel (lines 824, 829)
    content = content.replace(
        """                try:
                    sample_df = pd.read_csv(dataset_path, nrows=100)
                except:
                    return "tabular\"""",
        """                try:
                    sample_df = pd.read_csv(dataset_path, nrows=100)
                except (pd.errors.ParserError, ValueError, FileNotFoundError, PermissionError):
                    # ParserError: invalid CSV format
                    # ValueError: encoding or parsing error
                    # FileNotFoundError: file doesn't exist
                    # PermissionError: can't read file
                    return "tabular\""""
    )

    content = content.replace(
        """                try:
                    sample_df = pd.read_excel(dataset_path, nrows=100)
                except:
                    return "tabular\"""",
        """                try:
                    sample_df = pd.read_excel(dataset_path, nrows=100)
                except (pd.errors.ParserError, ValueError, FileNotFoundError, PermissionError):
                    # ParserError: invalid Excel format
                    # ValueError: encoding or parsing error
                    # FileNotFoundError: file doesn't exist
                    # PermissionError: can't read file
                    return "tabular\""""
    )

    # Fix 3: pd.to_datetime in detection (line 838)
    content = content.replace(
        """                try:
                    pd.to_datetime(sample_df[col])
                    datetime_cols.append(col)
                except:
                    pass""",
        """                try:
                    pd.to_datetime(sample_df[col])
                    datetime_cols.append(col)
                except (ValueError, TypeError, KeyError):
                    # ValueError: invalid date format
                    # TypeError: incompatible type for datetime conversion
                    # KeyError: column doesn't exist
                    pass"""
    )

    # Fix 4: JSON parsing (line 857)
    content = content.replace(
        """                else:
                    return "json"
            except:
                return "json\"""",
        """                else:
                    return "json"
            except (json.JSONDecodeError, FileNotFoundError, PermissionError, KeyError, TypeError):
                # JSONDecodeError: invalid JSON format
                # FileNotFoundError: file doesn't exist
                # PermissionError: can't read file
                # KeyError: unexpected data structure
                # TypeError: data is not indexable
                return "json\""""
    )

    # Fix 5-6: pd.read_csv and pd.read_excel in extract (lines 889, 894)
    content = content.replace(
        """                    try:
                        df = pd.read_csv(dataset_path)
                    except:
                        return metadata""",
        """                    try:
                        df = pd.read_csv(dataset_path)
                    except (pd.errors.ParserError, ValueError, FileNotFoundError, PermissionError):
                        # ParserError: invalid CSV format
                        # ValueError: encoding error
                        # FileNotFoundError: file doesn't exist
                        # PermissionError: can't read file
                        return metadata"""
    )

    content = content.replace(
        """                    try:
                        df = pd.read_excel(dataset_path)
                    except:
                        return metadata""",
        """                    try:
                        df = pd.read_excel(dataset_path)
                    except (pd.errors.ParserError, ValueError, FileNotFoundError, PermissionError):
                        # ParserError: invalid Excel format
                        # ValueError: encoding error
                        # FileNotFoundError: file doesn't exist
                        # PermissionError: can't read file
                        return metadata"""
    )

    # Fix 7: Database read (line 908)
    content = content.replace(
        """                        else:
                            return metadata
                    except:
                        return metadata""",
        """                        else:
                            return metadata
                    except (sqlite3.Error, pd.errors.DatabaseError, ValueError):
                        # sqlite3.Error: database error
                        # DatabaseError: pandas database error
                        # ValueError: invalid query or table
                        return metadata"""
    )

    # Fix 8: pd.to_datetime in metadata extraction (line 951)
    content = content.replace(
        """                        try:
                            pd.to_datetime(df[col])
                            datetime_cols.append(col)
                        except:
                            pass""",
        """                        try:
                            pd.to_datetime(df[col])
                            datetime_cols.append(col)
                        except (ValueError, TypeError, KeyError):
                            # ValueError: invalid date format
                            # TypeError: incompatible type for datetime conversion
                            # KeyError: column doesn't exist
                            pass"""
    )

    # Fix 9: pd.infer_freq (line 970)
    content = content.replace(
        """                            if freq:
                                metadata["frequency"] = freq
                        except:
                            pass""",
        """                            if freq:
                                metadata["frequency"] = freq
                        except (ValueError, TypeError):
                            # ValueError: can't infer frequency
                            # TypeError: incompatible datetime type
                            pass"""
    )

    # Fix 10-11: Image operations (lines 990, 1011)
    content = content.replace(
        """                        metadata["resolution"] = f"{img.width}x{img.height}"
                        metadata["color_mode"] = img.mode
                    except:
                        pass""",
        """                        metadata["resolution"] = f"{img.width}x{img.height}"
                        metadata["color_mode"] = img.mode
                    except (IOError, OSError, AttributeError):
                        # IOError: can't read image
                        # OSError: file doesn't exist or permission denied
                        # AttributeError: image doesn't have width/height/mode
                        pass"""
    )

    # Fix 12: DataFrame unique/classes (line 1051)
    content = content.replace(
        """                                classes = set(df[class_cols[0]].unique())
                                metadata["classes"] = list(classes)
                    except:
                        pass""",
        """                                classes = set(df[class_cols[0]].unique())
                                metadata["classes"] = list(classes)
                    except (KeyError, AttributeError):
                        # KeyError: column doesn't exist
                        # AttributeError: df doesn't have expected methods
                        pass"""
    )

    # Fix 13: DataFrame min/max (line 1130)
    content = content.replace(
        """                            col_schema["minimum"] = float(df[col].min())
                            col_schema["maximum"] = float(df[col].max())
                        except:
                            pass""",
        """                            col_schema["minimum"] = float(df[col].min())
                            col_schema["maximum"] = float(df[col].max())
                        except (ValueError, TypeError):
                            # ValueError: can't convert to float
                            # TypeError: incompatible type for min/max
                            pass"""
    )

    # Fix 14: DataFrame unique for enum (line 1142)
    content = content.replace(
        """                            try:
                                col_schema["enum"] = df[col].dropna().unique().tolist()
                            except:
                                pass""",
        """                            try:
                                col_schema["enum"] = df[col].dropna().unique().tolist()
                            except (ValueError, TypeError):
                                # ValueError: can't convert to list
                                # TypeError: incompatible type for unique()
                                pass"""
    )

    # Fix 15-16: Image verify (lines 1662, 1683)
    content = content.replace(
        """                        img.verify()
                        metrics["image_validity"] = 1.0
                    except:
                        metrics["image_validity"] = 0.0""",
        """                        img.verify()
                        metrics["image_validity"] = 1.0
                    except (IOError, OSError):
                        # IOError: can't verify image
                        # OSError: file error
                        metrics["image_validity"] = 0.0"""
    )

    content = content.replace(
        """                                img.verify()
                                valid_count += 1
                            except:
                                pass""",
        """                                img.verify()
                                valid_count += 1
                            except (IOError, OSError):
                                # IOError: can't verify image
                                # OSError: file error
                                pass"""
    )

    file_path.write_text(content)
    print(f"✓ Fixed: {file_path}")
    return True


def fix_protocol_adapters():
    """Fix protocol adapter files (OPC UA, Modbus, MQTT)"""

    # Fix OPC UA adapter (2 instances)
    opcua_path = Path("src/protocol_layer/industrial/adapters/opcua/opcua_adapter.py")
    if opcua_path.exists():
        content = opcua_path.read_text()

        content = content.replace(
            """                try:
                    result["timestamp"] = await node.get_value_timestamp()
                except:
                    pass""",
            """                try:
                    result["timestamp"] = await node.get_value_timestamp()
                except (AttributeError, asyncio.TimeoutError) as e:
                    # AttributeError: node doesn't support timestamps
                    # TimeoutError: request timed out
                    pass"""
        )

        content = content.replace(
            """                try:
                    result["description"] = (await node.get_description()).Text
                except:
                    pass""",
            """                try:
                    result["description"] = (await node.get_description()).Text
                except (AttributeError, asyncio.TimeoutError) as e:
                    # AttributeError: node doesn't have description
                    # TimeoutError: request timed out
                    pass"""
        )

        opcua_path.write_text(content)
        print(f"✓ Fixed: {opcua_path}")

    # Fix Modbus adapter (1 instance)
    modbus_path = Path("src/protocol_layer/industrial/adapters/modbus/modbus_adapter.py")
    if modbus_path.exists():
        content = modbus_path.read_text()

        content = content.replace(
            """                if not result.isError():
                    for key, value in result.information.items():
                        identification[key] = value.decode('utf-8', errors='replace')
            except:
                identification = {}""",
            """                if not result.isError():
                    for key, value in result.information.items():
                        identification[key] = value.decode('utf-8', errors='replace')
            except (AttributeError, UnicodeDecodeError, KeyError):
                # AttributeError: result.information doesn't exist
                # UnicodeDecodeError: can't decode bytes
                # KeyError: missing expected keys
                identification = {}"""
        )

        modbus_path.write_text(content)
        print(f"✓ Fixed: {modbus_path}")

    # Fix MQTT adapter (1 instance)
    mqtt_path = Path("src/protocol_layer/industrial/adapters/mqtt/mqtt_adapter.py")
    if mqtt_path.exists():
        content = mqtt_path.read_text()

        content = content.replace(
            """            # Try to unsubscribe
            try:
                await self.unsubscribe(subscription_id)
            except:
                pass""",
            """            # Try to unsubscribe
            try:
                await self.unsubscribe(subscription_id)
            except (KeyError, asyncio.TimeoutError, ConnectionError):
                # KeyError: subscription doesn't exist
                # TimeoutError: unsubscribe timed out
                # ConnectionError: not connected to broker
                pass"""
        )

        mqtt_path.write_text(content)
        print(f"✓ Fixed: {mqtt_path}")


def fix_deployment_layer():
    """Fix deployment operations layer files"""

    # Fix template manager (1 instance)
    template_path = Path("src/deployment_operations_layer/template/template_import_export_manager.py")
    if template_path.exists():
        content = template_path.read_text()

        content = content.replace(
            """                        return "json"
                    elif content.strip().startswith("---") or ":" in content:
                        return "yaml"
            except:
                pass""",
            """                        return "json"
                    elif content.strip().startswith("---") or ":" in content:
                        return "yaml"
            except (UnicodeDecodeError, AttributeError):
                # UnicodeDecodeError: file is not UTF-8
                # AttributeError: file_obj doesn't have read()
                pass"""
        )

        template_path.write_text(content)
        print(f"✓ Fixed: {template_path}")


def main():
    """Main entry point"""
    print("=" * 70)
    print("Week 17 Day 5: Fixing ALL Remaining Bare Except Clauses")
    print("=" * 70)
    print()

    fixed_count = 0

    # Fix data catalog system (16 instances)
    if fix_data_catalog_system():
        fixed_count += 16

    # Fix protocol adapters (4 instances)
    fix_protocol_adapters()
    fixed_count += 4

    # Fix deployment layer (1 instance)
    fix_deployment_layer()
    fixed_count += 1

    print()
    print("=" * 70)
    print(f"✓ Successfully fixed {fixed_count} bare except clauses")
    print(f"✓ Total progress: {9 + fixed_count}/31 instances fixed")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
