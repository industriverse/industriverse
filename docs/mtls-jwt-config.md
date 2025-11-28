# mTLS + JWT Configuration (Production Guide)

## mTLS (service-to-service)
- Generate CA, server, and client certificates; distribute via secret manager or cert-manager.
- Configure Postgres/NATS/Neo4j/Qdrant to require client certs.
- For k8s, install cert-manager, create ClusterIssuer, and issue certs per service; enforce mTLS at ingress/sidecar (Envoy/Linkerd/Istio).

## JWT/OIDC (user/API access)
- Deploy Keycloak/Dex; configure client for BridgeAPI with redirect URIs.
- Validate tokens in API gateway or app via JWKS.
- Map roles/claims to permissions (admin/operator/observer).

## Suggested env vars
```
JWT_ISSUER=https://auth.yourdomain
JWT_AUDIENCE=industriverse-api
JWKS_URL=https://auth.yourdomain/.well-known/jwks.json
```

## Integration points
- BridgeAPI/microservices: add JWT middleware using python-jose/authlib; verify iss/aud/exp.
- Resolver/registry/ledger endpoints: require mTLS for service calls; JWT for user-facing APIs.
- Telemetry endpoints (WebSocket): require JWT for subscription; validate before joining stream.
