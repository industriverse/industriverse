# UTID Attestation

- UTIDs are bound to host fingerprint and an attestation signature.
- Attestation key can be provided via:
  - `UTID_ATTEST_KEY_PATH` pointing to a key file (preferred).
  - `UTID_ATTEST_SECRET` environment variable (fallback).
- Resolver verifies both host binding and attestation signature.

Production guidance:
- Use TPM/PUF or HSM-backed key; mount key via `UTID_ATTEST_KEY_PATH`.
- Rotate secrets periodically; restrict file permissions to the service user.
