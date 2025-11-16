# Industriverse Capsules - iOS Live Activities

Production-ready iOS application with ActivityKit Live Activities for Capsule Pins.

## Overview

This iOS app displays real-time capsule updates using Apple's Live Activities framework, appearing in:
- **Dynamic Island** (iPhone 14 Pro and later)
- **Lock Screen** (all supported devices)
- **StandBy mode** (iOS 17+)
- **Apple Watch Smart Stack** (watchOS 11+)

## Requirements

- **Xcode 15.0+**
- **iOS 16.2+** (Live Activities)
- **Swift 5.9+**
- **ActivityKit framework**
- **APNs certificate** for remote updates

## Project Structure

```
IndustriverseCapsules/
├── IndustriverseCapsules.xcodeproj/    # Xcode project
├── IndustriverseCapsules/              # Main app target
│   ├── IndustriverseCapsulesApp.swift  # App entry point
│   ├── ContentView.swift               # Main UI
│   ├── CapsuleAttributes.swift         # ActivityAttributes definition
│   ├── CapsuleManager.swift            # ActivityKit lifecycle manager
│   ├── CapsuleAPIService.swift         # Backend API client
│   ├── Info.plist                      # App configuration
│   ├── IndustriverseCapsules.entitlements  # Capabilities
│   └── Assets.xcassets/                # App assets
└── CapsuleWidget/                      # Widget extension target
    ├── CapsuleWidgetLiveActivity.swift # Live Activity views
    ├── Info.plist                      # Widget configuration
    └── Assets.xcassets/                # Widget assets
```

## Features

### ✅ Live Activity Presentations

#### Dynamic Island
- **Compact**: Icon + progress/metric
- **Minimal**: Icon only (when multiple activities)
- **Expanded**: Full details with actions

#### Lock Screen
- Full-width presentation
- Progress bars
- Interactive action buttons
- Priority badges

#### StandBy
- Optimized for landscape viewing
- Larger text and graphics

### ✅ Production-Ready Components

1. **CapsuleAttributes** - ActivityAttributes protocol implementation
   - Static attributes (capsuleId, type, title, icon, color)
   - Dynamic ContentState (status, progress, metrics, actions)

2. **CapsuleManager** - ActivityKit lifecycle management
   - Start/update/end Live Activities
   - Push token registration
   - State observation
   - Alert configurations

3. **CapsuleAPIService** - Backend integration
   - Real HTTP client (no mocks)
   - Authentication with Bearer tokens
   - Activity sync
   - Action handlers

4. **App Intents** - Interactive actions
   - Mitigate intent
   - Inspect intent
   - Deep linking to app

## Setup Instructions

### 1. Configure Xcode Project

1. Open `IndustriverseCapsules.xcodeproj` in Xcode
2. Select the project in the navigator
3. Update **Bundle Identifier**: `com.industriverse.capsules`
4. Select your **Development Team**

### 2. Configure Capabilities

Enable the following capabilities in both targets:

**IndustriverseCapsules (Main App)**:
- ✅ Push Notifications
- ✅ Background Modes → Remote notifications
- ✅ App Groups → `group.com.industriverse.capsules`

**CapsuleWidgetExtension**:
- ✅ App Groups → `group.com.industriverse.capsules`

### 3. Configure APNs

1. Create an **APNs certificate** in Apple Developer Portal
2. Download and install the certificate
3. Export `.p8` key file
4. Configure in capsule-gateway backend

### 4. Configure Backend URL

Set the capsule-gateway URL:

**Option 1: Environment Variable**
```bash
export CAPSULE_GATEWAY_URL="https://capsule-gateway.industriverse.com"
```

**Option 2: Xcode Scheme**
1. Product → Scheme → Edit Scheme
2. Run → Arguments → Environment Variables
3. Add: `CAPSULE_GATEWAY_URL` = `https://your-gateway-url.com`

### 5. Build and Run

1. Select target device (iPhone with iOS 16.2+)
2. Build and run (⌘R)
3. Grant notification permissions when prompted

## API Integration

### Backend Endpoints

The app integrates with these capsule-gateway endpoints:

```
POST   /api/v1/devices/register        # Register push token
GET    /api/v1/capsules/activities     # Fetch all activities
GET    /api/v1/capsules/:id            # Fetch specific activity
POST   /api/v1/capsules/:id/action     # Perform action
PUT    /api/v1/capsules/:id/status     # Update status
```

### Authentication

The app uses Bearer token authentication:

```swift
await CapsuleAPIService.shared.setAuthToken("your-jwt-token")
```

Store tokens securely in Keychain (production recommendation).

### Starting a Live Activity

```swift
let initialState = CapsuleAttributes.ContentState(
    status: "active",
    statusMessage: "Security alert detected",
    progress: 0.5,
    metricValue: "23 events",
    metricLabel: "Total Events",
    lastUpdated: Date(),
    actionCount: 2,
    priority: 5,
    isStale: false,
    alertMessage: nil
)

try await CapsuleManager.shared.startActivity(
    capsuleId: "capsule-123",
    type: "security",
    title: "Security Alert",
    iconName: "shield.fill",
    primaryColor: "red",
    initialState: initialState
)
```

### Updating a Live Activity

```swift
let newState = CapsuleAttributes.ContentState(
    status: "resolved",
    statusMessage: "Issue has been mitigated",
    progress: 1.0,
    metricValue: "0 events",
    metricLabel: "Remaining",
    lastUpdated: Date(),
    actionCount: 0,
    priority: 2,
    isStale: false,
    alertMessage: nil
)

await CapsuleManager.shared.updateActivity(
    capsuleId: "capsule-123",
    newState: newState
)
```

### Critical Updates with Alerts

```swift
let alertConfig = CapsuleManager.createAlertConfig(
    title: "Critical Update",
    body: "Immediate action required",
    sound: .default
)

await CapsuleManager.shared.updateActivity(
    capsuleId: "capsule-123",
    newState: newState,
    alertConfig: alertConfig
)
```

### Ending a Live Activity

```swift
await CapsuleManager.shared.endActivity(
    capsuleId: "capsule-123",
    dismissalPolicy: .after(Date().addingTimeInterval(900)) // 15 minutes
)
```

## Remote Push Notifications

### Push Notification Format

Send push notifications to update Live Activities remotely:

```json
{
  "aps": {
    "timestamp": 1699999999,
    "event": "update",
    "content-state": {
      "status": "active",
      "statusMessage": "New update available",
      "progress": 0.75,
      "metricValue": "15 events",
      "metricLabel": "Pending",
      "lastUpdated": "2025-11-16T08:00:00Z",
      "actionCount": 1,
      "priority": 4,
      "isStale": false,
      "alertMessage": null
    },
    "alert": {
      "title": "Capsule Update",
      "body": "Your capsule has been updated"
    }
  }
}
```

### Push Token Registration

The app automatically registers push tokens with the backend:

```swift
// Happens automatically in CapsuleManager
private func registerPushToken(_ token: Data, for capsuleId: String) async {
    let tokenString = token.map { String(format: "%02x", $0) }.joined()
    await CapsuleAPIService.shared.registerPushToken(
        capsuleId: capsuleId,
        pushToken: tokenString
    )
}
```

## Testing

### Test on Physical Device

Live Activities require a **physical iPhone** (simulator not supported).

**Minimum Requirements**:
- iPhone 8 or later
- iOS 16.2 or later
- iPhone 14 Pro or later for Dynamic Island

### Test Scenarios

1. **Start Activity**: Tap "+" button in app
2. **Update Activity**: Tap "Update" in capsule row
3. **End Activity**: Tap "End" in capsule row
4. **Lock Screen**: Lock device to see Lock Screen presentation
5. **Dynamic Island**: Long-press Dynamic Island to see expanded view
6. **Actions**: Tap "Mitigate" or "Inspect" buttons

### Debug Logging

The app includes comprehensive logging:

```
✅ Started Live Activity for capsule: capsule-123
📱 Activity is active: capsule-123
🔑 Push token for capsule-123: a1b2c3d4...
✅ Updated Live Activity for capsule: capsule-123
🔔 Updated Live Activity with alert for capsule: capsule-123
🔚 Activity ended: capsule-123
```

## Design Guidelines

Following Apple's Human Interface Guidelines:

- **Glanceable**: Show most important info prominently
- **Defined Duration**: Max 8 hours per activity
- **No Sensitive Data**: Visible to casual observers
- **No Ads**: Only task-related information
- **Timely Updates**: Update only when content changes
- **Proper Dismissal**: 15-30 minutes after completion

## Troubleshooting

### Live Activities Not Appearing

1. Check Settings → Notifications → IndustriverseCapsules → Live Activities (enabled)
2. Verify iOS version (16.2+)
3. Check device compatibility
4. Review Xcode console for errors

### Push Notifications Not Working

1. Verify APNs certificate is valid
2. Check push token registration in backend
3. Verify network connectivity
4. Check notification permissions

### Dynamic Island Not Showing

1. Requires iPhone 14 Pro or later
2. Verify Live Activity is active
3. Check if other activities are using Dynamic Island

## Production Checklist

- [ ] Configure production APNs certificate
- [ ] Set production backend URL
- [ ] Implement secure token storage (Keychain)
- [ ] Add error handling and retry logic
- [ ] Test on multiple device models
- [ ] Test with poor network conditions
- [ ] Verify battery impact
- [ ] Add analytics and monitoring
- [ ] Submit for App Store review

## Resources

- [Apple HIG: Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [ActivityKit Documentation](https://developer.apple.com/documentation/activitykit)
- [Capsule Gateway API Docs](../../../docs/CAPSULE_GATEWAY.md)

## License

Copyright © 2025 Industriverse. All rights reserved.
