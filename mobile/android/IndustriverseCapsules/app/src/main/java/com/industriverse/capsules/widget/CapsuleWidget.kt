package com.industriverse.capsules.widget

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.glance.GlanceId
import androidx.glance.GlanceModifier
import androidx.glance.GlanceTheme
import androidx.glance.Image
import androidx.glance.ImageProvider
import androidx.glance.action.clickable
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.cornerRadius
import androidx.glance.appwidget.provideContent
import androidx.glance.background
import androidx.glance.layout.Alignment
import androidx.glance.layout.Box
import androidx.glance.layout.Column
import androidx.glance.layout.Row
import androidx.glance.layout.Spacer
import androidx.glance.layout.fillMaxSize
import androidx.glance.layout.fillMaxWidth
import androidx.glance.layout.height
import androidx.glance.layout.padding
import androidx.glance.layout.size
import androidx.glance.layout.width
import androidx.glance.text.FontWeight
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import com.industriverse.capsules.R
import com.industriverse.capsules.data.models.Capsule
import com.industriverse.capsules.data.models.CapsulePriority
import com.industriverse.capsules.data.models.CapsuleType

/**
 * Capsule Widget - Home Screen Widget Implementation
 * Week 13 Day 5-6: Home screen widgets using Glance
 *
 * Provides three widget sizes:
 * - Compact (1x1): Single capsule pill
 * - Expanded (2x2): 3-4 capsules in grid
 * - Full (4x2): Full launchpad with scrollable list
 */

/**
 * Compact Widget (1x1)
 * Shows the highest priority capsule as a pill
 */
class CompactCapsuleWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            GlanceTheme {
                CompactWidgetContent(getTopCapsule(context))
            }
        }
    }
}

@Composable
fun CompactWidgetContent(capsule: Capsule?) {
    Box(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(GlanceTheme.colors.background)
            .cornerRadius(16.dp)
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        if (capsule != null) {
            CapsulePill(capsule, compact = true)
        } else {
            EmptyWidgetState(compact = true)
        }
    }
}

/**
 * Expanded Widget (2x2)
 * Shows 3-4 capsules in a grid layout
 */
class ExpandedCapsuleWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            GlanceTheme {
                ExpandedWidgetContent(getActiveCapsules(context, limit = 4))
            }
        }
    }
}

@Composable
fun ExpandedWidgetContent(capsules: List<Capsule>) {
    Box(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(GlanceTheme.colors.background)
            .cornerRadius(16.dp)
            .padding(12.dp)
    ) {
        if (capsules.isNotEmpty()) {
            Column(
                modifier = GlanceModifier.fillMaxSize()
            ) {
                // Header
                WidgetHeader(capsuleCount = capsules.size)

                Spacer(GlanceModifier.height(8.dp))

                // Capsule grid (2x2)
                val rows = capsules.chunked(2)
                rows.forEach { rowCapsules ->
                    Row(
                        modifier = GlanceModifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.Horizontal.CenterHorizontally
                    ) {
                        rowCapsules.forEach { capsule ->
                            CapsulePill(capsule, compact = false)
                            if (rowCapsules.size == 2 && capsule != rowCapsules.last()) {
                                Spacer(GlanceModifier.width(8.dp))
                            }
                        }
                    }
                    if (rows.last() != rowCapsules) {
                        Spacer(GlanceModifier.height(8.dp))
                    }
                }
            }
        } else {
            EmptyWidgetState(compact = false)
        }
    }
}

/**
 * Full Widget (4x2)
 * Shows full launchpad with scrollable list of capsules
 */
class FullCapsuleWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            GlanceTheme {
                FullWidgetContent(getActiveCapsules(context, limit = 8))
            }
        }
    }
}

@Composable
fun FullWidgetContent(capsules: List<Capsule>) {
    Box(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(GlanceTheme.colors.background)
            .cornerRadius(16.dp)
            .padding(12.dp)
    ) {
        if (capsules.isNotEmpty()) {
            Column(
                modifier = GlanceModifier.fillMaxSize()
            ) {
                // Header with count
                Row(
                    modifier = GlanceModifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.Horizontal.Start,
                    verticalAlignment = Alignment.Vertical.CenterVertically
                ) {
                    Text(
                        text = "Capsules",
                        style = TextStyle(
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = GlanceTheme.colors.onBackground
                        )
                    )
                    Spacer(GlanceModifier.width(8.dp))
                    CountBadge(capsules.size)
                }

                Spacer(GlanceModifier.height(12.dp))

                // Capsule list (scrollable)
                capsules.take(8).forEach { capsule ->
                    CapsuleRow(capsule)
                    if (capsule != capsules.last()) {
                        Spacer(GlanceModifier.height(8.dp))
                    }
                }

                // Show "X more" if there are additional capsules
                if (capsules.size > 8) {
                    Spacer(GlanceModifier.height(8.dp))
                    Text(
                        text = "+${capsules.size - 8} more",
                        style = TextStyle(
                            fontSize = 12.sp,
                            color = GlanceTheme.colors.secondary
                        )
                    )
                }
            }
        } else {
            EmptyWidgetState(compact = false)
        }
    }
}

/**
 * Capsule Pill Component
 * Compact representation of a capsule for widgets
 */
@Composable
fun CapsulePill(capsule: Capsule, compact: Boolean) {
    val backgroundColor = getPriorityColor(capsule.priority)

    Box(
        modifier = GlanceModifier
            .then(if (compact) GlanceModifier.fillMaxSize() else GlanceModifier.size(80.dp, 40.dp))
            .background(backgroundColor)
            .cornerRadius(if (compact) 12.dp else 8.dp)
            .padding(if (compact) 8.dp else 6.dp)
            .clickable(onClick = actionOpenCapsule(capsule.capsuleId)),
        contentAlignment = Alignment.CenterStart
    ) {
        Column {
            Text(
                text = capsule.title,
                style = TextStyle(
                    fontSize = if (compact) 14.sp else 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = GlanceTheme.colors.onPrimary
                ),
                maxLines = 1
            )
            if (!compact && capsule.subtitle != null) {
                Text(
                    text = capsule.subtitle,
                    style = TextStyle(
                        fontSize = 10.sp,
                        color = GlanceTheme.colors.onPrimary
                    ),
                    maxLines = 1
                )
            }
        }
    }
}

/**
 * Capsule Row Component
 * Full-width row for the full widget
 */
@Composable
fun CapsuleRow(capsule: Capsule) {
    val backgroundColor = getPriorityColor(capsule.priority)
    val typeIcon = getTypeIcon(capsule.capsuleType)

    Row(
        modifier = GlanceModifier
            .fillMaxWidth()
            .background(backgroundColor)
            .cornerRadius(8.dp)
            .padding(10.dp)
            .clickable(onClick = actionOpenCapsule(capsule.capsuleId)),
        verticalAlignment = Alignment.Vertical.CenterVertically
    ) {
        // Type icon
        Image(
            provider = ImageProvider(typeIcon),
            contentDescription = capsule.capsuleType.name,
            modifier = GlanceModifier.size(20.dp)
        )

        Spacer(GlanceModifier.width(10.dp))

        // Capsule content
        Column(
            modifier = GlanceModifier.defaultWeight()
        ) {
            Text(
                text = capsule.title,
                style = TextStyle(
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    color = GlanceTheme.colors.onPrimary
                ),
                maxLines = 1
            )
            if (capsule.subtitle != null) {
                Text(
                    text = capsule.subtitle,
                    style = TextStyle(
                        fontSize = 11.sp,
                        color = GlanceTheme.colors.onPrimary
                    ),
                    maxLines = 1
                )
            }
        }

        // Priority indicator
        if (capsule.priority == CapsulePriority.CRITICAL || capsule.priority == CapsulePriority.HIGH) {
            Spacer(GlanceModifier.width(8.dp))
            PriorityIndicator(capsule.priority)
        }

        // Badge count
        if (capsule.badgeCount > 0) {
            Spacer(GlanceModifier.width(8.dp))
            CountBadge(capsule.badgeCount)
        }
    }
}

/**
 * Widget Header Component
 */
@Composable
fun WidgetHeader(capsuleCount: Int) {
    Row(
        modifier = GlanceModifier.fillMaxWidth(),
        horizontalAlignment = Alignment.Horizontal.CenterHorizontally,
        verticalAlignment = Alignment.Vertical.CenterVertically
    ) {
        Text(
            text = "Capsules",
            style = TextStyle(
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = GlanceTheme.colors.onBackground
            )
        )
        Spacer(GlanceModifier.width(6.dp))
        CountBadge(capsuleCount)
    }
}

/**
 * Empty Widget State
 */
@Composable
fun EmptyWidgetState(compact: Boolean) {
    Column(
        modifier = GlanceModifier.fillMaxSize(),
        horizontalAlignment = Alignment.Horizontal.CenterHorizontally,
        verticalAlignment = Alignment.Vertical.CenterVertically
    ) {
        Image(
            provider = ImageProvider(R.drawable.ic_notification),
            contentDescription = "No capsules",
            modifier = GlanceModifier.size(if (compact) 24.dp else 32.dp)
        )
        if (!compact) {
            Spacer(GlanceModifier.height(8.dp))
            Text(
                text = "No active capsules",
                style = TextStyle(
                    fontSize = 12.sp,
                    color = GlanceTheme.colors.secondary
                )
            )
        }
    }
}

/**
 * Count Badge Component
 */
@Composable
fun CountBadge(count: Int) {
    Box(
        modifier = GlanceModifier
            .background(GlanceTheme.colors.primary)
            .cornerRadius(10.dp)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = count.toString(),
            style = TextStyle(
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = GlanceTheme.colors.onPrimary
            )
        )
    }
}

/**
 * Priority Indicator Component
 */
@Composable
fun PriorityIndicator(priority: CapsulePriority) {
    Box(
        modifier = GlanceModifier
            .size(8.dp)
            .background(
                when (priority) {
                    CapsulePriority.CRITICAL -> androidx.glance.color.ColorProvider(android.graphics.Color.parseColor("#EF4444"))
                    CapsulePriority.HIGH -> androidx.glance.color.ColorProvider(android.graphics.Color.parseColor("#F59E0B"))
                    else -> androidx.glance.color.ColorProvider(android.graphics.Color.parseColor("#6B7280"))
                }
            )
            .cornerRadius(4.dp)
    )
}

/**
 * Helper Functions
 */

private fun getPriorityColor(priority: CapsulePriority): androidx.glance.color.ColorProvider {
    return androidx.glance.color.ColorProvider(
        when (priority) {
            CapsulePriority.CRITICAL -> android.graphics.Color.parseColor("#EF4444")
            CapsulePriority.HIGH -> android.graphics.Color.parseColor("#F59E0B")
            CapsulePriority.NORMAL -> android.graphics.Color.parseColor("#3B82F6")
            CapsulePriority.LOW -> android.graphics.Color.parseColor("#6B7280")
        }
    )
}

private fun getTypeIcon(type: CapsuleType): Int {
    return when (type) {
        CapsuleType.TASK -> R.drawable.ic_task
        CapsuleType.WORKFLOW -> R.drawable.ic_workflow
        CapsuleType.ALERT -> R.drawable.ic_alert
        CapsuleType.STATUS -> R.drawable.ic_status
        CapsuleType.DECISION -> R.drawable.ic_decision
        CapsuleType.CUSTOM -> R.drawable.ic_custom
    }
}

/**
 * Data fetching helpers
 * In production, these would query the local Room database
 */
private fun getTopCapsule(context: Context): Capsule? {
    // TODO: Query Room database for highest priority capsule
    // For now, return mock data
    return null
}

private fun getActiveCapsules(context: Context, limit: Int): List<Capsule> {
    // TODO: Query Room database for active capsules
    // For now, return mock data
    return emptyList()
}

/**
 * Widget Actions
 */
private fun actionOpenCapsule(capsuleId: String): androidx.glance.action.Action {
    // TODO: Implement action to open capsule in app
    return androidx.glance.action.action {}
}
