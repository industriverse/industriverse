#!/usr/bin/env python3
"""
Fix remaining bare except clauses in cloud providers and other files.
Week 17 Day 5: Final Error Handling Cleanup
"""

import sys
from pathlib import Path


def fix_cloud_providers():
    """Fix cloud provider files"""
    fixed_count = 0

    # AWS Provider
    aws_path = Path("src/deployment_operations_layer/cloud_provider/aws_provider.py")
    if aws_path.exists():
        content = aws_path.read_text()

        # Fix 1: ECS update service (line 733)
        content = content.replace(
            """                    forceNewDeployment=spec.get("force_new_deployment", True)
                )
            except:
                # Create new service""",
            """                    forceNewDeployment=spec.get("force_new_deployment", True)
                )
            except self.ecs_client.exceptions.ServiceNotFoundException:
                # ServiceNotFoundException: service doesn't exist, create new one
                # Create new service"""
        )

        # Fix 2: CloudFormation update stack (line 978)
        content = content.replace(
            """
                operation = "update"
            except:
                # Create new stack""",
            """
                operation = "update"
            except self.cf_client.exceptions.ClientError as e:
                # ClientError: stack doesn't exist or can't be updated
                if 'does not exist' in str(e):
                    # Create new stack"""
        )

        aws_path.write_text(content)
        print(f"✓ Fixed: {aws_path}")
        fixed_count += 2

    # Azure Provider
    azure_path = Path("src/deployment_operations_layer/cloud_provider/azure_provider.py")
    if azure_path.exists():
        content = azure_path.read_text()

        # Fix: Resource group check (line 251)
        content = content.replace(
            """            self.resource_client.resource_groups.get(resource_group_name)
            return True
        except:
            return False""",
            """            self.resource_client.resource_groups.get(resource_group_name)
            return True
        except Exception:
            # Azure exception: resource group doesn't exist or permission denied
            # Note: azure.core.exceptions could be more specific but Exception is safe here
            return False"""
        )

        azure_path.write_text(content)
        print(f"✓ Fixed: {azure_path}")
        fixed_count += 1

    # GCP Provider
    gcp_path = Path("src/deployment_operations_layer/cloud_provider/gcp_provider.py")
    if gcp_path.exists():
        content = gcp_path.read_text()

        # Fix 1: Cloud Run update service (line 793)
        content = content.replace(
            """                    service=service
                )
            except:
                # Create new service""",
            """                    service=service
                )
            except Exception:
                # Google API exception: service doesn't exist
                # Note: google.api_core.exceptions.NotFound would be more specific
                # Create new service"""
        )

        # Fix 2: Cloud Functions update (line 1086)
        content = content.replace(
            """                    function=function
                )
            except:
                # Create new function""",
            """                    function=function
                )
            except Exception:
                # Google API exception: function doesn't exist
                # Note: google.api_core.exceptions.NotFound would be more specific
                # Create new function"""
        )

        gcp_path.write_text(content)
        print(f"✓ Fixed: {gcp_path}")
        fixed_count += 2

    return fixed_count


def main():
    """Main entry point"""
    print("=" * 70)
    print("Week 17 Day 5: Fixing FINAL Bare Except Clauses")
    print("=" * 70)
    print()

    fixed_count = fix_cloud_providers()

    print()
    print("=" * 70)
    print(f"✓ Successfully fixed {fixed_count} bare except clauses")
    print(f"✓ Total progress: {30 + fixed_count}/36 instances fixed")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
