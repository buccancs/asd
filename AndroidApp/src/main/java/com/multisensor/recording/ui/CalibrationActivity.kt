package com.multisensor.recording.ui

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
import com.multisensor.recording.databinding.ActivityCalibrationBinding
import dagger.hilt.android.AndroidEntryPoint

/**
 * Calibration Activity - Comprehensive Calibration Interface
 * 
 * Provides calibration interfaces for:
 * - Camera calibration (stereo and intrinsic)
 * - Thermal camera calibration 
 * - Shimmer device calibration
 * - System validation and diagnostics
 * - Calibration data management
 */
@AndroidEntryPoint
class CalibrationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityCalibrationBinding
    private lateinit var viewModel: CalibrationViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        binding = ActivityCalibrationBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[CalibrationViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize calibration: ${e.message}")
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
            title = "System Calibration"
            subtitle = "Configure and validate sensors"
        }
        
        setupCameraCalibration()
        setupThermalCalibration()
        setupShimmerCalibration()
        setupCalibrationData()
    }

    private fun setupCameraCalibration() {
        // Start camera calibration
        binding.calibrateCameraButton.setOnClickListener {
            try {
                viewModel.startCameraCalibration()
                showMessage("Starting camera calibration...")
            } catch (e: Exception) {
                showError("Camera calibration failed: ${e.message}")
            }
        }
        
        // Reset camera calibration
        binding.resetCameraCalibrationButton.setOnClickListener {
            try {
                viewModel.resetCameraCalibration()
                showMessage("Camera calibration reset")
            } catch (e: Exception) {
                showError("Reset failed: ${e.message}")
            }
        }
    }

    private fun setupThermalCalibration() {
        // Start thermal calibration
        binding.calibrateThermalButton.setOnClickListener {
            try {
                viewModel.startThermalCalibration()
                showMessage("Starting thermal calibration...")
            } catch (e: Exception) {
                showError("Thermal calibration failed: ${e.message}")
            }
        }
        
        // Reset thermal calibration
        binding.resetThermalCalibrationButton.setOnClickListener {
            try {
                viewModel.resetThermalCalibration()
                showMessage("Thermal calibration reset")
            } catch (e: Exception) {
                showError("Reset failed: ${e.message}")
            }
        }
    }

    private fun setupShimmerCalibration() {
        // Start Shimmer calibration
        binding.calibrateShimmerButton.setOnClickListener {
            try {
                viewModel.startShimmerCalibration()
                showMessage("Starting Shimmer calibration...")
            } catch (e: Exception) {
                showError("Shimmer calibration failed: ${e.message}")
            }
        }
        
        // Reset Shimmer calibration
        binding.resetShimmerCalibrationButton.setOnClickListener {
            try {
                viewModel.resetShimmerCalibration()
                showMessage("Shimmer calibration reset")
            } catch (e: Exception) {
                showError("Reset failed: ${e.message}")
            }
        }
    }

    private fun setupCalibrationData() {
        // Save calibration data
        binding.saveCalibrationButton.setOnClickListener {
            try {
                viewModel.saveCalibrationData()
                showMessage("Calibration data saved")
            } catch (e: Exception) {
                showError("Save failed: ${e.message}")
            }
        }
        
        // Load calibration data
        binding.loadCalibrationButton.setOnClickListener {
            try {
                viewModel.loadCalibrationData()
                showMessage("Calibration data loaded")
            } catch (e: Exception) {
                showError("Load failed: ${e.message}")
            }
        }
        
        // Export calibration data
        binding.exportCalibrationButton.setOnClickListener {
            try {
                viewModel.exportCalibrationData()
                showMessage("Calibration data exported")
            } catch (e: Exception) {
                showError("Export failed: ${e.message}")
            }
        }
        
        // Run system validation
        binding.validateSystemButton.setOnClickListener {
            try {
                viewModel.validateSystem()
                showMessage("Starting system validation...")
            } catch (e: Exception) {
                showError("Validation failed: ${e.message}")
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

    private fun updateUI(uiState: CalibrationUiState) {
        // Update camera calibration status
        updateCameraCalibrationStatus(uiState)
        
        // Update thermal calibration status  
        updateThermalCalibrationStatus(uiState)
        
        // Update Shimmer calibration status
        updateShimmerCalibrationStatus(uiState)
        
        // Update progress indicators
        updateProgressIndicators(uiState)
        
        // Update calibration data status
        updateCalibrationDataStatus(uiState)
    }

    private fun updateCameraCalibrationStatus(uiState: CalibrationUiState) {
        binding.cameraCalibrationStatus.text = when {
            uiState.isCameraCalibrating -> "Calibrating... ${uiState.cameraCalibrationProgress}%"
            uiState.isCameraCalibrated -> "✓ Calibrated"
            else -> "Not calibrated"
        }
        
        binding.calibrateCameraButton.isEnabled = !uiState.isCameraCalibrating && uiState.canStartCalibration
        binding.resetCameraCalibrationButton.isEnabled = uiState.isCameraCalibrated
        
        // Update camera calibration details
        if (uiState.isCameraCalibrated) {
            binding.cameraCalibrationDetails.text = buildString {
                appendLine("Intrinsic Parameters: ✓")
                appendLine("Distortion Coefficients: ✓")
                if (uiState.cameraCalibrationError > 0) {
                    appendLine("Reprojection Error: ${String.format("%.3f", uiState.cameraCalibrationError)}")
                }
                appendLine("Calibration Date: ${uiState.cameraCalibrationDate}")
            }
        } else {
            binding.cameraCalibrationDetails.text = "No calibration data available"
        }
    }

    private fun updateThermalCalibrationStatus(uiState: CalibrationUiState) {
        binding.thermalCalibrationStatus.text = when {
            uiState.isThermalCalibrating -> "Calibrating... ${uiState.thermalCalibrationProgress}%"
            uiState.isThermalCalibrated -> "✓ Calibrated"
            else -> "Not calibrated"
        }
        
        binding.calibrateThermalButton.isEnabled = !uiState.isThermalCalibrating && uiState.canStartCalibration
        binding.resetThermalCalibrationButton.isEnabled = uiState.isThermalCalibrated
        
        // Update thermal calibration details
        if (uiState.isThermalCalibrated) {
            binding.thermalCalibrationDetails.text = buildString {
                appendLine("Temperature Range: ${uiState.thermalTempRange}")
                appendLine("Emissivity: ${uiState.thermalEmissivity}")
                appendLine("Color Palette: ${uiState.thermalColorPalette}")
                appendLine("Calibration Date: ${uiState.thermalCalibrationDate}")
            }
        } else {
            binding.thermalCalibrationDetails.text = "No calibration data available"
        }
    }

    private fun updateShimmerCalibrationStatus(uiState: CalibrationUiState) {
        binding.shimmerCalibrationStatus.text = when {
            uiState.isShimmerCalibrating -> "Calibrating... ${uiState.shimmerCalibrationProgress}%"
            uiState.isShimmerCalibrated -> "✓ Calibrated"
            else -> "Not calibrated"
        }
        
        binding.calibrateShimmerButton.isEnabled = !uiState.isShimmerCalibrating && uiState.canStartCalibration
        binding.resetShimmerCalibrationButton.isEnabled = uiState.isShimmerCalibrated
        
        // Update Shimmer calibration details
        if (uiState.isShimmerCalibrated) {
            binding.shimmerCalibrationDetails.text = buildString {
                appendLine("Device MAC: ${uiState.shimmerMacAddress}")
                appendLine("Sensor Config: ${uiState.shimmerSensorConfig}")
                appendLine("Sampling Rate: ${uiState.shimmerSamplingRate}Hz")
                appendLine("Calibration Date: ${uiState.shimmerCalibrationDate}")
            }
        } else {
            binding.shimmerCalibrationDetails.text = "No calibration data available"
        }
    }

    private fun updateProgressIndicators(uiState: CalibrationUiState) {
        // Overall calibration progress
        val overallProgress = listOf(
            if (uiState.isCameraCalibrated) 1 else 0,
            if (uiState.isThermalCalibrated) 1 else 0,
            if (uiState.isShimmerCalibrated) 1 else 0
        ).sum() * 100 / 3
        
        binding.overallProgressBar.progress = overallProgress
        binding.overallProgressText.text = "Overall Progress: $overallProgress%"
        
        // Individual progress bars
        binding.cameraProgressBar.progress = if (uiState.isCameraCalibrating) uiState.cameraCalibrationProgress else if (uiState.isCameraCalibrated) 100 else 0
        binding.thermalProgressBar.progress = if (uiState.isThermalCalibrating) uiState.thermalCalibrationProgress else if (uiState.isThermalCalibrated) 100 else 0
        binding.shimmerProgressBar.progress = if (uiState.isShimmerCalibrating) uiState.shimmerCalibrationProgress else if (uiState.isShimmerCalibrated) 100 else 0
    }

    private fun updateCalibrationDataStatus(uiState: CalibrationUiState) {
        // Enable/disable data management buttons
        val hasCalibrationData = uiState.isCameraCalibrated || uiState.isThermalCalibrated || uiState.isShimmerCalibrated
        
        binding.saveCalibrationButton.isEnabled = hasCalibrationData && !uiState.isAnyCalibrating
        binding.exportCalibrationButton.isEnabled = hasCalibrationData && !uiState.isAnyCalibrating
        binding.loadCalibrationButton.isEnabled = !uiState.isAnyCalibrating
        binding.validateSystemButton.isEnabled = hasCalibrationData && !uiState.isAnyCalibrating && !uiState.isValidating
        
        // Update validation status
        binding.validationStatus.text = when {
            uiState.isValidating -> "Validating system..."
            uiState.isSystemValid -> "✓ System validation passed"
            uiState.validationErrors.isNotEmpty() -> "⚠ Validation issues found"
            else -> "System not validated"
        }
        
        // Show validation errors if any
        if (uiState.validationErrors.isNotEmpty()) {
            binding.validationDetails.text = "Issues:\n${uiState.validationErrors.joinToString("\n• ", "• ")}"
        } else {
            binding.validationDetails.text = ""
        }
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
        android.util.Log.e("CalibrationActivity", error)
    }
}