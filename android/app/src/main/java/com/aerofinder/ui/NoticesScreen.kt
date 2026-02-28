package com.aerofinder.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import com.aerofinder.data.Notice

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NoticesScreen(
    viewModel: NoticesViewModel,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    var airlineDropdownExpanded by remember { mutableStateOf(false) }
    val selectedAirlineName = state.airlines.find { it.id == state.selectedAirlineId }?.name ?: "항공사"

    Column(modifier = modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            FilterChip(
                selected = state.filter == NoticeFilter.ALL,
                onClick = { viewModel.setFilterAll() },
                label = { Text("전체") },
            )
            FilterChip(
                selected = state.filter == NoticeFilter.SPECIAL_DEAL,
                onClick = { viewModel.setFilterSpecialDeal() },
                label = { Text("특가") },
            )
            ExposedDropdownMenuBox(
                expanded = airlineDropdownExpanded,
                onExpandedChange = { airlineDropdownExpanded = it },
            ) {
                FilterChip(
                    modifier = Modifier.menuAnchor(),
                    selected = state.filter == NoticeFilter.AIRLINE,
                    onClick = { airlineDropdownExpanded = true },
                    label = { Text(if (state.filter == NoticeFilter.AIRLINE) selectedAirlineName else "항공사") },
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = airlineDropdownExpanded) },
                )
                ExposedDropdownMenu(
                    expanded = airlineDropdownExpanded,
                    onDismissRequest = { airlineDropdownExpanded = false },
                ) {
                    state.airlines.forEach { airline ->
                        DropdownMenuItem(
                            text = { Text(airline.name) },
                            onClick = {
                                viewModel.setFilterAirline(airline.id)
                                airlineDropdownExpanded = false
                            },
                        )
                    }
                }
            }
        }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.loading && state.notices.isEmpty()) {
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

        if (state.notices.isEmpty() && !state.loading) {
            item {
                Text(
                    "공지가 없습니다. 크롤링이 진행되면 표시됩니다.",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 16.dp),
                )
            }
            return@LazyColumn
        }

        items(state.notices, key = { it.id }) { notice ->
            val isRead = notice.id in state.readNoticeIds
            NoticeItem(
                notice = notice,
                isNew = !isRead,
                onClick = {
                    viewModel.markAsRead(notice.id)
                    openUrl(context, notice.sourceUrl)
                },
            )
        }
    }
    }
}

@Composable
private fun NoticeItem(
    notice: Notice,
    isNew: Boolean,
    onClick: () -> Unit,
) {
    val containerColor = if (isNew) {
        MaterialTheme.colorScheme.errorContainer
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }
    val displayTitle = notice.displayTitle()
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = containerColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                displayTitle,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Row(
                modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    notice.airline,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.primary,
                )
                if (notice.isSpecialDeal) {
                    Surface(
                        shape = MaterialTheme.shapes.small,
                        color = MaterialTheme.colorScheme.primaryContainer,
                    ) {
                        Text(
                            "특가",
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        )
                    }
                }
            }
            Text(
                notice.formatPeriod(),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 2.dp),
            )
        }
    }
}

private fun Notice.displayTitle(): String {
    if (title.isNotBlank() && title != airline) return title
    val path = sourceUrl.trimEnd('/')
    val lastSegment = path.substringAfterLast("/").takeIf { it.isNotBlank() }
    return lastSegment ?: "공지"
}

private fun Notice.formatPeriod(): String {
    if (eventStart == null && eventEnd == null) return "기간 미정"
    return buildString {
        eventStart?.let { append(it.substringBefore("T")) }
        if (eventStart != null && eventEnd != null) append(" ~ ")
        eventEnd?.let { append(it.substringBefore("T")) }
    }.ifEmpty { "기간 미정" }
}

private fun openUrl(context: android.content.Context, url: String) {
    try {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    } catch (_: Exception) { }
}
