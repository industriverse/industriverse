# Android Testing Guide
**Week 13 Day 7: Comprehensive Testing Protocol**

## Testing Environment Setup

### Required Devices
- **Physical Device**: Pixel 6 or newer (Android 12+)
- **Emulator**: API 34 (Android 14) and API 24 (Android 7.0)
- **Variety**: Test on different manufacturers (Samsung, OnePlus, Xiaomi)

### Development Tools
```bash
# Install Android SDK Platform Tools
brew install android-platform-tools  # macOS
sudo apt-get install android-tools-adb  # Linux

# Enable USB debugging on physical device
# Settings → About Phone → Tap Build Number 7 times
# Settings → Developer Options → USB Debugging

# Verify device connection
adb devices

# Enable logcat filtering
adb logcat -s CapsuleService:D WebSocketManager:D CapsuleWidget:D
```

## Unit Testing

### Data Models
```kotlin
// CapsuleTest.kt
class CapsuleTest {
    @Test
    fun capsule_requiresAttention_criticalPriority_returnsTrue() {
        val capsule = Capsule(
            capsuleId = "test-1",
            priority = CapsulePriority.CRITICAL,
            // ...
        )
        assertTrue(capsule.requiresAttention())
    }

    @Test
    fun capsule_requiresAttention_lowPriorityRead_returnsFalse() {
        val capsule = Capsule(
            capsuleId = "test-2",
            priority = CapsulePriority.LOW,
            isRead = true,
            // ...
        )
        assertFalse(capsule.requiresAttention())
    }
}
```

### WebSocket Manager
```kotlin
// WebSocketManagerTest.kt
class WebSocketManagerTest {
    @Test
    fun webSocketManager_connect_updatesConnectionState() = runTest {
        val manager = WebSocketManager(Gson())
        manager.connect("user123", "token123")

        delay(1000)
        assertTrue(manager.connectionState.value is ConnectionState.Connecting)
    }

    @Test
    fun webSocketManager_reconnect_exponentialBackoff() = runTest {
        val manager = WebSocketManager(Gson())
        // Simulate connection failures
        // Verify backoff delays: 2s, 4s, 8s, 16s...
    }
}
```

## Integration Testing

### Service Lifecycle
```bash
# Start service manually
adb shell am startservice \
  -n com.industriverse.capsules/.service.CapsuleService \
  -a com.industriverse.capsules.START_SERVICE

# Verify service running
adb shell dumpsys activity services CapsuleService

# Stop service
adb shell am startservice \
  -n com.industriverse.capsules/.service.CapsuleService \
  -a com.industriverse.capsules.STOP_SERVICE

# Verify service stopped
adb shell dumpsys activity services | grep CapsuleService
```

### WebSocket Connection
```bash
# Monitor WebSocket connection
adb logcat -s WebSocketManager:D

# Expected logs:
# D/WebSocketManager: Connecting to WebSocket...
# D/WebSocketManager: WebSocket opened successfully
# D/WebSocketManager: Connected to Capsule Gateway
```

### Notification Testing
```bash
# Verify notification channels created
adb shell dumpsys notification

# Check notification posted
adb shell dumpsys notification | grep "com.industriverse.capsules"

# Simulate notification action
adb shell am broadcast \
  -a com.industriverse.capsules.EXECUTE_ACTION \
  --es capsule_id "test-capsule-1" \
  --es action_id "dismiss"
```

## UI Testing (Espresso)

### Main Activity
```kotlin
// MainActivityTest.kt
@RunWith(AndroidJUnit4::class)
class MainActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_displaysConnectionStatus() {
        onView(withId(R.id.connection_status))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_emptyState_whenNoCapsules() {
        onView(withText("No active capsules"))
            .check(matches(isDisplayed()))
    }

    @Test
    fun mainActivity_capsuleList_whenCapsulesExist() {
        // Mock capsules in WebSocketManager
        onView(withId(R.id.capsule_list))
            .check(matches(isDisplayed()))
    }
}
```

### Widget Testing
```kotlin
// WidgetTest.kt
class CompactWidgetTest {
    @Test
    fun compactWidget_showsCapsule_whenAvailable() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val provider = CompactWidgetProvider()

        // Trigger widget update
        val intent = Intent(AppWidgetManager.ACTION_APPWIDGET_UPDATE)
        provider.onReceive(context, intent)

        // Verify widget content
        // (Requires custom test harness for Glance widgets)
    }
}
```

## Functional Test Scenarios

### Scenario 1: Cold Start
```
1. Kill app completely (adb shell am force-stop com.industriverse.capsules)
2. Launch app from launcher
3. VERIFY: MainActivity opens
4. VERIFY: CapsuleService starts within 2 seconds
5. VERIFY: Foreground notification appears
6. VERIFY: WebSocket connects within 5 seconds
7. VERIFY: Connection status shows "Connected"
```

### Scenario 2: Background Persistence
```
1. Launch app
2. Wait for service to start
3. Press Home button
4. Swipe app from Recent Apps
5. VERIFY: Foreground notification still visible
6. VERIFY: Service still running (adb shell dumpsys)
7. VERIFY: WebSocket still connected
8. Wait 5 minutes
9. VERIFY: Service hasn't been killed
```

### Scenario 3: Reboot Persistence
```
1. Install app
2. Launch once to initialize
3. Reboot device (adb reboot)
4. Wait for device to boot
5. VERIFY: Service auto-starts via BootReceiver
6. VERIFY: Foreground notification appears
7. VERIFY: No user interaction needed
```

### Scenario 4: Network Interruption
```
1. Launch app with active connection
2. Enable Airplane mode
3. VERIFY: Connection status shows "Disconnected"
4. VERIFY: Reconnection attempts visible in logs
5. Wait 30 seconds
6. Disable Airplane mode
7. VERIFY: Connection automatically restored within 10 seconds
8. VERIFY: No data loss or corruption
```

### Scenario 5: Capsule Notifications
```
1. Ensure service running
2. Simulate capsule creation via WebSocket
3. VERIFY: Notification appears within 1 second
4. VERIFY: Notification shows correct title and subtitle
5. VERIFY: Action buttons present (Dismiss, Complete)
6. Tap "Dismiss" action
7. VERIFY: Notification dismissed
8. VERIFY: Action sent to server via WebSocket
```

### Scenario 6: Widget Updates
```
1. Add Compact widget to home screen
2. VERIFY: Widget shows highest priority capsule
3. Wait 15 minutes
4. VERIFY: Widget updates via WorkManager
5. Add Expanded widget
6. VERIFY: Shows 3-4 capsules in grid
7. Add Full widget
8. VERIFY: Shows scrollable list of capsules
9. Tap widget
10. VERIFY: App opens to capsule details
```

### Scenario 7: Battery Optimization
```
1. Enable battery saver mode
2. VERIFY: Service continues running
3. Enable Doze mode simulation:
   adb shell dumpsys deviceidle force-idle
4. VERIFY: Service adapts to restrictions
5. Exit Doze mode:
   adb shell dumpsys deviceidle unforce
6. VERIFY: Service resumes normal operation
```

### Scenario 8: Memory Pressure
```
1. Launch app
2. Open 10+ other apps to create memory pressure
3. VERIFY: Service not killed by system
4. Check memory usage:
   adb shell dumpsys meminfo com.industriverse.capsules
5. VERIFY: RAM usage < 100MB
6. Force low memory:
   adb shell am send-trim-memory com.industriverse.capsules RUNNING_CRITICAL
7. VERIFY: Service handles gracefully
```

## Performance Testing

### Metrics to Track
```bash
# CPU usage
adb shell top -n 1 | grep com.industriverse.capsules

# Memory usage
adb shell dumpsys meminfo com.industriverse.capsules

# Network usage
adb shell dumpsys netstats detail

# Battery usage
adb shell dumpsys batterystats com.industriverse.capsules

# Frame rate (should be 60fps)
adb shell dumpsys gfxinfo com.industriverse.capsules framestats
```

### Performance Benchmarks
- **Cold start**: < 2 seconds to CapsuleService running
- **WebSocket connect**: < 5 seconds from service start
- **Notification latency**: < 1 second from WebSocket message
- **Widget update**: < 100ms to render
- **Memory (app)**: < 50MB when in foreground
- **Memory (service)**: < 30MB when in background
- **CPU (idle)**: < 1% when no activity
- **Battery drain**: < 2% per hour (screen off, idle)

## Accessibility Testing

### TalkBack
```
1. Enable TalkBack (Settings → Accessibility)
2. Navigate app with screen reader
3. VERIFY: All buttons have content descriptions
4. VERIFY: Capsule list items readable
5. VERIFY: Notifications announce correctly
```

### Large Text
```
1. Increase text size to maximum (Settings → Display → Font Size)
2. VERIFY: All text scales appropriately
3. VERIFY: No text truncated or overlapping
4. VERIFY: Widgets remain readable
```

### High Contrast
```
1. Enable high contrast mode
2. VERIFY: All UI elements visible
3. VERIFY: Priority colors still distinguishable
```

## Security Testing

### Network Security
```bash
# Verify HTTPS/WSS only
adb shell dumpsys package com.industriverse.capsules | grep uses-cleartext

# Should output: uses-cleartext-traffic='false'

# Test certificate pinning
# Attempt MITM attack with invalid certificate
# VERIFY: Connection rejected
```

### Permission Handling
```bash
# Verify permissions requested
adb shell dumpsys package com.industriverse.capsules | grep permission

# VERIFY: Only necessary permissions requested
# VERIFY: Dangerous permissions have runtime requests
```

### Data Protection
```bash
# Verify app data encryption (Android 6+)
adb shell run-as com.industriverse.capsules ls -la

# VERIFY: No sensitive data in plain text
# VERIFY: Token stored in encrypted storage
```

## Regression Testing

### Test Matrix
| Test Case | Android 7 | Android 10 | Android 12 | Android 14 |
|-----------|-----------|------------|------------|------------|
| Cold start | ✓ | ✓ | ✓ | ✓ |
| Service persistence | ✓ | ✓ | ✓ | ✓ |
| Notifications | ✓ | ✓ | ✓ | ✓ |
| Widgets | ✓ | ✓ | ✓ | ✓ |
| Network failure | ✓ | ✓ | ✓ | ✓ |
| Battery optimization | - | ✓ | ✓ | ✓ |
| Notification permission | - | - | - | ✓ |

### Device Matrix
| Manufacturer | Model | Android | Status |
|--------------|-------|---------|--------|
| Google | Pixel 8 | 14 | ✓ |
| Samsung | Galaxy S23 | 13 | ✓ |
| OnePlus | 11 | 13 | ✓ |
| Xiaomi | 13 Pro | 13 | ✓ |
| Generic | Emulator | 7-14 | ✓ |

## Automated Testing

### GitHub Actions CI
```yaml
# .github/workflows/android.yml
name: Android CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      - name: Run unit tests
        run: ./gradlew test
      - name: Run instrumentation tests
        run: ./gradlew connectedAndroidTest
```

### Test Execution
```bash
# Run all unit tests
./gradlew test

# Run instrumentation tests (requires device/emulator)
./gradlew connectedAndroidTest

# Generate test coverage report
./gradlew jacocoTestReport

# Lint check
./gradlew lint
```

## Bug Reporting Template

```markdown
**Bug Title**: [Brief description]

**Environment**:
- Device: [e.g., Pixel 6]
- Android Version: [e.g., 14]
- App Version: [e.g., 1.0.0]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [Third step]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Logs**:
```
[Paste relevant logcat output]
```

**Screenshots**:
[Attach screenshots if applicable]

**Severity**:
- [ ] Critical (app crash, data loss)
- [ ] High (major feature broken)
- [ ] Medium (minor feature broken)
- [ ] Low (cosmetic issue)
```

## Test Sign-Off Checklist

Before marking Week 13 complete:

### Core Functionality
- [ ] App installs successfully
- [ ] Service starts on app launch
- [ ] WebSocket connects to gateway
- [ ] Notifications appear for capsules
- [ ] Widgets display on home screen
- [ ] Service survives app termination
- [ ] Service restarts after reboot

### Performance
- [ ] Cold start < 2 seconds
- [ ] Memory usage acceptable
- [ ] Battery drain < 2% per hour
- [ ] No ANRs or crashes
- [ ] Smooth animations (60fps)

### Compatibility
- [ ] Works on Android 7+
- [ ] Works on major manufacturers
- [ ] Adapts to different screen sizes
- [ ] Handles RTL languages
- [ ] Accessibility compliant

### Security
- [ ] HTTPS/WSS only
- [ ] No sensitive data in logs
- [ ] Proper permission handling
- [ ] Token encryption enabled

### Documentation
- [ ] README complete
- [ ] Code well-commented
- [ ] API documented
- [ ] Known issues listed

## Next Steps

After passing all tests:
1. Tag release: `git tag android-v1.0.0`
2. Generate signed APK for distribution
3. Submit to internal testing track
4. Proceed to Week 14: Desktop Applications
