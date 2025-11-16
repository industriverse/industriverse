//
//  CapsuleManager.swift
//  IndustriverseCapsules
//
//  Production-ready ActivityKit lifecycle manager
//  Handles starting, updating, and ending Live Activities
//

import Foundation
import ActivityKit
import Combine

/// Manages the lifecycle of Capsule Live Activities
@MainActor
class CapsuleManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = CapsuleManager()
    
    // MARK: - Published Properties
    
    @Published var activeActivities: [String: Activity<CapsuleAttributes>] = [:]
    @Published var activityStates: [String: CapsuleAttributes.ContentState] = [:]
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    private init() {
        // Observe existing activities on app launch
        Task {
            await observeExistingActivities()
        }
    }
    
    // MARK: - Public Methods
    
    /// Start a new Live Activity
    /// - Parameters:
    ///   - capsuleId: Unique identifier for the capsule
    ///   - type: Capsule type
    ///   - title: Capsule title
    ///   - iconName: SF Symbol name
    ///   - primaryColor: Color theme
    ///   - initialState: Initial content state
    /// - Returns: Activity ID if successful
    func startActivity(
        capsuleId: String,
        type: String,
        title: String,
        iconName: String,
        primaryColor: String,
        initialState: CapsuleAttributes.ContentState
    ) async throws -> String? {
        
        // Check if Live Activities are enabled
        guard ActivityAuthorizationInfo().areActivitiesEnabled else {
            print("❌ Live Activities are disabled in Settings")
            return nil
        }
        
        // Check if activity already exists
        if activeActivities[capsuleId] != nil {
            print("⚠️ Activity already exists for capsule: \(capsuleId)")
            return capsuleId
        }
        
        // Create attributes
        let attributes = CapsuleAttributes(
            capsuleId: capsuleId,
            capsuleType: type,
            title: title,
            iconName: iconName,
            primaryColor: primaryColor,
            createdAt: Date()
        )
        
        do {
            // Request new activity
            let activity = try Activity<CapsuleAttributes>.request(
                attributes: attributes,
                content: .init(state: initialState, staleDate: nil),
                pushType: .token
            )
            
            // Store activity
            activeActivities[capsuleId] = activity
            activityStates[capsuleId] = initialState
            
            // Observe activity state changes
            observeActivity(activity, capsuleId: capsuleId)
            
            // Get push token for remote updates
            if let pushToken = activity.pushToken {
                await registerPushToken(pushToken, for: capsuleId)
            }
            
            print("✅ Started Live Activity for capsule: \(capsuleId)")
            return activity.id
            
        } catch {
            print("❌ Failed to start Live Activity: \(error.localizedDescription)")
            throw error
        }
    }
    
    /// Update an existing Live Activity
    /// - Parameters:
    ///   - capsuleId: Capsule identifier
    ///   - newState: New content state
    ///   - alertConfig: Optional alert configuration for critical updates
    func updateActivity(
        capsuleId: String,
        newState: CapsuleAttributes.ContentState,
        alertConfig: AlertConfiguration? = nil
    ) async {
        guard let activity = activeActivities[capsuleId] else {
            print("⚠️ No active activity found for capsule: \(capsuleId)")
            return
        }
        
        do {
            // Update activity content
            if let alertConfig = alertConfig {
                // Critical update with alert
                await activity.update(
                    .init(state: newState, staleDate: nil),
                    alertConfiguration: alertConfig
                )
                print("🔔 Updated Live Activity with alert for capsule: \(capsuleId)")
            } else {
                // Normal update
                await activity.update(.init(state: newState, staleDate: nil))
                print("✅ Updated Live Activity for capsule: \(capsuleId)")
            }
            
            // Update local state
            activityStates[capsuleId] = newState
            
        } catch {
            print("❌ Failed to update Live Activity: \(error.localizedDescription)")
        }
    }
    
    /// End a Live Activity
    /// - Parameters:
    ///   - capsuleId: Capsule identifier
    ///   - finalState: Optional final state to show before dismissal
    ///   - dismissalPolicy: When to remove from Lock Screen
    func endActivity(
        capsuleId: String,
        finalState: CapsuleAttributes.ContentState? = nil,
        dismissalPolicy: ActivityUIDismissalPolicy = .default
    ) async {
        guard let activity = activeActivities[capsuleId] else {
            print("⚠️ No active activity found for capsule: \(capsuleId)")
            return
        }
        
        do {
            if let finalState = finalState {
                // Update with final state before ending
                await activity.end(
                    .init(state: finalState, staleDate: nil),
                    dismissalPolicy: dismissalPolicy
                )
            } else {
                // End immediately
                await activity.end(nil, dismissalPolicy: dismissalPolicy)
            }
            
            // Remove from active activities
            activeActivities.removeValue(forKey: capsuleId)
            activityStates.removeValue(forKey: capsuleId)
            
            print("✅ Ended Live Activity for capsule: \(capsuleId)")
            
        } catch {
            print("❌ Failed to end Live Activity: \(error.localizedDescription)")
        }
    }
    
    /// End all active Live Activities
    func endAllActivities() async {
        for (capsuleId, _) in activeActivities {
            await endActivity(capsuleId: capsuleId)
        }
    }
    
    /// Get current state for a capsule
    func getState(for capsuleId: String) -> CapsuleAttributes.ContentState? {
        return activityStates[capsuleId]
    }
    
    /// Check if activity exists for capsule
    func hasActivity(for capsuleId: String) -> Bool {
        return activeActivities[capsuleId] != nil
    }
    
    // MARK: - Private Methods
    
    /// Observe existing activities on app launch
    private func observeExistingActivities() async {
        for activity in Activity<CapsuleAttributes>.activities {
            let capsuleId = activity.attributes.capsuleId
            activeActivities[capsuleId] = activity
            activityStates[capsuleId] = activity.content.state
            observeActivity(activity, capsuleId: capsuleId)
            
            // Get push token
            if let pushToken = activity.pushToken {
                await registerPushToken(pushToken, for: capsuleId)
            }
        }
        
        print("✅ Observed \(activeActivities.count) existing Live Activities")
    }
    
    /// Observe activity state changes
    private func observeActivity(_ activity: Activity<CapsuleAttributes>, capsuleId: String) {
        Task {
            for await state in activity.activityStateUpdates {
                switch state {
                case .active:
                    print("📱 Activity is active: \(capsuleId)")
                case .ended:
                    print("🔚 Activity ended: \(capsuleId)")
                    activeActivities.removeValue(forKey: capsuleId)
                    activityStates.removeValue(forKey: capsuleId)
                case .dismissed:
                    print("👋 Activity dismissed: \(capsuleId)")
                    activeActivities.removeValue(forKey: capsuleId)
                    activityStates.removeValue(forKey: capsuleId)
                case .stale:
                    print("⏰ Activity is stale: \(capsuleId)")
                @unknown default:
                    break
                }
            }
        }
        
        // Observe push token updates
        Task {
            for await pushToken in activity.pushTokenUpdates {
                await registerPushToken(pushToken, for: capsuleId)
            }
        }
    }
    
    /// Register push token with backend
    private func registerPushToken(_ token: Data, for capsuleId: String) async {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        print("🔑 Push token for \(capsuleId): \(tokenString)")
        
        // Send to capsule-gateway API
        await CapsuleAPIService.shared.registerPushToken(
            capsuleId: capsuleId,
            pushToken: tokenString
        )
    }
}

// MARK: - Helper Extensions

extension CapsuleManager {
    
    /// Create alert configuration for critical updates
    static func createAlertConfig(
        title: String,
        body: String,
        sound: AlertConfiguration.AlertSound = .default
    ) -> AlertConfiguration {
        return AlertConfiguration(
            title: .init(stringLiteral: title),
            body: .init(stringLiteral: body),
            sound: sound
        )
    }
    
    /// Create dismissal policy
    static func dismissalPolicy(after seconds: TimeInterval) -> ActivityUIDismissalPolicy {
        return .after(Date().addingTimeInterval(seconds))
    }
}
