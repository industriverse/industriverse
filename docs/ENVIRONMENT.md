# Environment Configuration

This document describes all environment variables used by Capsule Pins PWA.

---

## Configuration Methods

### Method 1: Manus Platform Settings (Recommended)

Use the **Settings** panel in the Manus Management UI:

1. **App Title & Logo**: Settings → General
   - `VITE_APP_TITLE`: Application title
   - `VITE_APP_LOGO`: Logo path

2. **Secrets**: Settings → Secrets
   - Add/edit environment variables securely
   - Variables are encrypted and injected at runtime

### Method 2: Local Development

For local development, you can use environment variables:

```bash
# Create .env.local file (not tracked by git)
cp docs/env-template.txt .env.local

# Edit .env.local with your values
nano .env.local
```

---

## Required Variables

### Capsule Gateway Configuration

**`VITE_CAPSULE_GATEWAY_API`**
- **Description**: REST API endpoint for Capsule Gateway
- **Default**: `https://capsule-gateway.industriverse.io`
- **Example**: `https://capsule-gateway.industriverse.io`

**`VITE_CAPSULE_GATEWAY_WS`**
- **Description**: WebSocket endpoint for real-time updates
- **Default**: `wss://capsule-gateway.industriverse.io/ws`
- **Example**: `wss://capsule-gateway.industriverse.io/ws`

**`VITE_AUTH_TOKEN`**
- **Description**: JWT token for authentication
- **Required**: Yes (for production)
- **How to obtain**: Industriverse platform dashboard
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## Optional Variables

### Feature Flags

**`VITE_ENABLE_WEBSOCKET`**
- **Description**: Enable WebSocket auto-connect
- **Default**: `false`
- **Values**: `true` | `false`
- **Note**: Set to `false` in development when using mock data

**`VITE_USE_MOCK_DATA`**
- **Description**: Use mock capsule data instead of API
- **Default**: `true`
- **Values**: `true` | `false`
- **Note**: Set to `false` in production

**`VITE_ENABLE_PUSH_NOTIFICATIONS`**
- **Description**: Enable push notifications
- **Default**: `true`
- **Values**: `true` | `false`
- **Note**: Requires service worker and user permission

**`VITE_ENABLE_OFFLINE_MODE`**
- **Description**: Enable offline functionality
- **Default**: `true`
- **Values**: `true` | `false`
- **Note**: Requires service worker

**`VITE_ENABLE_BACKGROUND_SYNC`**
- **Description**: Enable background sync for offline actions
- **Default**: `true`
- **Values**: `true` | `false`
- **Note**: Requires service worker

### Development Options

**`VITE_DEBUG`**
- **Description**: Show debug information in console
- **Default**: `false`
- **Values**: `true` | `false`

**`VITE_WS_RECONNECT_DELAY`**
- **Description**: Initial WebSocket reconnect delay (ms)
- **Default**: `1000`
- **Example**: `1000`

**`VITE_WS_MAX_RECONNECT_DELAY`**
- **Description**: Maximum WebSocket reconnect delay (ms)
- **Default**: `30000`
- **Example**: `30000`

**`VITE_WS_HEARTBEAT_INTERVAL`**
- **Description**: WebSocket heartbeat interval (ms)
- **Default**: `30000`
- **Example**: `30000`

---

## Auto-Configured Variables

These variables are automatically configured by the Manus Platform:

- `VITE_ANALYTICS_ENDPOINT`: Analytics endpoint
- `VITE_ANALYTICS_WEBSITE_ID`: Analytics website ID
- `VITE_APP_ID`: Application ID
- `BUILT_IN_FORGE_API_KEY`: Internal API key
- `BUILT_IN_FORGE_API_URL`: Internal API URL

**Do not modify these variables unless instructed.**

---

## Environment Examples

### Development (Mock Data)

```bash
VITE_ENABLE_WEBSOCKET=false
VITE_USE_MOCK_DATA=true
VITE_DEBUG=true
```

### Development (Real Backend)

```bash
VITE_CAPSULE_GATEWAY_API=https://dev.capsule-gateway.industriverse.io
VITE_CAPSULE_GATEWAY_WS=wss://dev.capsule-gateway.industriverse.io/ws
VITE_AUTH_TOKEN=your_dev_token
VITE_ENABLE_WEBSOCKET=true
VITE_USE_MOCK_DATA=false
VITE_DEBUG=true
```

### Production

```bash
VITE_CAPSULE_GATEWAY_API=https://capsule-gateway.industriverse.io
VITE_CAPSULE_GATEWAY_WS=wss://capsule-gateway.industriverse.io/ws
VITE_AUTH_TOKEN=your_production_token
VITE_ENABLE_WEBSOCKET=true
VITE_USE_MOCK_DATA=false
VITE_DEBUG=false
VITE_ENABLE_PUSH_NOTIFICATIONS=true
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_BACKGROUND_SYNC=true
```

---

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use Manus Settings UI** for production secrets
3. **Rotate tokens regularly** (every 90 days)
4. **Use different tokens** for dev/staging/production
5. **Limit token permissions** to minimum required
6. **Monitor token usage** in platform dashboard

---

## Troubleshooting

### WebSocket Connection Fails

**Problem**: WebSocket shows "disconnected" or errors

**Solutions**:
1. Check `VITE_ENABLE_WEBSOCKET` is set to `true`
2. Verify `VITE_CAPSULE_GATEWAY_WS` URL is correct
3. Ensure `VITE_AUTH_TOKEN` is valid
4. Check network connectivity
5. Verify server supports WebSocket (wss://)

### API Calls Fail

**Problem**: API requests return 401 or 403 errors

**Solutions**:
1. Verify `VITE_AUTH_TOKEN` is valid
2. Check token hasn't expired
3. Ensure `VITE_CAPSULE_GATEWAY_API` URL is correct
4. Verify CORS is configured on server

### Mock Data Not Showing

**Problem**: No capsules displayed in development

**Solutions**:
1. Ensure `VITE_USE_MOCK_DATA=true`
2. Check browser console for errors
3. Verify mock data is defined in `Home.tsx`

---

## Adding New Variables

To add a new environment variable:

1. **Add to code**: Use `import.meta.env.VITE_YOUR_VAR`
2. **Document here**: Add to this file with description
3. **Update Settings UI**: If user-configurable
4. **Test**: Verify in dev and production

**Note**: All `VITE_*` variables are exposed to the client. Never use `VITE_*` prefix for server-only secrets.

---

## Support

For configuration help:
- Documentation: https://docs.industriverse.io
- Support: https://help.manus.im
