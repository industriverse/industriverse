//
//  CapsuleAttributes.swift
//  IndustriverseCapsules
//
//  Created by Industriverse
//  Production-ready ActivityKit implementation
//

import Foundation
import ActivityKit
import SwiftUI

/// Defines the static and dynamic data for Capsule Live Activities
/// Following Apple's ActivityAttributes protocol
struct CapsuleAttributes: ActivityAttributes {
    
    // MARK: - Static Attributes (Set once, never change)
    
    /// Unique identifier for the capsule
    let capsuleId: String
    
    /// Capsule type (e.g., "security", "performance", "discovery")
    let capsuleType: String
    
    /// Capsule title
    let title: String
    
    /// Icon name (SF Symbol or custom)
    let iconName: String
    
    /// Primary color theme
    let primaryColor: String
    
    /// Created timestamp
    let createdAt: Date
    
    // MARK: - Dynamic Content State
    
    /// Dynamic data that changes over time
    struct ContentState: Codable, Hashable {
        /// Current status (e.g., "active", "pending", "resolved")
        var status: String
        
        /// Status message
        var statusMessage: String
        
        /// Progress value (0.0 to 1.0)
        var progress: Double
        
        /// Current metric value
        var metricValue: String
        
        /// Metric label
        var metricLabel: String
        
        /// Timestamp of last update
        var lastUpdated: Date
        
        /// Action count (e.g., number of pending actions)
        var actionCount: Int
        
        /// Priority level (1-5, where 5 is highest)
        var priority: Int
        
        /// Whether the activity is stale (no updates for a while)
        var isStale: Bool
        
        /// Optional alert message for critical updates
        var alertMessage: String?
    }
    
    // MARK: - Helper Methods
    
    /// Get SwiftUI Color from string
    func getColor() -> Color {
        switch primaryColor.lowercased() {
        case "red": return .red
        case "orange": return .orange
        case "yellow": return .yellow
        case "green": return .green
        case "blue": return .blue
        case "purple": return .purple
        case "pink": return .pink
        default: return .blue
        }
    }
    
    /// Get SF Symbol for capsule type
    func getTypeIcon() -> String {
        switch capsuleType.lowercased() {
        case "security": return "shield.fill"
        case "performance": return "gauge.high"
        case "discovery": return "sparkles"
        case "alert": return "exclamationmark.triangle.fill"
        case "success": return "checkmark.circle.fill"
        default: return iconName
        }
    }
}

// MARK: - Priority Extension

extension CapsuleAttributes.ContentState {
    /// Get color based on priority
    var priorityColor: Color {
        switch priority {
        case 5: return .red
        case 4: return .orange
        case 3: return .yellow
        case 2: return .blue
        default: return .gray
        }
    }
    
    /// Get priority label
    var priorityLabel: String {
        switch priority {
        case 5: return "Critical"
        case 4: return "High"
        case 3: return "Medium"
        case 2: return "Low"
        default: return "Info"
        }
    }
}

// MARK: - Status Extension

extension CapsuleAttributes.ContentState {
    /// Get status icon
    var statusIcon: String {
        switch status.lowercased() {
        case "active": return "circle.fill"
        case "pending": return "clock.fill"
        case "resolved": return "checkmark.circle.fill"
        case "error": return "xmark.circle.fill"
        default: return "circle"
        }
    }
    
    /// Get status color
    var statusColor: Color {
        switch status.lowercased() {
        case "active": return .green
        case "pending": return .orange
        case "resolved": return .blue
        case "error": return .red
        default: return .gray
        }
    }
}
