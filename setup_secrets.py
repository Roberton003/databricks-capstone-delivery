"""
One-time setup script: creates the Databricks secret scopes and stores the
Massive API key and Alpaca credentials. Run this locally (with the Databricks
CLI configured) or from a notebook - never commit the resulting secret values.

Usage:
    python setup_secrets.py
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

# Create/update Massive API key secret
w.secrets.create_scope(scope="massive")
w.secrets.put_secret(
    scope="massive",
    key="api-key",
    string_value=getpass.getpass("Paste your Massive API key: ")
)

# Create Lakebase URL secret
w.secrets.create_scope(scope="database")
w.secrets.put_secret(
    scope="database",
    key="lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)

# Create Alpaca credentials secrets
w.secrets.put_secret(
    scope="database",
    key="alpaca-key-id",
    string_value=getpass.getpass("Paste your Alpaca API Key ID: ")
)
w.secrets.put_secret(
    scope="database",
    key="alpaca-secret-key",
    string_value=getpass.getpass("Paste your Alpaca Secret Key: ")
)

# Set ACLs - restrict to specific service principals in production
w.secrets.put_acl(
    scope="database",
    principal="users",
    permission=workspace.AclPermission.READ,
)
w.secrets.put_acl(
    scope="massive",
    principal="users",
    permission=workspace.AclPermission.READ,
)

print("\nSetup complete! Secrets created:")
print("  - database/lakebase-url")
print("  - database/alpaca-key-id")
print("  - database/alpaca-secret-key")
print("  - massive/api-key")
print("\nIMPORTANT: For production, restrict ACLs to specific service principals!")
