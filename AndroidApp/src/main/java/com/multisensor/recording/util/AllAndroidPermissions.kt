package com.multisensor.recording.util

import android.Manifest
import android.os.Build

/**
 * Comprehensive list of all Android permissions that can be requested.
 * This class provides a complete bundle of all available Android permissions
 * for applications that need to request all permissions at once.
 */
object AllAndroidPermissions {
    /**
     * Get all available Android permissions based on the current API level
     */
    fun getAllPermissions(): Array<String> {
        val permissions = mutableListOf<String>()

        // Core permissions
        permissions.addAll(getCorePermissions())

        // Location permissions
        permissions.addAll(getLocationPermissions())

        // Storage permissions
        permissions.addAll(getStoragePermissions())

        // Camera and microphone permissions
        permissions.addAll(getCameraAndAudioPermissions())

        // Communication permissions
        permissions.addAll(getCommunicationPermissions())

        // Bluetooth permissions
        permissions.addAll(getBluetoothPermissions())

        // Network permissions
        permissions.addAll(getNetworkPermissions())

        // System permissions
        permissions.addAll(getSystemPermissions())

        // Sensor permissions
        permissions.addAll(getSensorPermissions())

        // Device admin permissions
        permissions.addAll(getDeviceAdminPermissions())

        // Media permissions (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.addAll(getMediaPermissions())
        }

        // Notification permissions (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.addAll(getNotificationPermissions())
        }

        return permissions.toTypedArray()
    }

    private fun getCorePermissions(): List<String> =
        listOf(
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.INTERNET,
            Manifest.permission.WAKE_LOCK,
            Manifest.permission.VIBRATE,
            Manifest.permission.DISABLE_KEYGUARD,
            Manifest.permission.GET_ACCOUNTS,
        )

    private fun getLocationPermissions(): List<String> {
        val permissions =
            mutableListOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
            )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            permissions.add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
        }

        return permissions
    }

    private fun getStoragePermissions(): List<String> {
        val permissions =
            mutableListOf(
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
            )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            permissions.add(Manifest.permission.MANAGE_EXTERNAL_STORAGE)
        }

        return permissions
    }

    private fun getCameraAndAudioPermissions(): List<String> =
        listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.MODIFY_AUDIO_SETTINGS,
        )

    private fun getCommunicationPermissions(): List<String> {
        val permissions =
            mutableListOf(
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_PHONE_NUMBERS,
                Manifest.permission.CALL_PHONE,
                Manifest.permission.READ_CALL_LOG,
                Manifest.permission.WRITE_CALL_LOG,
                Manifest.permission.ADD_VOICEMAIL,
                Manifest.permission.USE_SIP,
                @Suppress("DEPRECATION")
                Manifest.permission.PROCESS_OUTGOING_CALLS,
                Manifest.permission.SEND_SMS,
                Manifest.permission.RECEIVE_SMS,
                Manifest.permission.READ_SMS,
                Manifest.permission.RECEIVE_WAP_PUSH,
                Manifest.permission.RECEIVE_MMS,
                Manifest.permission.READ_CONTACTS,
                Manifest.permission.WRITE_CONTACTS,
                Manifest.permission.READ_CALENDAR,
                Manifest.permission.WRITE_CALENDAR,
            )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            permissions.add(Manifest.permission.ANSWER_PHONE_CALLS)
        }

        return permissions
    }

    private fun getBluetoothPermissions(): List<String> {
        val permissions =
            mutableListOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
            )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions.addAll(
                listOf(
                    Manifest.permission.BLUETOOTH_SCAN,
                    Manifest.permission.BLUETOOTH_ADVERTISE,
                    Manifest.permission.BLUETOOTH_CONNECT,
                ),
            )
        }

        return permissions
    }

    private fun getNetworkPermissions(): List<String> =
        listOf(
            Manifest.permission.CHANGE_NETWORK_STATE,
            Manifest.permission.CHANGE_WIFI_MULTICAST_STATE,
            Manifest.permission.NFC,
            Manifest.permission.TRANSMIT_IR,
        )

    private fun getSystemPermissions(): List<String> {
        val permissions =
            mutableListOf(
                Manifest.permission.EXPAND_STATUS_BAR,
                Manifest.permission.INSTALL_SHORTCUT,
                Manifest.permission.UNINSTALL_SHORTCUT,
                Manifest.permission.KILL_BACKGROUND_PROCESSES,
                Manifest.permission.FOREGROUND_SERVICE,
                Manifest.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                Manifest.permission.REQUEST_DELETE_PACKAGES,
                Manifest.permission.REQUEST_INSTALL_PACKAGES,
                Manifest.permission.SYSTEM_ALERT_WINDOW,
                Manifest.permission.WRITE_SETTINGS,
                Manifest.permission.CHANGE_CONFIGURATION,
                Manifest.permission.REORDER_TASKS,
                Manifest.permission.SET_WALLPAPER,
                Manifest.permission.SET_WALLPAPER_HINTS,
                Manifest.permission.WRITE_SYNC_SETTINGS,
                Manifest.permission.READ_SYNC_SETTINGS,
                Manifest.permission.READ_SYNC_STATS,
            )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            permissions.addAll(
                listOf(
                    Manifest.permission.FOREGROUND_SERVICE_CAMERA,
                    Manifest.permission.FOREGROUND_SERVICE_MICROPHONE,
                ),
            )
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            permissions.add(Manifest.permission.ACTIVITY_RECOGNITION)
        }

        return permissions
    }

    private fun getSensorPermissions(): List<String> {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT_WATCH) {
            permissions.add(Manifest.permission.BODY_SENSORS)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.BODY_SENSORS_BACKGROUND)
        }

        return permissions
    }

    private fun getDeviceAdminPermissions(): List<String> =
        listOf(
            Manifest.permission.BIND_DEVICE_ADMIN,
            Manifest.permission.BIND_INPUT_METHOD,
            Manifest.permission.BIND_ACCESSIBILITY_SERVICE,
            Manifest.permission.BIND_WALLPAPER,
        )

    private fun getMediaPermissions(): List<String> {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.addAll(
                listOf(
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO,
                ),
            )
        }

        return permissions
    }

    private fun getNotificationPermissions(): List<String> {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        return permissions
    }

    /**
     * Get permissions that are considered dangerous and require runtime permission
     */
    fun getDangerousPermissions(): Array<String> {
        val dangerousPermissions = mutableListOf<String>()

        // Location (foreground only - background location handled separately to avoid XXPermissions restriction)
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
            ),
        )

        // Note: ACCESS_BACKGROUND_LOCATION is excluded to prevent XXPermissions library restriction
        // Background location permissions are handled separately through PermissionTool's three-phase system

        // Storage
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
            ),
        )

        // Camera and Audio
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.CAMERA,
                Manifest.permission.RECORD_AUDIO,
            ),
        )

        // Phone
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_PHONE_NUMBERS,
                Manifest.permission.CALL_PHONE,
                Manifest.permission.READ_CALL_LOG,
                Manifest.permission.WRITE_CALL_LOG,
                Manifest.permission.ADD_VOICEMAIL,
                Manifest.permission.USE_SIP,
                @Suppress("DEPRECATION")
                Manifest.permission.PROCESS_OUTGOING_CALLS,
            ),
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            dangerousPermissions.add(Manifest.permission.ANSWER_PHONE_CALLS)
        }

        // SMS
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.SEND_SMS,
                Manifest.permission.RECEIVE_SMS,
                Manifest.permission.READ_SMS,
                Manifest.permission.RECEIVE_WAP_PUSH,
                Manifest.permission.RECEIVE_MMS,
            ),
        )

        // Contacts
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.READ_CONTACTS,
                Manifest.permission.WRITE_CONTACTS,
                Manifest.permission.GET_ACCOUNTS,
            ),
        )

        // Calendar
        dangerousPermissions.addAll(
            listOf(
                Manifest.permission.READ_CALENDAR,
                Manifest.permission.WRITE_CALENDAR,
            ),
        )

        // Sensors
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT_WATCH) {
            dangerousPermissions.add(Manifest.permission.BODY_SENSORS)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            dangerousPermissions.add(Manifest.permission.BODY_SENSORS_BACKGROUND)
        }

        // Activity Recognition
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            dangerousPermissions.add(Manifest.permission.ACTIVITY_RECOGNITION)
        }

        // Media (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            dangerousPermissions.addAll(
                listOf(
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO,
                ),
            )
        }

        // Notifications (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            dangerousPermissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        return dangerousPermissions.toTypedArray()
    }

    /**
     * Get a human-readable description for permission groups
     */
    fun getPermissionGroupDescriptions(): Map<String, String> =
        mapOf(
            "Location" to "Access device location for GPS and network-based positioning",
            "Storage" to "Read and write files on device storage",
            "Camera" to "Take pictures and record videos using device cameras",
            "Microphone" to "Record audio using device microphone",
            "Phone" to "Make and manage phone calls, access phone state",
            "SMS" to "Send and receive text messages",
            "Contacts" to "Access and modify device contacts",
            "Calendar" to "Access and modify calendar events",
            "Sensors" to "Access device sensors like accelerometer, gyroscope",
            "Bluetooth" to "Connect to and communicate with Bluetooth devices",
            "Network" to "Access network information and modify network settings",
            "System" to "Access system-level features and settings",
            "Media" to "Access photos, videos, and audio files",
            "Notifications" to "Show notifications to the user",
        )
}
