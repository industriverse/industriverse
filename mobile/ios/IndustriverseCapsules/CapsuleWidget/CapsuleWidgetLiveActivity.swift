//
//  CapsuleWidgetLiveActivity.swift
//  CapsuleWidget
//
//  Production-ready Live Activity implementation
//  Following Apple's ActivityConfiguration pattern
//

import ActivityKit
import WidgetKit
import SwiftUI

@main
struct CapsuleWidgetLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: CapsuleAttributes.self) { context in
            // MARK: - Lock Screen Presentation
            // Also appears as banner on devices without Dynamic Island
            LockScreenLiveActivityView(context: context)
                .activityBackgroundTint(context.attributes.getColor().opacity(0.2))
                .activitySystemActionForegroundColor(context.attributes.getColor())
            
        } dynamicIsland: { context in
            // MARK: - Dynamic Island Presentations
            DynamicIsland {
                // MARK: Expanded Presentation
                // Shown when user long-presses the Dynamic Island
                DynamicIslandExpandedRegion(.leading) {
                    // Left side: Icon and title
                    VStack(alignment: .leading, spacing: 4) {
                        Image(systemName: context.attributes.getTypeIcon())
                            .font(.title2)
                            .foregroundColor(context.attributes.getColor())
                        
                        Text(context.attributes.title)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .lineLimit(2)
                    }
                }
                
                DynamicIslandExpandedRegion(.trailing) {
                    // Right side: Status and priority
                    VStack(alignment: .trailing, spacing: 4) {
                        HStack(spacing: 4) {
                            Image(systemName: context.state.statusIcon)
                                .font(.caption2)
                                .foregroundColor(context.state.statusColor)
                            Text(context.state.status.capitalized)
                                .font(.caption2)
                                .fontWeight(.medium)
                        }
                        
                        Text(context.state.priorityLabel)
                            .font(.caption2)
                            .foregroundColor(context.state.priorityColor)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(context.state.priorityColor.opacity(0.2))
                            .cornerRadius(4)
                    }
                }
                
                DynamicIslandExpandedRegion(.center) {
                    // Center: Progress bar
                    if context.state.progress > 0 {
                        VStack(spacing: 4) {
                            ProgressView(value: context.state.progress)
                                .progressViewStyle(.linear)
                                .tint(context.attributes.getColor())
                            
                            Text("\(Int(context.state.progress * 100))%")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal)
                    }
                }
                
                DynamicIslandExpandedRegion(.bottom) {
                    // Bottom: Main content
                    VStack(alignment: .leading, spacing: 8) {
                        // Status message
                        Text(context.state.statusMessage)
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .lineLimit(2)
                        
                        // Metric
                        HStack {
                            Text(context.state.metricLabel)
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Spacer()
                            Text(context.state.metricValue)
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(context.attributes.getColor())
                        }
                        
                        // Actions
                        if context.state.actionCount > 0 {
                            HStack(spacing: 12) {
                                Button(intent: MitigateIntent(capsuleId: context.attributes.capsuleId)) {
                                    Label("Mitigate", systemImage: "shield.fill")
                                        .font(.caption)
                                }
                                .buttonStyle(.borderedProminent)
                                .tint(context.attributes.getColor())
                                
                                Button(intent: InspectIntent(capsuleId: context.attributes.capsuleId)) {
                                    Label("Inspect", systemImage: "magnifyingglass")
                                        .font(.caption)
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                
            } compactLeading: {
                // MARK: Compact Leading (left pill)
                Image(systemName: context.attributes.getTypeIcon())
                    .foregroundColor(context.attributes.getColor())
                
            } compactTrailing: {
                // MARK: Compact Trailing (right pill)
                if context.state.progress > 0 {
                    ProgressView(value: context.state.progress)
                        .progressViewStyle(.circular)
                        .tint(context.attributes.getColor())
                } else {
                    Text(context.state.metricValue)
                        .font(.caption2)
                        .fontWeight(.semibold)
                        .foregroundColor(context.attributes.getColor())
                }
                
            } minimal: {
                // MARK: Minimal (when multiple activities)
                Image(systemName: context.attributes.getTypeIcon())
                    .foregroundColor(context.attributes.getColor())
            }
            .keylineTint(context.attributes.getColor())
        }
    }
}

// MARK: - Lock Screen View

struct LockScreenLiveActivityView: View {
    let context: ActivityViewContext<CapsuleAttributes>
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack(spacing: 12) {
                Image(systemName: context.attributes.getTypeIcon())
                    .font(.title2)
                    .foregroundColor(context.attributes.getColor())
                    .frame(width: 40, height: 40)
                    .background(context.attributes.getColor().opacity(0.2))
                    .cornerRadius(8)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(context.attributes.title)
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    HStack(spacing: 6) {
                        Image(systemName: context.state.statusIcon)
                            .font(.caption2)
                            .foregroundColor(context.state.statusColor)
                        Text(context.state.status.capitalized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Priority badge
                Text(context.state.priorityLabel)
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(context.state.priorityColor)
                    .cornerRadius(6)
            }
            
            // Progress bar
            if context.state.progress > 0 {
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Progress")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Spacer()
                        Text("\(Int(context.state.progress * 100))%")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(context.attributes.getColor())
                    }
                    
                    ProgressView(value: context.state.progress)
                        .progressViewStyle(.linear)
                        .tint(context.attributes.getColor())
                }
            }
            
            // Status message
            Text(context.state.statusMessage)
                .font(.subheadline)
                .foregroundColor(.primary)
                .lineLimit(2)
            
            // Metric
            HStack {
                Text(context.state.metricLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text(context.state.metricValue)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(context.attributes.getColor())
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(context.attributes.getColor().opacity(0.1))
            .cornerRadius(8)
            
            // Actions
            if context.state.actionCount > 0 {
                HStack(spacing: 12) {
                    Button(intent: MitigateIntent(capsuleId: context.attributes.capsuleId)) {
                        HStack {
                            Image(systemName: "shield.fill")
                            Text("Mitigate")
                        }
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(context.attributes.getColor())
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                    
                    Button(intent: InspectIntent(capsuleId: context.attributes.capsuleId)) {
                        HStack {
                            Image(systemName: "magnifyingglass")
                            Text("Inspect")
                        }
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(Color.secondary.opacity(0.2))
                        .foregroundColor(.primary)
                        .cornerRadius(8)
                    }
                }
            }
            
            // Last updated
            Text("Updated \(context.state.lastUpdated, style: .relative) ago")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding(16)
    }
}

// MARK: - App Intents for Actions

import AppIntents

struct MitigateIntent: AppIntent {
    static var title: LocalizedStringResource = "Mitigate Capsule"
    static var description = IntentDescription("Mitigate the capsule issue")
    
    @Parameter(title: "Capsule ID")
    var capsuleId: String
    
    func perform() async throws -> some IntentResult {
        // Call capsule-gateway API to perform mitigation
        await CapsuleAPIService.shared.performAction(capsuleId: capsuleId, action: "mitigate")
        return .result()
    }
}

struct InspectIntent: AppIntent {
    static var title: LocalizedStringResource = "Inspect Capsule"
    static var description = IntentDescription("Inspect the capsule details")
    
    @Parameter(title: "Capsule ID")
    var capsuleId: String
    
    func perform() async throws -> some IntentResult {
        // Call capsule-gateway API to perform inspection
        await CapsuleAPIService.shared.performAction(capsuleId: capsuleId, action: "inspect")
        return .result()
    }
}

// MARK: - Preview

#Preview("Notification", as: .content, using: CapsuleAttributes(
    capsuleId: "test-123",
    capsuleType: "security",
    title: "Security Alert",
    iconName: "shield.fill",
    primaryColor: "red",
    createdAt: Date()
)) {
    CapsuleWidgetLiveActivity()
} contentStates: {
    CapsuleAttributes.ContentState(
        status: "active",
        statusMessage: "Suspicious activity detected in production cluster",
        progress: 0.65,
        metricValue: "23 events",
        metricLabel: "Total Events",
        lastUpdated: Date(),
        actionCount: 2,
        priority: 5,
        isStale: false,
        alertMessage: nil
    )
}
