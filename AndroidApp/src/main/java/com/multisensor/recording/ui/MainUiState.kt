package com.multisensor.recording.ui

/**
 * Streamlined UI State for single-dashboard interface
 * 
 * Minimalist approach focusing only on essential state properties
 * needed for the single-screen dashboard. Reduces complexity while
 * maintaining full functionality.
 */
data class MainUiState(
    // Core System Status
    val statusText: String = "Initializing...",
    val isInitialized: Boolean = false,
    
    // Recording State (Primary Function)
    val isRecording: Boolean = false,
    val recordingDuration: Long = 0L,
    val recordingSessionId: String? = null,
    val isReadyToRecord: Boolean = false,
    
    // Device Connections (Essential for Operation)
    val isPcConnected: Boolean = false,
    val isShimmerConnected: Boolean = false,
    val isThermalConnected: Boolean = false,
    val isGsrConnected: Boolean = false,
    val isNetworkConnected: Boolean = false,
    val isCameraConnected: Boolean = false,
    
    // Device Info (Minimal for Status Display)
    val shimmerBatteryLevel: Int = -1,
    val thermalTemperature: Float? = null,
    val networkAddress: String = "",
    
    // Calibration State (Essential for System Readiness)
    val isCameraCalibrated: Boolean = false,
    val isThermalCalibrated: Boolean = false,
    val isShimmerCalibrated: Boolean = false,
    val isCalibrationRunning: Boolean = false,
    
    // Storage (Critical for Recording)
    val storageUsed: Long = 0L,
    val storageAvailable: Long = 0L,
    val storageTotal: Long = 0L,
    val sessionCount: Int = 0,
    val fileCount: Int = 0,
    
    // Data Transfer (Essential for Field Work)
    val isTransferring: Boolean = false,
    
    // Error Handling (Critical)
    val errorMessage: String? = null,
    val showErrorDialog: Boolean = false,
    
    // Loading States (User Feedback)
    val isLoadingRecording: Boolean = false,
    val isLoadingCalibration: Boolean = false
) {
    
    /**
     * Can start recording if system is ready and not currently recording
     */
    val canStartRecording: Boolean
        get() = isInitialized && 
                !isRecording && 
                !isLoadingRecording &&
                isCameraConnected
    
    /**
     * Can stop recording if currently recording
     */
    val canStopRecording: Boolean
        get() = isRecording && !isLoadingRecording
    
    /**
     * Can run calibration if not recording and not already calibrating
     */
    val canRunCalibration: Boolean
        get() = isInitialized && 
                !isRecording && 
                !isCalibrationRunning && 
                !isLoadingCalibration
    
    /**
     * Overall system health status for dashboard display
     */
    val systemHealthStatus: SystemHealthStatus
        get() = when {
            !isInitialized -> SystemHealthStatus.INITIALIZING
            errorMessage != null -> SystemHealthStatus.ERROR
            isRecording -> SystemHealthStatus.RECORDING
            isPcConnected && (isShimmerConnected || isThermalConnected) && isCameraConnected -> SystemHealthStatus.READY
            isPcConnected && isCameraConnected -> SystemHealthStatus.PARTIAL_CONNECTION
            else -> SystemHealthStatus.DISCONNECTED
        }
    
    /**
     * Storage usage percentage for progress bar
     */
    val storageUsagePercentage: Int
        get() = if (storageTotal > 0) {
            ((storageUsed * 100) / storageTotal).toInt()
        } else 0
}

/**
 * System health status enumeration
 */
enum class SystemHealthStatus {
    INITIALIZING,
    READY,
    PARTIAL_CONNECTION,
    DISCONNECTED,
    RECORDING,
    ERROR
}