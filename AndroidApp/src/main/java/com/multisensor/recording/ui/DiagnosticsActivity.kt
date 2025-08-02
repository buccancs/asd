package com.multisensor.recording.ui

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.ActivityDiagnosticsBinding
import com.multisensor.recording.ui.DiagnosticsHealthStatus
import dagger.hilt.android.AndroidEntryPoint

/**
 * Diagnostics Activity - System Health Dashboard
 * 
 * Provides comprehensive system diagnostics including:
 * - System health dashboard with real-time metrics
 * - Performance monitoring and metrics display
 * - Error logs viewer with filtering and search
 * - Network connectivity tests and results
 * - Device communication tests
 * - Diagnostics report generation and export
 */
@AndroidEntryPoint
class DiagnosticsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDiagnosticsBinding
    private lateinit var viewModel: DiagnosticsViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        binding = ActivityDiagnosticsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[DiagnosticsViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize diagnostics: ${e.message}")
            return
        }

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
            title = "System Diagnostics"
            subtitle = "Monitor system health and performance"
        }
        
        setupDiagnosticActions()
        setupReportActions()
    }

    private fun setupDiagnosticActions() {
        // Run full system diagnostic
        binding.runFullDiagnosticButton.setOnClickListener {
            try {
                viewModel.runFullSystemDiagnostic()
                showMessage("Running full system diagnostic...")
            } catch (e: Exception) {
                showError("Diagnostic failed: ${e.message}")
            }
        }
        
        // Test network connectivity
        binding.testNetworkButton.setOnClickListener {
            try {
                viewModel.testNetworkConnectivity()
                showMessage("Testing network connectivity...")
            } catch (e: Exception) {
                showError("Network test failed: ${e.message}")
            }
        }
        
        // Test device communication
        binding.testDevicesButton.setOnClickListener {
            try {
                viewModel.testDeviceCommunication()
                showMessage("Testing device communication...")
            } catch (e: Exception) {
                showError("Device test failed: ${e.message}")
            }
        }
        
        // Test performance
        binding.testPerformanceButton.setOnClickListener {
            try {
                viewModel.testSystemPerformance()
                showMessage("Testing system performance...")
            } catch (e: Exception) {
                showError("Performance test failed: ${e.message}")
            }
        }
        
        // Clear error logs
        binding.clearLogsButton.setOnClickListener {
            try {
                viewModel.clearErrorLogs()
                showMessage("Error logs cleared")
            } catch (e: Exception) {
                showError("Failed to clear logs: ${e.message}")
            }
        }
        
        // Refresh system status
        binding.refreshStatusButton.setOnClickListener {
            try {
                viewModel.refreshSystemStatus()
                showMessage("Refreshing system status...")
            } catch (e: Exception) {
                showError("Refresh failed: ${e.message}")
            }
        }
    }

    private fun setupReportActions() {
        // Generate diagnostic report
        binding.generateReportButton.setOnClickListener {
            try {
                viewModel.generateDiagnosticReport()
                showMessage("Generating diagnostic report...")
            } catch (e: Exception) {
                showError("Report generation failed: ${e.message}")
            }
        }
        
        // Export diagnostic data
        binding.exportDiagnosticsButton.setOnClickListener {
            try {
                viewModel.exportDiagnosticData()
                showMessage("Exporting diagnostic data...")
            } catch (e: Exception) {
                showError("Export failed: ${e.message}")
            }
        }
        
        // Send logs to support
        binding.sendLogsButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_EMAIL, arrayOf("support@multisensor-recording.com"))
                    putExtra(Intent.EXTRA_SUBJECT, "Diagnostic Logs - Multi-Sensor Recording App")
                    putExtra(Intent.EXTRA_TEXT, viewModel.getDiagnosticLogContent())
                }
                
                if (intent.resolveActivity(packageManager) != null) {
                    startActivity(Intent.createChooser(intent, "Send diagnostic logs"))
                } else {
                    showError("No email app available")
                }
            } catch (e: Exception) {
                showError("Failed to send logs: ${e.message}")
            }
        }
    }

    private fun observeViewModel() {
        try {
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

    private fun updateUI(uiState: DiagnosticsUiState) {
        updateSystemHealth(uiState)
        updatePerformanceMetrics(uiState)
        updateErrorLogs(uiState)
        updateTestResults(uiState)
        updateButtons(uiState)
    }

    private fun updateSystemHealth(uiState: DiagnosticsUiState) {
        // Overall system health
        binding.systemHealthStatus.text = when (uiState.systemHealthStatus) {
            DiagnosticsHealthStatus.EXCELLENT -> "Excellent"
            DiagnosticsHealthStatus.GOOD -> "Good"
            DiagnosticsHealthStatus.WARNING -> "Warning"
            DiagnosticsHealthStatus.CRITICAL -> "Critical"
            DiagnosticsHealthStatus.UNKNOWN -> "Unknown"
        }
        
        binding.systemHealthStatus.setTextColor(getColor(when (uiState.systemHealthStatus) {
            DiagnosticsHealthStatus.EXCELLENT -> com.multisensor.recording.R.color.md_theme_primary
            DiagnosticsHealthStatus.GOOD -> com.multisensor.recording.R.color.md_theme_primary
            DiagnosticsHealthStatus.WARNING -> com.multisensor.recording.R.color.md_theme_secondary
            DiagnosticsHealthStatus.CRITICAL -> com.multisensor.recording.R.color.md_theme_error
            DiagnosticsHealthStatus.UNKNOWN -> com.multisensor.recording.R.color.md_theme_outline
        }))
        
        // System uptime
        binding.systemUptimeText.text = "System Uptime: ${uiState.systemUptime}"
        
        // Connected devices count
        binding.connectedDevicesText.text = "Connected Devices: ${uiState.connectedDevicesCount}/5"
        
        // Active processes
        binding.activeProcessesText.text = "Active Processes: ${uiState.activeProcessesCount}"
        
        // Last diagnostic run
        binding.lastDiagnosticText.text = "Last Diagnostic: ${uiState.lastDiagnosticRun}"
    }

    private fun updatePerformanceMetrics(uiState: DiagnosticsUiState) {
        // CPU usage
        binding.cpuUsageText.text = "CPU Usage: ${uiState.cpuUsagePercent}%"
        binding.cpuUsageProgress.progress = uiState.cpuUsagePercent
        
        // Memory usage
        binding.memoryUsageText.text = "Memory Usage: ${uiState.memoryUsagePercent}%"
        binding.memoryUsageProgress.progress = uiState.memoryUsagePercent
        
        // Storage usage
        binding.storageUsageText.text = "Storage Usage: ${uiState.storageUsagePercent}%"
        binding.storageUsageProgress.progress = uiState.storageUsagePercent
        
        // Network bandwidth
        binding.networkBandwidthText.text = "Network: ↓${uiState.networkDownload} ↑${uiState.networkUpload}"
        
        // Battery level (if applicable)
        binding.batteryLevelText.text = "Battery: ${uiState.batteryLevel}%"
        binding.batteryLevelProgress.progress = uiState.batteryLevel
        
        // Frame rate
        binding.frameRateText.text = "Frame Rate: ${uiState.currentFrameRate}fps"
    }

    private fun updateErrorLogs(uiState: DiagnosticsUiState) {
        // Error count
        binding.errorCountText.text = "Errors: ${uiState.errorCount}"
        binding.warningCountText.text = "Warnings: ${uiState.warningCount}"
        binding.infoCountText.text = "Info: ${uiState.infoCount}"
        
        // Recent error logs
        if (uiState.recentErrorLogs.isNotEmpty()) {
            binding.errorLogsText.text = uiState.recentErrorLogs.takeLast(20).joinToString("\n") { log ->
                "${log.timestamp} [${log.level}] ${log.message}"
            }
        } else {
            binding.errorLogsText.text = "No error logs available"
        }
    }

    private fun updateTestResults(uiState: DiagnosticsUiState) {
        // Network test results
        binding.networkTestResults.text = buildString {
            if (uiState.networkTestResults.isNotEmpty()) {
                append("Network Tests:\n")
                uiState.networkTestResults.forEach { result ->
                    append("• ${result.testName}: ${if (result.passed) "PASS" else "FAIL"}")
                    if (result.details.isNotEmpty()) {
                        append(" (${result.details})")
                    }
                    append("\n")
                }
            } else {
                append("No network tests run")
            }
        }
        
        // Device test results
        binding.deviceTestResults.text = buildString {
            if (uiState.deviceTestResults.isNotEmpty()) {
                append("Device Tests:\n")
                uiState.deviceTestResults.forEach { result ->
                    append("• ${result.testName}: ${if (result.passed) "PASS" else "FAIL"}")
                    if (result.details.isNotEmpty()) {
                        append(" (${result.details})")
                    }
                    append("\n")
                }
            } else {
                append("No device tests run")
            }
        }
        
        // Performance test results
        binding.performanceTestResults.text = buildString {
            if (uiState.performanceTestResults.isNotEmpty()) {
                append("Performance Tests:\n")
                uiState.performanceTestResults.forEach { result ->
                    append("• ${result.testName}: ${if (result.passed) "PASS" else "FAIL"}")
                    if (result.details.isNotEmpty()) {
                        append(" (${result.details})")
                    }
                    append("\n")
                }
            } else {
                append("No performance tests run")
            }
        }
    }

    private fun updateButtons(uiState: DiagnosticsUiState) {
        // Disable buttons during tests
        binding.runFullDiagnosticButton.isEnabled = !uiState.isRunningDiagnostic
        binding.testNetworkButton.isEnabled = !uiState.isTestingNetwork
        binding.testDevicesButton.isEnabled = !uiState.isTestingDevices
        binding.testPerformanceButton.isEnabled = !uiState.isTestingPerformance
        
        // Report buttons
        binding.generateReportButton.isEnabled = !uiState.isGeneratingReport
        binding.exportDiagnosticsButton.isEnabled = !uiState.isExportingData
        
        // Clear logs button
        binding.clearLogsButton.isEnabled = uiState.errorCount > 0 || uiState.warningCount > 0
        
        // Update button text for active operations
        binding.runFullDiagnosticButton.text = if (uiState.isRunningDiagnostic) "Running Diagnostic..." else "Run Full Diagnostic"
        binding.generateReportButton.text = if (uiState.isGeneratingReport) "Generating..." else "Generate Report"
        binding.exportDiagnosticsButton.text = if (uiState.isExportingData) "Exporting..." else "Export Data"
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            android.R.id.home -> {
                onBackPressedDispatcher.onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(error: String) {
        Toast.makeText(this, "Error: $error", Toast.LENGTH_LONG).show()
        android.util.Log.e("DiagnosticsActivity", error)
    }
}