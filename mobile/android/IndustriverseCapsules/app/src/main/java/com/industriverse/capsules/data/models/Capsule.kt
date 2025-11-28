package com.industriverse.capsules.data.models

import com.google.gson.annotations.SerializedName
import java.util.Date

/**
 * Data models for Deploy Anywhere Capsules (DACs)
 * Week 13: Android Native Implementation
 */

/**
 * Main Capsule data class representing a DAC instance
 */
data class Capsule(
    @SerializedName("capsule_id")
    val capsuleId: String,

    @SerializedName("capsule_type")
    val capsuleType: CapsuleType,

    @SerializedName("title")
    val title: String,

    @SerializedName("subtitle")
    val subtitle: String? = null,

    @SerializedName("description")
    val description: String? = null,

    @SerializedName("priority")
    val priority: CapsulePriority = CapsulePriority.NORMAL,

    @SerializedName("state")
    val state: CapsuleState,

    @SerializedName("utid")
    val utid: String? = null,

    @SerializedName("proof")
    val proof: CapsuleProof? = null,

    @SerializedName("energy_signature")
    val energySignature: EnergySignature? = null,

    @SerializedName("actions")
    val actions: List<CapsuleAction> = emptyList(),

    @SerializedName("metadata")
    val metadata: Map<String, Any> = emptyMap(),

    @SerializedName("created_at")
    val createdAt: Date,

    @SerializedName("updated_at")
    val updatedAt: Date,

    @SerializedName("expires_at")
    val expiresAt: Date? = null,

    // UI-specific fields
    @SerializedName("icon")
    val icon: String? = null,

    @SerializedName("color")
    val color: String? = null,

    @SerializedName("badge_count")
    val badgeCount: Int = 0,

    @SerializedName("progress")
    val progress: Float? = null,

    @SerializedName("is_pinned")
    val isPinned: Boolean = false,

    @SerializedName("is_read")
    val isRead: Boolean = false
) {
    /**
     * Get display color with fallback
     */
    fun getDisplayColor(): String = color ?: when (capsuleType) {
        CapsuleType.ALERT -> "#EF4444"
        CapsuleType.TASK -> "#3B82F6"
        CapsuleType.WORKFLOW -> "#8B5CF6"
        CapsuleType.STATUS -> "#10B981"
        CapsuleType.DECISION -> "#F59E0B"
        CapsuleType.CUSTOM -> "#6B7280"
    }

    /**
     * Check if capsule requires attention
     */
    fun requiresAttention(): Boolean = when {
        priority == CapsulePriority.CRITICAL -> true
        priority == CapsulePriority.HIGH && !isRead -> true
        state == CapsuleState.ERROR -> true
        badgeCount > 0 -> true
        else -> false
    }

    /**
     * Check if capsule is expired
     */
    fun isExpired(): Boolean = expiresAt?.let { it.before(Date()) } ?: false
}

/**
 * Capsule types enum
 */
enum class CapsuleType {
    @SerializedName("task")
    TASK,

    @SerializedName("workflow")
    WORKFLOW,

    @SerializedName("alert")
    ALERT,

    @SerializedName("status")
    STATUS,

    @SerializedName("decision")
    DECISION,

    @SerializedName("custom")
    CUSTOM
}

/**
 * Capsule priority levels
 */
enum class CapsulePriority {
    @SerializedName("low")
    LOW,

    @SerializedName("normal")
    NORMAL,

    @SerializedName("high")
    HIGH,

    @SerializedName("critical")
    CRITICAL
}

/**
 * Capsule state enum
 */
enum class CapsuleState {
    @SerializedName("pending")
    PENDING,

    @SerializedName("active")
    ACTIVE,

    @SerializedName("in_progress")
    IN_PROGRESS,

    @SerializedName("completed")
    COMPLETED,

    @SerializedName("dismissed")
    DISMISSED,

    @SerializedName("error")
    ERROR,

    @SerializedName("expired")
    EXPIRED
}

/**
 * Capsule proof data (zk-SNARK)
 */
data class CapsuleProof(
    @SerializedName("proof_hash")
    val proofHash: String,

    @SerializedName("blockchain_tx")
    val blockchainTx: String? = null,

    @SerializedName("verified")
    val verified: Boolean = false,

    @SerializedName("lineage")
    val lineage: List<String> = emptyList()
)

/**
 * Energy signature for thermodynamic tracking
 */
data class EnergySignature(
    @SerializedName("e_state")
    val eState: Float,

    @SerializedName("de_dt")
    val deDt: Float,

    @SerializedName("s_state")
    val sState: Float,

    @SerializedName("timestamp")
    val timestamp: Date
)

/**
 * Capsule action (buttons, commands)
 */
data class CapsuleAction(
    @SerializedName("action_id")
    val actionId: String,

    @SerializedName("label")
    val label: String,

    @SerializedName("icon")
    val icon: String? = null,

    @SerializedName("action_type")
    val actionType: ActionType,

    @SerializedName("is_primary")
    val isPrimary: Boolean = false,

    @SerializedName("is_destructive")
    val isDestructive: Boolean = false,

    @SerializedName("requires_confirmation")
    val requiresConfirmation: Boolean = false
)

/**
 * Action types
 */
enum class ActionType {
    @SerializedName("complete")
    COMPLETE,

    @SerializedName("dismiss")
    DISMISS,

    @SerializedName("acknowledge")
    ACKNOWLEDGE,

    @SerializedName("approve")
    APPROVE,

    @SerializedName("reject")
    REJECT,

    @SerializedName("open")
    OPEN,

    @SerializedName("custom")
    CUSTOM
}

/**
 * Capsule update event from WebSocket
 */
data class CapsuleUpdate(
    @SerializedName("event_type")
    val eventType: UpdateEventType,

    @SerializedName("capsule_id")
    val capsuleId: String,

    @SerializedName("capsule")
    val capsule: Capsule? = null,

    @SerializedName("changes")
    val changes: Map<String, Any> = emptyMap(),

    @SerializedName("timestamp")
    val timestamp: Date
)

/**
 * Update event types
 */
enum class UpdateEventType {
    @SerializedName("created")
    CREATED,

    @SerializedName("updated")
    UPDATED,

    @SerializedName("deleted")
    DELETED,

    @SerializedName("state_changed")
    STATE_CHANGED,

    @SerializedName("action_completed")
    ACTION_COMPLETED
}

/**
 * Capsule list response from API
 */
data class CapsuleListResponse(
    @SerializedName("capsules")
    val capsules: List<Capsule>,

    @SerializedName("total_count")
    val totalCount: Int,

    @SerializedName("has_more")
    val hasMore: Boolean = false
)

/**
 * Action execution request
 */
data class ActionExecutionRequest(
    @SerializedName("action_id")
    val actionId: String,

    @SerializedName("capsule_id")
    val capsuleId: String,

    @SerializedName("user_id")
    val userId: String,

    @SerializedName("metadata")
    val metadata: Map<String, Any> = emptyMap()
)

/**
 * Action execution response
 */
data class ActionExecutionResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("message")
    val message: String? = null,

    @SerializedName("updated_capsule")
    val updatedCapsule: Capsule? = null
)
