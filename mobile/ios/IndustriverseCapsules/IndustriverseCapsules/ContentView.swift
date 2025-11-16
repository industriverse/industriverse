//
//  ContentView.swift
//  IndustriverseCapsules
//
//  Main view showing active capsules and Live Activities
//

import SwiftUI
import ActivityKit

struct ContentView: View {
    
    // MARK: - Environment
    
    @EnvironmentObject var capsuleManager: CapsuleManager
    
    // MARK: - State
    
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                if capsuleManager.activeActivities.isEmpty {
                    emptyState
                } else {
                    activityList
                }
                
                if isLoading {
                    ProgressView()
                }
            }
            .navigationTitle("Capsule Pins")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: refreshActivities) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: createTestActivity) {
                        Image(systemName: "plus")
                    }
                }
            }
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK") {
                    errorMessage = nil
                }
            } message: {
                if let error = errorMessage {
                    Text(error)
                }
            }
        }
    }
    
    // MARK: - Views
    
    private var emptyState: some View {
        VStack(spacing: 20) {
            Image(systemName: "tray")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("No Active Capsules")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Create a test capsule or wait for activities from the backend")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            Button(action: createTestActivity) {
                Label("Create Test Capsule", systemImage: "plus.circle.fill")
                    .font(.headline)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
        }
    }
    
    private var activityList: some View {
        List {
            ForEach(Array(capsuleManager.activeActivities.keys.sorted()), id: \.self) { capsuleId in
                if let activity = capsuleManager.activeActivities[capsuleId],
                   let state = capsuleManager.activityStates[capsuleId] {
                    CapsuleRow(
                        attributes: activity.attributes,
                        state: state,
                        onUpdate: { newState in
                            await updateActivity(capsuleId: capsuleId, state: newState)
                        },
                        onEnd: {
                            await endActivity(capsuleId: capsuleId)
                        }
                    )
                }
            }
        }
    }
    
    // MARK: - Actions
    
    private func refreshActivities() {
        isLoading = true
        Task {
            do {
                let activities = try await CapsuleAPIService.shared.fetchAllActivities()
                
                for activity in activities {
                    if capsuleManager.hasActivity(for: activity.capsuleId) {
                        // Update existing
                        await capsuleManager.updateActivity(
                            capsuleId: activity.capsuleId,
                            newState: activity.toContentState()
                        )
                    } else {
                        // Create new
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
                
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    private func createTestActivity() {
        Task {
            let capsuleId = "test-\(UUID().uuidString.prefix(8))"
            let initialState = CapsuleAttributes.ContentState(
                status: "active",
                statusMessage: "Test capsule created from iOS app",
                progress: 0.5,
                metricValue: "100%",
                metricLabel: "Health",
                lastUpdated: Date(),
                actionCount: 2,
                priority: 3,
                isStale: false,
                alertMessage: nil
            )
            
            try? await capsuleManager.startActivity(
                capsuleId: capsuleId,
                type: "test",
                title: "Test Capsule",
                iconName: "sparkles",
                primaryColor: "blue",
                initialState: initialState
            )
        }
    }
    
    private func updateActivity(capsuleId: String, state: CapsuleAttributes.ContentState) async {
        await capsuleManager.updateActivity(capsuleId: capsuleId, newState: state)
    }
    
    private func endActivity(capsuleId: String) async {
        await capsuleManager.endActivity(capsuleId: capsuleId)
    }
}

// MARK: - Capsule Row

struct CapsuleRow: View {
    let attributes: CapsuleAttributes
    let state: CapsuleAttributes.ContentState
    let onUpdate: (CapsuleAttributes.ContentState) async -> Void
    let onEnd: () async -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: attributes.getTypeIcon())
                    .font(.title2)
                    .foregroundColor(attributes.getColor())
                    .frame(width: 40, height: 40)
                    .background(attributes.getColor().opacity(0.2))
                    .cornerRadius(8)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(attributes.title)
                        .font(.headline)
                    
                    HStack {
                        Image(systemName: state.statusIcon)
                            .font(.caption2)
                            .foregroundColor(state.statusColor)
                        Text(state.status.capitalized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                Text(state.priorityLabel)
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(state.priorityColor)
                    .cornerRadius(6)
            }
            
            Text(state.statusMessage)
                .font(.subheadline)
                .foregroundColor(.primary)
                .lineLimit(2)
            
            if state.progress > 0 {
                ProgressView(value: state.progress)
                    .progressViewStyle(.linear)
                    .tint(attributes.getColor())
            }
            
            HStack {
                Button(action: { Task { await onUpdate(createUpdatedState()) } }) {
                    Label("Update", systemImage: "arrow.clockwise")
                        .font(.caption)
                }
                .buttonStyle(.bordered)
                
                Button(role: .destructive, action: { Task { await onEnd() } }) {
                    Label("End", systemImage: "xmark")
                        .font(.caption)
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(.vertical, 8)
    }
    
    private func createUpdatedState() -> CapsuleAttributes.ContentState {
        var newState = state
        newState.progress = min(state.progress + 0.1, 1.0)
        newState.lastUpdated = Date()
        newState.statusMessage = "Updated at \(Date().formatted(date: .omitted, time: .shortened))"
        return newState
    }
}

// MARK: - Preview

#Preview {
    ContentView()
        .environmentObject(CapsuleManager.shared)
}
