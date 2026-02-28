package com.aerofinder.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.Icon
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aerofinder.data.Deal

@Composable
fun DealsScreen(
    viewModel: DealsViewModel,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    var isOngoingExpanded by remember { mutableStateOf(true) }
    var isUpcomingExpanded by remember { mutableStateOf(true) }
    var isExpiredExpanded by remember { mutableStateOf(true) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.loading && state.ongoing.isEmpty() && state.upcoming.isEmpty() && state.expired.isEmpty()) {
            item {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    CircularProgressIndicator()
                    Text("로딩 중...", modifier = Modifier.padding(top = 8.dp))
                }
            }
            return@LazyColumn
        }

        state.error?.let { msg ->
            item {
                Text("오류: $msg", color = MaterialTheme.colorScheme.error)
            }
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { isOngoingExpanded = !isOngoingExpanded }
                    .padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("진행 중인 이벤트 (${state.ongoing.size})", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Icon(
                    imageVector = if (isOngoingExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = if (isOngoingExpanded) "접기" else "펼치기"
                )
            }
        }
        if (isOngoingExpanded) {
            if (state.ongoing.isEmpty()) {
                item { Text("진행 중인 이벤트가 없습니다.", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(bottom = 8.dp)) }
            } else {
                items(state.ongoing, key = { it.id }) { deal ->
                    DealItem(deal = deal, onClick = { openUrl(context, deal.url) }, isOngoing = true)
                }
            }
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { isUpcomingExpanded = !isUpcomingExpanded }
                    .padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("진행 예정인 이벤트 (${state.upcoming.size})", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Icon(
                    imageVector = if (isUpcomingExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = if (isUpcomingExpanded) "접기" else "펼치기"
                )
            }
        }
        if (isUpcomingExpanded) {
            if (state.upcoming.isEmpty()) {
                item { Text("진행 예정인 이벤트가 없습니다.", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(bottom = 8.dp)) }
            } else {
                items(state.upcoming, key = { it.id }) { deal ->
                    DealItem(deal = deal, onClick = { openUrl(context, deal.url) })
                }
            }
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { isExpiredExpanded = !isExpiredExpanded }
                    .padding(vertical = 8.dp, horizontal = 0.dp)
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("종료된 이벤트 (${state.expired.size})", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha=0.6f))
                Icon(
                    imageVector = if (isExpiredExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = if (isExpiredExpanded) "접기" else "펼치기",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha=0.6f)
                )
            }
        }
        if (isExpiredExpanded) {
            if (state.expired.isEmpty()) {
                item { Text("최근 종료된 이벤트가 없습니다.", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(bottom = 8.dp), color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha=0.6f)) }
            } else {
                items(state.expired, key = { it.id }) { deal ->
                    DealItem(deal = deal, onClick = { openUrl(context, deal.url) }, isExpired = true)
                }
            }
        }
    }
}

@Composable
private fun DealItem(
    deal: Deal,
    onClick: () -> Unit,
    isOngoing: Boolean = false,
    isExpired: Boolean = false,
) {
    val alpha = if (isExpired) 0.5f else 1f
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = if (isOngoing) MaterialTheme.colorScheme.primaryContainer else if (isExpired) MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = if (isExpired) 0.dp else 2.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(deal.airline, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary.copy(alpha = alpha))
            Text(deal.title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface.copy(alpha = alpha))
            Text(deal.formatPeriod(), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = alpha))
        }
    }
}

private fun openUrl(context: android.content.Context, url: String) {
    try {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    } catch (_: Exception) { }
}
