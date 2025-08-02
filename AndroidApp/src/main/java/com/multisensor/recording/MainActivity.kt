package com.multisensor.recording

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityMainBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.SystemHealthStatus
import com.multisensor.recording.ui.SettingsActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Streamlined Material Design 3 Dashboard
 * 
 * Minimalist research data collection interface:
 * - Single-screen dashboard with organized sections
 * - Live video preview and recording controls at top
 * - System status and quick actions below
 * - Optimized for one-handed field operation
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Initialize binding and ViewModel
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize app: ${e.message}")
            return
        }

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        binding.toolbar.title = "Multi-Sensor Recording"
        
        // Setup recording controls
        setupRecordingControls()
        
        // Setup device status indicators
        setupDeviceStatus()
        
        // Setup quick actions
        setupQuickActions()
        
        // Setup toolbar menu
        setupToolbarMenu()
    }

    private fun setupRecordingControls() {
        binding.recordButton.setOnClickListener {
            try {
                if (viewModel.uiState.value.isRecording) {
                    viewModel.stopRecording()
                } else {
                    viewModel.startRecording()
                }
            } catch (e: Exception) {
                showError("Recording control failed: ${e.message}")
            }
        }
        
        // Camera switch button
        binding.cameraSwitchButton.setOnClickListener {
            try {
                // Use existing method if available
                showMessage("Camera switch requested")
            } catch (e: Exception) {
                showError("Camera switch failed: ${e.message}")
            }
        }
    }

    private fun setupDeviceStatus() {
        // PC connection
        binding.pcConnectionButton.setOnClickListener {
            try {
                showMessage("PC connection requested")
            } catch (e: Exception) {
                showError("PC connection failed: ${e.message}")
            }
        }
        
        // Shimmer connection
        binding.shimmerConnectionButton.setOnClickListener {
            try {
                if (viewModel.uiState.value.isShimmerConnected) {
                    viewModel.disconnectShimmer()
                } else {
                    viewModel.connectShimmer()
                }
            } catch (e: Exception) {
                showError("Shimmer connection failed: ${e.message}")
            }
        }
        
        // Thermal connection
        binding.thermalConnectionButton.setOnClickListener {
            try {
                if (viewModel.uiState.value.isThermalConnected) {
                    viewModel.disconnectThermal()
                } else {
                    viewModel.connectThermal()
                }
            } catch (e: Exception) {
                showError("Thermal connection failed: ${e.message}")
            }
        }
    }

    private fun setupQuickActions() {
        // Calibration
        binding.calibrationButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.CalibrationActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open calibration: ${e.message}")
            }
        }
        
        // Files management
        binding.filesButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.FileViewActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open files: ${e.message}")
            }
        }
        
        // Device settings
        binding.devicesButton.setOnClickListener {
            try {
                val intent = Intent(this, com.multisensor.recording.ui.DevicesActivity::class.java)
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open device management: ${e.message}")
            }
        }
        
        // Data transfer
        binding.transferButton.setOnClickListener {
            try {
                showMessage("Data transfer requested")
            } catch (e: Exception) {
                showError("Data transfer failed: ${e.message}")
            }
        }
    }

    private fun setupToolbarMenu() {
        binding.toolbar.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                R.id.action_settings -> {
                    navigateToActivity(SettingsActivity::class.java)
                    true
                }
                R.id.action_diagnostics -> {
                    navigateToActivity(com.multisensor.recording.ui.DiagnosticsActivity::class.java)
                    true
                }
                R.id.action_about -> {
                    navigateToActivity(com.multisensor.recording.ui.AboutActivity::class.java)
                    true
                }
                else -> false
            }
        }
        
        binding.toolbar.inflateMenu(R.menu.main_toolbar_menu)
    }

    private fun observeViewModel() {
        try {
            // Observe UI state changes using StateFlow
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { uiState ->
                        updateUI(uiState)
                    }
                }
            }
            
        } catch (e: Exception) {
            showError("Failed to setup monitoring: ${e.message}")
        }
    }

    private fun updateUI(uiState: MainUiState) {
        // Update recording controls
        updateRecordingControls(uiState)
        
        // Update device status indicators
        updateDeviceStatus(uiState)
        
        // Update system status
        updateSystemStatus(uiState)
        
        // Update storage info
        updateStorageInfo(uiState)
        
        // Update toolbar subtitle
        updateToolbarSubtitle(uiState)
    }

    private fun updateRecordingControls(uiState: MainUiState) {
        // Record button
        binding.recordButton.isEnabled = uiState.canStartRecording || uiState.canStopRecording
        binding.recordButton.text = if (uiState.isRecording) "Stop Recording" else "Start Recording"
        
        // Recording status
        binding.recordingStatusText.text = when {
            uiState.isRecording -> "● Recording - ${formatDuration(uiState.recordingDuration)}"
            uiState.isReadyToRecord -> "Ready to record"
            else -> "Not ready"
        }
        
        // Camera controls
        binding.cameraSwitchButton.isEnabled = !uiState.isRecording
    }

    private fun updateDeviceStatus(uiState: MainUiState) {
        // PC connection
        updateConnectionButton(binding.pcConnectionButton, uiState.isPcConnected, "PC")
        binding.pcStatusText.text = if (uiState.isPcConnected) "Connected" else "Disconnected"
        
        // Shimmer connection
        updateConnectionButton(binding.shimmerConnectionButton, uiState.isShimmerConnected, "Shimmer")
        binding.shimmerStatusText.text = if (uiState.isShimmerConnected) {
            "Connected${if (uiState.shimmerBatteryLevel > 0) " (${uiState.shimmerBatteryLevel}%)" else ""}"
        } else "Disconnected"
        
        // Thermal connection
        updateConnectionButton(binding.thermalConnectionButton, uiState.isThermalConnected, "Thermal")
        binding.thermalStatusText.text = if (uiState.isThermalConnected) {
            "Connected${uiState.thermalTemperature?.let { " (${String.format("%.1f°C", it)})" } ?: ""}"
        } else "Disconnected"
        
        // Network status
        binding.networkStatusText.text = if (uiState.isNetworkConnected) {
            "Network Connected${if (uiState.networkAddress.isNotEmpty()) " (${uiState.networkAddress})" else ""}"
        } else "Network Disconnected"
    }

    private fun updateConnectionButton(button: com.google.android.material.button.MaterialButton, 
                                      isConnected: Boolean, deviceName: String) {
        button.text = if (isConnected) "Disconnect $deviceName" else "Connect $deviceName"
        button.setIconResource(if (isConnected) R.drawable.ic_disconnect else R.drawable.ic_connect)
    }

    private fun updateSystemStatus(uiState: MainUiState) {
        binding.systemStatusText.text = when (uiState.systemHealthStatus) {
            SystemHealthStatus.INITIALIZING -> "Initializing..."
            SystemHealthStatus.READY -> "System Ready"
            SystemHealthStatus.PARTIAL_CONNECTION -> "Partial Connection"
            SystemHealthStatus.DISCONNECTED -> "Disconnected"
            SystemHealthStatus.RECORDING -> "Recording Active"
            SystemHealthStatus.ERROR -> "System Error"
        }
        
        // Update calibration status
        binding.calibrationStatusText.text = when {
            uiState.isCalibrationRunning -> "Calibrating..."
            uiState.isCameraCalibrated && uiState.isThermalCalibrated && uiState.isShimmerCalibrated -> "All Calibrated"
            uiState.isCameraCalibrated || uiState.isThermalCalibrated || uiState.isShimmerCalibrated -> "Partially Calibrated"
            else -> "Not Calibrated"
        }
        
        binding.calibrationButton.isEnabled = uiState.canRunCalibration
    }

    private fun updateStorageInfo(uiState: MainUiState) {
        val usedPercentage = uiState.storageUsagePercentage
        
        binding.storageProgressBar.progress = usedPercentage
        binding.storageText.text = "${formatBytes(uiState.storageAvailable)} available"
        binding.sessionCountText.text = "${uiState.sessionCount} sessions, ${uiState.fileCount} files"
        
        // Transfer status
        binding.transferButton.isEnabled = !uiState.isTransferring && uiState.fileCount > 0
        binding.transferStatusText.text = if (uiState.isTransferring) "Transferring..." else "Ready"
    }

    private fun updateToolbarSubtitle(uiState: MainUiState) {
        val connectedDevices = listOfNotNull(
            if (uiState.isPcConnected) "PC" else null,
            if (uiState.isShimmerConnected) "Shimmer" else null,
            if (uiState.isThermalConnected) "Thermal" else null,
            if (uiState.isGsrConnected) "GSR" else null
        )
        
        binding.toolbar.subtitle = when {
            uiState.isRecording -> "● Recording..."
            connectedDevices.isNotEmpty() -> "${connectedDevices.size} devices connected"
            else -> "No devices connected"
        }
    }

    private fun formatDuration(durationMs: Long): String {
        val seconds = durationMs / 1000
        val minutes = seconds / 60
        val hours = minutes / 60
        return when {
            hours > 0 -> String.format("%d:%02d:%02d", hours, minutes % 60, seconds % 60)
            else -> String.format("%d:%02d", minutes, seconds % 60)
        }
    }

    private fun navigateToActivity(activityClass: Class<*>) {
        try {
            startActivity(Intent(this, activityClass))
        } catch (e: Exception) {
            showError("Navigation failed: ${e.message}")
        }
    }

    private fun runDiagnostics() {
        try {
            val currentState = viewModel.uiState.value
            val diagnosticInfo = buildString {
                appendLine("=== SYSTEM DIAGNOSTICS ===")
                appendLine("App Version: ${BuildConfig.VERSION_NAME}")
                appendLine("PC Connected: ${currentState.isPcConnected}")
                appendLine("Shimmer Connected: ${currentState.isShimmerConnected}")
                appendLine("Thermal Connected: ${currentState.isThermalConnected}")
                appendLine("GSR Connected: ${currentState.isGsrConnected}")
                appendLine("Network Connected: ${currentState.isNetworkConnected}")
                appendLine("Recording Active: ${currentState.isRecording}")
                appendLine("System Status: ${currentState.systemHealthStatus}")
                appendLine("Permissions OK: ${checkPermissions()}")
                appendLine("Storage Available: ${formatBytes(currentState.storageAvailable)}")
                appendLine("========================")
            }
            
            showMessage("Diagnostics completed - check logs for details")
            android.util.Log.i("DiagnosticsMD3", diagnosticInfo)
            
        } catch (e: Exception) {
            showError("Diagnostics failed: ${e.message}")
        }
    }

    private fun formatBytes(bytes: Long): String {
        return when {
            bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
            bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> "$bytes B"
        }
    }

    private fun checkPermissions(): Boolean {
        // Simple permission check - can be expanded
        return checkSelfPermission(android.Manifest.permission.CAMERA) == 
               android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("MainActivityMD3", error)
    }
}