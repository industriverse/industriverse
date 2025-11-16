//
//  IndustriverseCapsulesApp.swift
//  IndustriverseCapsules
//
//  Production-ready iOS app with Live Activities
//

import SwiftUI

@main
struct IndustriverseCapsulesApp: App {
    
    // MARK: - State
    
    @StateObject private var capsuleManager = CapsuleManager.shared
    
    // MARK: - Body
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(capsuleManager)
                .onAppear {
                    setupApp()
                }
        }
    }
    
    // MARK: - Setup
    
    private func setupApp() {
        // Configure API service
        Task {
            // In production, get auth token from secure storage
            if let token = UserDefaults.standard.string(forKey: "auth_token") {
                await CapsuleAPIService.shared.setAuthToken(token)
            }
            
            // Sync activities from backend
            await syncActivities()
        }
    }
    
    private func syncActivities() async {
        do {
            let activities = try await CapsuleAPIService.shared.fetchAllActivities()
            
            for activity in activities {
                // Start Live Activity if not already active
                if !capsuleManager.hasActivity(for: activity.capsuleId) {
                    try? await capsuleManager.startActivity(
                        capsuleId: activity.capsuleId,
                        type: activity.type,
                        title: activity.title,
                        iconName: activity.iconName,
                        primaryColor: activity.primaryColor,
                        initialState: activity.toContentState()
                    )
                }
            }
            
            print("✅ Synced \(activities.count) activities from backend")
        } catch {
            print("⚠️ Failed to sync activities: \(error.localizedDescription)")
        }
    }
}
