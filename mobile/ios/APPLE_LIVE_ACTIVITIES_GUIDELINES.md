# Apple Live Activities Guidelines - Key Points

**Source:** Apple Human Interface Guidelines & ActivityKit Documentation

## Core Principles

1. **Defined Duration**: Live Activities are for tasks with clear beginning and end (max 8 hours)
2. **Glanceable Information**: Prioritize important info for quick understanding
3. **All Presentations**: Must support Lock Screen, Dynamic Island, StandBy, and Apple Watch
4. **No Ads/Promotions**: Only display event/task-related information
5. **Privacy**: Avoid sensitive information in Live Activity (visible to casual observers)

## Starting Live Activities

- Start when people expect it (e.g., food delivery order, rideshare request)
- Offer App Shortcuts to start Live Activities
- Can start with remote push notification (iOS 17.2+)
- Give people control with buttons/toggles if needed

## Updating Live Activities

- Update only when new content is available
- Alert people only for essential updates (lights up screen, plays sound)
- Avoid alerting too often or people will disable in Settings
- Consider cycling through multiple events instead of creating many Live Activities

## Ending Live Activities

- End immediately after task completes
- Dynamic Island: Removed immediately
- Lock Screen: Remains up to 4 hours (configurable)
- Choose custom removal time proportional to duration (15-30 min typical)

## Layout Considerations

### Dynamic Island
- Compact: Small pill shape (minimal space)
- Minimal: Two separate elements on either side of camera
- Expanded: Larger interactive area

### Lock Screen
- Full-width presentation
- More space for information
- Swipe up to dismiss

### StandBy
- Optimized for landscape viewing
- Larger text and graphics

## Design Best Practices

- Use ContainerRelativeShape for consistent appearance
- Add transitions and animations for content updates
- Support Dark Mode and accessibility features
- Test on all supported devices and orientations
- Use SF Symbols and system fonts when possible

## Technical Requirements

- iOS 16.2+ for Live Activities
- ActivityKit framework
- Push notification entitlements
- App Groups for data sharing
- Background modes configuration
