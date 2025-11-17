package com.industriverse.capsules.ui

import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.industriverse.capsules.data.models.Capsule
import com.industriverse.capsules.service.CapsuleService
import com.industriverse.capsules.service.ConnectionState
import com.industriverse.capsules.service.WebSocketManager
import dagger.hilt.android.AndroidEntryPoint
import timber.log.Timber
import javax.inject.Inject

/**
 * Main Activity for Industriverse Capsules
 * Week 13: Android Native Implementation
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var webSocketManager: WebSocketManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Timber.d("MainActivity onCreate")

        // Start Capsule Service
        startCapsuleService()

        setContent {
            MaterialTheme {
                CapsuleScreen(webSocketManager)
            }
        }
    }

    private fun startCapsuleService() {
        val intent = Intent(this, CapsuleService::class.java).apply {
            action = CapsuleService.ACTION_START_SERVICE
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}

@Composable
fun CapsuleScreen(webSocketManager: WebSocketManager) {
    val connectionState by webSocketManager.connectionState.collectAsState()
    val capsules by webSocketManager.activeCapsules.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Capsules") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Connection status
            ConnectionStatusBar(connectionState)

            // Capsule list
            if (capsules.isEmpty()) {
                EmptyState()
            } else {
                CapsuleList(capsules)
            }
        }
    }
}

@Composable
fun ConnectionStatusBar(connectionState: ConnectionState) {
    val (text, color) = when (connectionState) {
        is ConnectionState.Connected -> "Connected" to Color.Green
        is ConnectionState.Connecting -> "Connecting..." to Color.Yellow
        is ConnectionState.Disconnected -> "Disconnected" to Color.Gray
        is ConnectionState.Error -> "Error: ${connectionState.message}" to Color.Red
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = color.copy(alpha = 0.2f)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(8.dp),
            style = MaterialTheme.typography.bodySmall
        )
    }
}

@Composable
fun EmptyState() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "No active capsules",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun CapsuleList(capsules: List<Capsule>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(capsules, key = { it.capsuleId }) { capsule ->
            CapsuleCard(capsule)
        }
    }
}

@Composable
fun CapsuleCard(capsule: Capsule) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = capsule.title,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            capsule.subtitle?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Priority badge
                PriorityBadge(capsule.priority.name)

                // Type badge
                TypeBadge(capsule.capsuleType.name)

                Spacer(modifier = Modifier.weight(1f))

                // Badge count
                if (capsule.badgeCount > 0) {
                    Badge {
                        Text(capsule.badgeCount.toString())
                    }
                }
            }
        }
    }
}

@Composable
fun PriorityBadge(priority: String) {
    val color = when (priority) {
        "CRITICAL" -> Color.Red
        "HIGH" -> Color.Orange
        "NORMAL" -> Color.Blue
        "LOW" -> Color.Gray
        else -> Color.Gray
    }

    Surface(
        color = color.copy(alpha = 0.2f),
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = priority,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}

@Composable
fun TypeBadge(type: String) {
    Surface(
        color = MaterialTheme.colorScheme.secondaryContainer,
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = type,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall
        )
    }
}
