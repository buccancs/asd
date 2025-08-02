package com.multisensor.recording.ui

import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Camera
import android.hardware.Sensor
import android.hardware.SensorManager
import android.os.Build
import android.util.DisplayMetrics
import android.view.WindowManager
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject

/**
 * Developer information data class
 */
data class Developer(
    val name: String,
    val role: String = "",
    val email: String = ""
)

/**
 * About UI State
 * 
 * Represents comprehensive system and app information including:
 * - System specifications and hardware details
 * - App version and build information
 * - Legal information and licenses
 * - Developer credits and acknowledgments
 */
data class AboutUiState(
    // System Information
    val androidVersion: String = "",
    val androidApiLevel: String = "",
    val deviceManufacturer: String = "",
    val deviceModel: String = "",
    val deviceBoard: String = "",
    val deviceArchitecture: String = "",
    val kernelVersion: String = "",
    val javaVersion: String = "",
    
    // Hardware Information
    val totalMemory: String = "",
    val availableMemory: String = "",
    val totalStorage: String = "",
    val availableStorage: String = "",
    val processorInfo: String = "",
    val screenResolution: String = "",
    val screenDensity: String = "",
    val cameraInfo: List<String> = emptyList(),
    val sensorInfo: List<String> = emptyList(),
    
    // Legal Information
    val copyrightInfo: String = "",
    val licenseInfo: String = "",
    val thirdPartyLicenses: List<String> = emptyList(),
    
    // Credits
    val developers: List<Developer> = emptyList(),
    val contributors: List<String> = emptyList(),
    val acknowledgments: List<String> = emptyList(),
    
    // Status
    val isLoading: Boolean = false
)

/**
 * About ViewModel
 * 
 * Manages system information collection and app metadata.
 * Provides comprehensive details about the device, app, and credits.
 */
@HiltViewModel
class AboutViewModel @Inject constructor(
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val _uiState = MutableStateFlow(AboutUiState())
    val uiState: StateFlow<AboutUiState> = _uiState.asStateFlow()

    init {
        // Load initial system information
        refreshSystemInfo()
        loadStaticInfo()
    }

    /**
     * Refresh system information
     */
    fun refreshSystemInfo() {
        _uiState.value = _uiState.value.copy(isLoading = true)
        
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            try {
                val systemInfo = collectSystemInfo()
                val hardwareInfo = collectHardwareInfo()
                
                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        androidVersion = systemInfo.androidVersion,
                        androidApiLevel = systemInfo.androidApiLevel,
                        deviceManufacturer = systemInfo.deviceManufacturer,
                        deviceModel = systemInfo.deviceModel,
                        deviceBoard = systemInfo.deviceBoard,
                        deviceArchitecture = systemInfo.deviceArchitecture,
                        kernelVersion = systemInfo.kernelVersion,
                        javaVersion = systemInfo.javaVersion,
                        totalMemory = hardwareInfo.totalMemory,
                        availableMemory = hardwareInfo.availableMemory,
                        totalStorage = hardwareInfo.totalStorage,
                        availableStorage = hardwareInfo.availableStorage,
                        processorInfo = hardwareInfo.processorInfo,
                        screenResolution = hardwareInfo.screenResolution,
                        screenDensity = hardwareInfo.screenDensity,
                        cameraInfo = hardwareInfo.cameraInfo,
                        sensorInfo = hardwareInfo.sensorInfo
                    )
                }
            } catch (e: Exception) {
                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                    _uiState.value = _uiState.value.copy(isLoading = false)
                }
                android.util.Log.e("AboutViewModel", "Failed to collect system info", e)
            }
        }
    }

    /**
     * Get build date from build configuration
     */
    fun getBuildDate(): String {
        return try {
            val buildTime = com.multisensor.recording.BuildConfig.BUILD_TIME
            if (buildTime.isNotEmpty()) {
                // If it's a timestamp, convert it to a readable date
                val timestamp = buildTime.toLongOrNull()
                if (timestamp != null) {
                    java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.getDefault())
                        .format(java.util.Date(timestamp))
                } else {
                    buildTime
                }
            } else {
                "Unknown"
            }
        } catch (e: Exception) {
            "Unknown"
        }
    }

    private fun loadStaticInfo() {
        val developers = listOf(
            Developer("buccancs", "Lead Developer & Research Student", "buccancs@github.com"),
            Developer("Multi-Sensor Recording Team", "Development Team"),
            Developer("University Research Group", "Academic Supervision")
        )
        
        val contributors = listOf(
            "Android Development Community",
            "Material Design Team",
            "Shimmer Research Community",
            "OpenCV Contributors",
            "FLIR Thermal Imaging Community"
        )
        
        val acknowledgments = listOf(
            "University Research Lab for project support",
            "Master's Thesis Supervisor for guidance",
            "Open Source Community for tools and libraries",
            "Research participants for testing and feedback"
        )
        
        val thirdPartyLicenses = listOf(
            "Android Jetpack - Apache License 2.0",
            "Material Design Components - Apache License 2.0",
            "Hilt Dependency Injection - Apache License 2.0",
            "Kotlin Coroutines - Apache License 2.0",
            "OkHttp - Apache License 2.0",
            "Gson - Apache License 2.0",
            "Shimmer for Android - BSD 3-Clause License",
            "OpenCV - Apache License 2.0"
        )
        
        _uiState.value = _uiState.value.copy(
            developers = developers,
            contributors = contributors,
            acknowledgments = acknowledgments,
            thirdPartyLicenses = thirdPartyLicenses,
            copyrightInfo = "© 2024 Multi-Sensor Recording System\nAll rights reserved",
            licenseInfo = "This project is licensed under the Apache License 2.0\nSee LICENSE file for details"
        )
    }

    private data class SystemInfo(
        val androidVersion: String,
        val androidApiLevel: String,
        val deviceManufacturer: String,
        val deviceModel: String,
        val deviceBoard: String,
        val deviceArchitecture: String,
        val kernelVersion: String,
        val javaVersion: String
    )

    private data class HardwareInfo(
        val totalMemory: String,
        val availableMemory: String,
        val totalStorage: String,
        val availableStorage: String,
        val processorInfo: String,
        val screenResolution: String,
        val screenDensity: String,
        val cameraInfo: List<String>,
        val sensorInfo: List<String>
    )

    private fun collectSystemInfo(): SystemInfo {
        return SystemInfo(
            androidVersion = Build.VERSION.RELEASE,
            androidApiLevel = Build.VERSION.SDK_INT.toString(),
            deviceManufacturer = Build.MANUFACTURER.replaceFirstChar { it.uppercase() },
            deviceModel = Build.MODEL,
            deviceBoard = Build.BOARD,
            deviceArchitecture = Build.SUPPORTED_ABIS.firstOrNull() ?: "Unknown",
            kernelVersion = System.getProperty("os.version") ?: "Unknown",
            javaVersion = System.getProperty("java.version") ?: "Unknown"
        )
    }

    private fun collectHardwareInfo(): HardwareInfo {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        val memInfo = android.app.ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        
        val totalMemory = formatBytes(memInfo.totalMem)
        val availableMemory = formatBytes(memInfo.availMem)
        
        val internalDir = context.filesDir
        val totalStorage = formatBytes(internalDir.totalSpace)
        val availableStorage = formatBytes(internalDir.freeSpace)
        
        val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val displayMetrics = DisplayMetrics()
        windowManager.defaultDisplay.getMetrics(displayMetrics)
        
        val screenResolution = "${displayMetrics.widthPixels} × ${displayMetrics.heightPixels}"
        val screenDensity = displayMetrics.densityDpi.toString()
        
        val processorInfo = getCpuInfo()
        val cameraInfo = getCameraInfo()
        val sensorInfo = getSensorInfo()
        
        return HardwareInfo(
            totalMemory = totalMemory,
            availableMemory = availableMemory,
            totalStorage = totalStorage,
            availableStorage = availableStorage,
            processorInfo = processorInfo,
            screenResolution = screenResolution,
            screenDensity = screenDensity,
            cameraInfo = cameraInfo,
            sensorInfo = sensorInfo
        )
    }

    private fun getCpuInfo(): String {
        return try {
            val cpuInfo = java.io.File("/proc/cpuinfo").readText()
            val modelName = cpuInfo.lines()
                .find { it.startsWith("model name") || it.startsWith("Processor") }
                ?.substringAfter(":")
                ?.trim()
            
            modelName ?: "${Build.HARDWARE} (${Build.SUPPORTED_ABIS.joinToString(", ")})"
        } catch (e: Exception) {
            "${Build.HARDWARE} (${Build.SUPPORTED_ABIS.joinToString(", ")})"
        }
    }

    @Suppress("DEPRECATION")
    private fun getCameraInfo(): List<String> {
        return try {
            val cameraList = mutableListOf<String>()
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as android.hardware.camera2.CameraManager
                val cameraIds = cameraManager.cameraIdList
                
                for (cameraId in cameraIds) {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                    val facing = characteristics.get(android.hardware.camera2.CameraCharacteristics.LENS_FACING)
                    val facingStr = when (facing) {
                        android.hardware.camera2.CameraCharacteristics.LENS_FACING_FRONT -> "Front"
                        android.hardware.camera2.CameraCharacteristics.LENS_FACING_BACK -> "Back"
                        android.hardware.camera2.CameraCharacteristics.LENS_FACING_EXTERNAL -> "External"
                        else -> "Unknown"
                    }
                    cameraList.add("Camera $cameraId: $facingStr")
                }
            } else {
                val numberOfCameras = Camera.getNumberOfCameras()
                for (i in 0 until numberOfCameras) {
                    val cameraInfo = Camera.CameraInfo()
                    Camera.getCameraInfo(i, cameraInfo)
                    val facing = if (cameraInfo.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) "Front" else "Back"
                    cameraList.add("Camera $i: $facing")
                }
            }
            
            cameraList
        } catch (e: Exception) {
            listOf("Camera information unavailable")
        }
    }

    private fun getSensorInfo(): List<String> {
        return try {
            val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
            val sensors = sensorManager.getSensorList(Sensor.TYPE_ALL)
            
            sensors.map { sensor ->
                "${sensor.name} (${sensor.vendor})"
            }.take(10) // Limit to first 10 sensors to avoid overwhelming the UI
        } catch (e: Exception) {
            listOf("Sensor information unavailable")
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
}