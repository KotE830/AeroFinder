package com.aerofinder

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.aerofinder.ui.AirlinesScreen
import com.aerofinder.ui.AirlinesViewModel
import com.aerofinder.ui.DealsScreen
import com.aerofinder.ui.DealsViewModel
import com.aerofinder.ui.NoticesScreen
import com.aerofinder.ui.NoticesViewModel
import com.aerofinder.ui.theme.AeroFinderTheme

class MainActivity : ComponentActivity() {

    private val requestNotification = registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requestNotification.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
        enableEdgeToEdge()
        setContent {
            AeroFinderTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
                    Column(modifier = Modifier.fillMaxSize().statusBarsPadding()) {
                        TabRow(selectedTabIndex = selectedTab) {
                            Tab(
                                selected = selectedTab == 0,
                                onClick = { selectedTab = 0 },
                                text = { Text("이벤트") },
                            )
                            Tab(
                                selected = selectedTab == 1,
                                onClick = { selectedTab = 1 },
                                text = { Text("공지") },
                            )
                            Tab(
                                selected = selectedTab == 2,
                                onClick = { selectedTab = 2 },
                                text = { Text("항공사") },
                            )
                        }
                        Box(modifier = Modifier.fillMaxSize()) {
                            when (selectedTab) {
                                0 -> {
                                    val viewModel: DealsViewModel = viewModel()
                                    DealsScreen(viewModel = viewModel, modifier = Modifier.fillMaxSize())
                                }
                                1 -> {
                                    val viewModel: NoticesViewModel = viewModel()
                                    NoticesScreen(viewModel = viewModel, modifier = Modifier.fillMaxSize())
                                }
                                2 -> {
                                    val viewModel: AirlinesViewModel = viewModel()
                                    AirlinesScreen(viewModel = viewModel, modifier = Modifier.fillMaxSize())
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
