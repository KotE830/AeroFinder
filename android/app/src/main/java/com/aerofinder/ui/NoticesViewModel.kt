package com.aerofinder.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.aerofinder.data.Airline
import com.aerofinder.data.AirlinesRepository
import com.aerofinder.data.Notice
import com.aerofinder.data.NoticesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** 공지 필터: 전체 / 특가만 / 특정 항공사 */
enum class NoticeFilter {
    ALL,
    SPECIAL_DEAL,
    AIRLINE,
}

data class NoticesUiState(
    val notices: List<Notice> = emptyList(),
    val readNoticeIds: Set<String> = emptySet(),
    val loading: Boolean = false,
    val error: String? = null,
    val filter: NoticeFilter = NoticeFilter.ALL,
    val selectedAirlineId: String? = null,
    val airlines: List<Airline> = emptyList(),
)

private const val PREFS_NAME = "notices_read"
private const val KEY_READ_IDS = "read_notice_ids"

class NoticesViewModel(application: Application) : AndroidViewModel(application) {

    private val noticesRepository = NoticesRepository()
    private val airlinesRepository = AirlinesRepository()
    private val prefs = application.applicationContext.getSharedPreferences(PREFS_NAME, 0)

    private val _state = MutableStateFlow(NoticesUiState(readNoticeIds = loadReadIds()))
    val state: StateFlow<NoticesUiState> = _state.asStateFlow()

    private fun loadReadIds(): Set<String> {
        return prefs.getStringSet(KEY_READ_IDS, null) ?: emptySet()
    }

    private fun saveReadIds(ids: Set<String>) {
        prefs.edit().putStringSet(KEY_READ_IDS, ids).apply()
    }

    init {
        loadAirlines()
        loadNotices()
    }

    private fun loadAirlines() {
        viewModelScope.launch {
            airlinesRepository.getAirlines()
                .onSuccess { list ->
                    _state.value = _state.value.copy(airlines = list)
                }
                .onFailure { }
        }
    }

    fun loadNotices() {
        viewModelScope.launch {
            val filter = _state.value.filter
            val airlineId = if (filter == NoticeFilter.AIRLINE) _state.value.selectedAirlineId else null
            val specialOnly = filter == NoticeFilter.SPECIAL_DEAL

            _state.value = _state.value.copy(loading = true, error = null)
            noticesRepository.getNotices(airlineId = airlineId, specialDealOnly = specialOnly)
                .onSuccess { list ->
                    _state.value = _state.value.copy(
                        notices = list,
                        loading = false,
                        readNoticeIds = loadReadIds(),
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

    fun setFilterAll() {
        if (_state.value.filter == NoticeFilter.ALL) return
        _state.value = _state.value.copy(filter = NoticeFilter.ALL, selectedAirlineId = null)
        loadNotices()
    }

    fun setFilterSpecialDeal() {
        if (_state.value.filter == NoticeFilter.SPECIAL_DEAL) return
        _state.value = _state.value.copy(filter = NoticeFilter.SPECIAL_DEAL, selectedAirlineId = null)
        loadNotices()
    }

    fun setFilterAirline(airlineId: String?) {
        if (_state.value.filter == NoticeFilter.AIRLINE && _state.value.selectedAirlineId == airlineId) return
        _state.value = _state.value.copy(filter = NoticeFilter.AIRLINE, selectedAirlineId = airlineId)
        loadNotices()
    }

    /** 클릭해서 확인한 공지 → 읽음 처리(배경 회색으로 복귀) */
    fun markAsRead(noticeId: String) {
        val newSet = _state.value.readNoticeIds + noticeId
        saveReadIds(newSet)
        _state.value = _state.value.copy(readNoticeIds = newSet)
    }
}
