package com.aerofinder.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.aerofinder.data.Deal
import com.aerofinder.data.DealsRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.format.DateTimeParseException

data class DealsUiState(
    val ongoing: List<Deal> = emptyList(),
    val upcoming: List<Deal> = emptyList(),
    val expired: List<Deal> = emptyList(),
    val loading: Boolean = false,
    val error: String? = null,
)

class DealsViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = DealsRepository()

    private val _state = MutableStateFlow(DealsUiState())
    val state: StateFlow<DealsUiState> = _state.asStateFlow()

    init {
        loadDeals()
    }

    fun loadDeals() {
        viewModelScope.launch {
            _state.value = _state.value.copy(loading = true, error = null)
            repository.getDeals()
                .onSuccess { list ->
                    val now = Instant.now()
                    val ongoing = mutableListOf<Deal>()
                    val upcoming = mutableListOf<Deal>()
                    val expired = mutableListOf<Deal>()
                    for (deal in list) {
                        when (deal.periodStatus(now)) {
                            PeriodStatus.ONGOING, PeriodStatus.UNKNOWN -> ongoing.add(deal)
                            PeriodStatus.UPCOMING -> upcoming.add(deal)
                            PeriodStatus.PAST -> {
                                val end = deal.eventEnd?.parseInstant()
                                if (end != null) {
                                    val sevenDaysAgo = now.minus(7, java.time.temporal.ChronoUnit.DAYS)
                                    if (end.isAfter(sevenDaysAgo)) expired.add(deal)
                                }
                            }
                        }
                    }
                    _state.value = DealsUiState(
                        ongoing = ongoing,
                        upcoming = upcoming,
                        expired = expired,
                        loading = false,
                    )
                }
                .onFailure {
                    _state.value = _state.value.copy(
                        loading = false,
                        error = it.message ?: "오류 발생",
                    )
                }
        }
    }

    private enum class PeriodStatus { ONGOING, UPCOMING, PAST, UNKNOWN }

    private fun Deal.periodStatus(now: Instant): PeriodStatus {
        val start = eventStart?.parseInstant()
        val end = eventEnd?.parseInstant()
        if (start == null && end == null) return PeriodStatus.UNKNOWN
        if (end != null && end.isBefore(now)) return PeriodStatus.PAST
        if (start != null && start.isAfter(now)) return PeriodStatus.UPCOMING
        if (start != null && end != null && !start.isAfter(now) && !end.isBefore(now)) return PeriodStatus.ONGOING
        if (start == null && end != null && !end.isBefore(now)) return PeriodStatus.ONGOING
        if (start != null && !start.isAfter(now) && (end == null || !end.isBefore(now))) return PeriodStatus.ONGOING
        return PeriodStatus.UPCOMING
    }

    private fun String.parseInstant(): Instant? = try {
        val s = this.trim().replace(" ", "T")
        if (s.contains("+") || s.endsWith("Z")) Instant.parse(s)
        else Instant.parse(s.substringBefore(".").plus("Z"))
    } catch (_: DateTimeParseException) {
        null
    }
}

fun Deal.formatPeriod(): String {
    if (eventStart == null && eventEnd == null) return "기간 미정"
    return buildString {
        eventStart?.let { append(it.substringBefore("T")) }
        if (eventStart != null && eventEnd != null) append(" ~ ")
        eventEnd?.let { append(it.substringBefore("T")) }
    }.ifEmpty { "기간 미정" }
}
