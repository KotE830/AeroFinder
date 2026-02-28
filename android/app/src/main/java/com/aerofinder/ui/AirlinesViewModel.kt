package com.aerofinder.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.aerofinder.data.Airline
import com.aerofinder.data.AirlinesRepository
import com.aerofinder.data.PreferencesManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class AirlinesUiState(
    val airlines: List<Airline> = emptyList(),
    val loading: Boolean = false,
    val error: String? = null,
    val appNotificationEnabled: Boolean = true,
    val airlinePreferences: Map<String, Boolean> = emptyMap()
)

class AirlinesViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AirlinesRepository()
    private val prefs = PreferencesManager(application)

    private val _state = MutableStateFlow(AirlinesUiState())
    val state: StateFlow<AirlinesUiState> = _state.asStateFlow()

    init {
        loadAirlines()
    }

    fun loadAirlines() {
        viewModelScope.launch {
            _state.value = _state.value.copy(loading = true, error = null)
            repository.getAirlines()
                .onSuccess { list ->
                    val prefsMap = list.associate { it.id to prefs.isAirlineNotificationEnabled(it.id) }
                    _state.value = AirlinesUiState(
                        airlines = list, 
                        loading = false,
                        appNotificationEnabled = prefs.isAppNotificationEnabled,
                        airlinePreferences = prefsMap
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

    fun toggleAppNotification(enabled: Boolean) {
        prefs.isAppNotificationEnabled = enabled
        _state.value = _state.value.copy(appNotificationEnabled = enabled)
    }

    fun toggleAirlineNotification(airlineId: String, enabled: Boolean) {
        prefs.setAirlineNotificationEnabled(airlineId, enabled)
        val newMap = _state.value.airlinePreferences.toMutableMap()
        newMap[airlineId] = enabled
        _state.value = _state.value.copy(airlinePreferences = newMap)
    }
}
