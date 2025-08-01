package com.multisensor.recording.recording

import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.*
import java.net.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Handles robust PC communication for Shimmer3 GSR+ devices.
 * 
 * This class provides rock-solid PC connectivity including:
 * - Device pairing and discovery for PC connections
 * - Real-time data streaming to PC applications
 * - Bidirectional command/control communication
 * - File transfer capabilities
 * - Network protocol handling
 * - Connection state management
 */
class PCCommunicationHandler(
    private val logger: Logger
) {
    
    /**
     * PC connection states
     */
    enum class PCConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        STREAMING,
        ERROR,
        PAIRING
    }
    
    /**
     * Data streaming modes to PC
     */
    enum class StreamingMode {
        NONE,
        REAL_TIME,      // Live streaming as data arrives
        BUFFERED,       // Batched streaming for efficiency
        ON_DEMAND,      // Stream on PC request
        FILE_TRANSFER   // File-based transfer
    }
    
    /**
     * PC communication configuration
     */
    data class PCConfiguration(
        val serverPort: Int = 8080,
        val maxConnections: Int = 5,
        val bufferSize: Int = 8192,
        val heartbeatInterval: Long = 5000L,
        val connectionTimeout: Long = 30000L,
        val enableFileTransfer: Boolean = true,
        val enableRealTimeStreaming: Boolean = true,
        val dataFormat: String = "JSON" // JSON, CSV, BINARY
    )
    
    /**
     * PC connection information
     */
    data class PCConnection(
        val connectionId: String,
        val clientSocket: Socket,
        val inputStream: DataInputStream,
        val outputStream: DataOutputStream,
        val connectedAt: Long,
        val clientAddress: String,
        val isAuthenticated: Boolean = false,
        val streamingMode: StreamingMode = StreamingMode.NONE
    )
    
    /**
     * Commands that can be sent from PC
     */
    sealed class PCCommand {
        data class StartStreaming(val deviceIds: List<String>, val mode: StreamingMode) : PCCommand()
        data class StopStreaming(val deviceIds: List<String>) : PCCommand()
        data class ConfigureDevice(val deviceId: String, val config: Map<String, Any>) : PCCommand()
        data class RequestDeviceInfo(val deviceId: String) : PCCommand()
        data class RequestFileTransfer(val filename: String) : PCCommand()
        object ListDevices : PCCommand()
        object GetStatus : PCCommand()
        data class Authenticate(val token: String) : PCCommand()
    }
    
    /**
     * Responses sent to PC
     */
    sealed class PCResponse {
        data class DeviceList(val devices: List<Map<String, Any>>) : PCResponse()
        data class DeviceInfo(val deviceId: String, val info: Map<String, Any>) : PCResponse()
        data class StreamingData(val deviceId: String, val data: Map<String, Any>) : PCResponse()
        data class Status(val status: Map<String, Any>) : PCResponse()
        data class Error(val message: String, val code: Int) : PCResponse()
        data class Success(val message: String) : PCResponse()
        data class FileData(val filename: String, val data: ByteArray) : PCResponse()
    }
    
    // Configuration and state
    private val config = PCConfiguration()
    private val _connectionState = MutableStateFlow(PCConnectionState.DISCONNECTED)
    val connectionState: StateFlow<PCConnectionState> = _connectionState.asStateFlow()
    
    // Network components
    private var serverSocket: ServerSocket? = null
    private val activeConnections = ConcurrentHashMap<String, PCConnection>()
    private val streamingQueues = ConcurrentHashMap<String, ConcurrentLinkedQueue<String>>()
    
    // Coroutine management
    private val communicationScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val isRunning = AtomicBoolean(false)
    
    // Statistics
    private val bytesTransferred = AtomicLong(0L)
    private val commandsProcessed = AtomicLong(0L)
    private val activeStreams = AtomicLong(0L)
    
    /**
     * Start PC communication server
     */
    suspend fun startServer(port: Int = config.serverPort): Boolean = withContext(Dispatchers.IO) {
        try {
            if (isRunning.compareAndSet(false, true)) {
                logger.info("Starting PC communication server on port $port")
                
                serverSocket = ServerSocket(port)
                _connectionState.value = PCConnectionState.CONNECTING
                
                // Start accepting connections
                communicationScope.launch {
                    acceptConnections()
                }
                
                // Start heartbeat monitoring
                communicationScope.launch {
                    monitorConnections()
                }
                
                _connectionState.value = PCConnectionState.CONNECTED
                logger.info("PC communication server started successfully")
                true
            } else {
                logger.warning("PC communication server is already running")
                false
            }
        } catch (e: Exception) {
            logger.error("Failed to start PC communication server", e)
            _connectionState.value = PCConnectionState.ERROR
            isRunning.set(false)
            false
        }
    }
    
    /**
     * Stop PC communication server
     */
    suspend fun stopServer() = withContext(Dispatchers.IO) {
        try {
            if (isRunning.compareAndSet(true, false)) {
                logger.info("Stopping PC communication server")
                
                _connectionState.value = PCConnectionState.DISCONNECTED
                
                // Close all active connections
                activeConnections.values.forEach { connection ->
                    try {
                        connection.clientSocket.close()
                    } catch (e: Exception) {
                        logger.debug("Error closing client connection: ${e.message}")
                    }
                }
                activeConnections.clear()
                
                // Close server socket
                serverSocket?.close()
                serverSocket = null
                
                // Cancel coroutines
                communicationScope.cancel()
                
                _connectionState.value = PCConnectionState.DISCONNECTED
                logger.info("PC communication server stopped")
            }
        } catch (e: Exception) {
            logger.error("Error stopping PC communication server", e)
        }
    }
    
    /**
     * Stream sensor data to connected PCs
     */
    suspend fun streamSensorData(deviceId: String, sensorSample: SensorSample) {
        if (!isRunning.get()) return
        
        try {
            val jsonData = sensorSample.toJsonString()
            val response = PCResponse.StreamingData(deviceId, mapOf(
                "timestamp" to sensorSample.systemTimestamp,
                "deviceId" to deviceId,
                "sensors" to sensorSample.sensorValues,
                "battery" to sensorSample.batteryLevel,
                "sequence" to sensorSample.sequenceNumber
            ))
            
            // Send to all connected PCs that are streaming this device
            activeConnections.values.forEach { connection ->
                if (connection.streamingMode != StreamingMode.NONE) {
                    sendResponse(connection, response)
                    bytesTransferred.addAndGet(jsonData.length.toLong())
                }
            }
        } catch (e: Exception) {
            logger.error("Error streaming sensor data to PC", e)
        }
    }
    
    /**
     * Send device list to PC
     */
    suspend fun sendDeviceList(connectionId: String, devices: List<ShimmerDevice>) {
        val connection = activeConnections[connectionId] ?: return
        
        val deviceList = devices.map { device ->
            mapOf(
                "deviceId" to device.deviceId,
                "macAddress" to device.macAddress,
                "deviceName" to device.deviceName,
                "connectionState" to device.connectionState.name,
                "isStreaming" to device.isActivelyStreaming(),
                "batteryLevel" to device.batteryLevel,
                "sampleCount" to device.sampleCount.get(),
                "lastSeen" to device.lastSampleTime
            )
        }
        
        val response = PCResponse.DeviceList(deviceList)
        sendResponse(connection, response)
    }
    
    /**
     * Handle device pairing requests from PC
     */
    suspend fun handlePairingRequest(deviceId: String, pairingCode: String): Boolean {
        return try {
            logger.info("Processing PC pairing request for device $deviceId")
            
            // Validate pairing code (implement your security logic here)
            val isValidCode = validatePairingCode(pairingCode)
            
            if (isValidCode) {
                // Mark device as paired with PC
                notifyDevicePairedWithPC(deviceId, true)
                logger.info("Device $deviceId successfully paired with PC")
                true
            } else {
                logger.warning("Invalid pairing code for device $deviceId")
                false
            }
        } catch (e: Exception) {
            logger.error("Error handling PC pairing request", e)
            false
        }
    }
    
    /**
     * Transfer file to PC
     */
    suspend fun transferFile(connectionId: String, file: File) {
        val connection = activeConnections[connectionId] ?: return
        
        try {
            logger.info("Transferring file to PC: ${file.name}")
            
            val fileData = file.readBytes()
            val response = PCResponse.FileData(file.name, fileData)
            
            sendResponse(connection, response)
            bytesTransferred.addAndGet(fileData.size.toLong())
            
            logger.info("File transfer completed: ${file.name} (${fileData.size} bytes)")
        } catch (e: Exception) {
            logger.error("Error transferring file to PC", e)
            val errorResponse = PCResponse.Error("File transfer failed: ${e.message}", 500)
            sendResponse(connection, errorResponse)
        }
    }
    
    /**
     * Get PC communication statistics
     */
    fun getStatistics(): Map<String, Any> = mapOf(
        "isRunning" to isRunning.get(),
        "connectionState" to _connectionState.value.name,
        "activeConnections" to activeConnections.size,
        "bytesTransferred" to bytesTransferred.get(),
        "commandsProcessed" to commandsProcessed.get(),
        "activeStreams" to activeStreams.get(),
        "serverPort" to config.serverPort
    )
    
    /**
     * Accept incoming PC connections
     */
    private suspend fun acceptConnections() {
        while (isRunning.get()) {
            try {
                val clientSocket = serverSocket?.accept()
                if (clientSocket != null) {
                    logger.info("New PC connection from: ${clientSocket.remoteSocketAddress}")
                    
                    val connectionId = generateConnectionId()
                    val connection = PCConnection(
                        connectionId = connectionId,
                        clientSocket = clientSocket,
                        inputStream = DataInputStream(clientSocket.getInputStream()),
                        outputStream = DataOutputStream(clientSocket.getOutputStream()),
                        connectedAt = System.currentTimeMillis(),
                        clientAddress = clientSocket.remoteSocketAddress.toString()
                    )
                    
                    activeConnections[connectionId] = connection
                    
                    // Handle this connection in a separate coroutine
                    communicationScope.launch {
                        handleConnection(connection)
                    }
                }
            } catch (e: SocketException) {
                if (isRunning.get()) {
                    logger.error("Socket error in PC communication", e)
                }
            } catch (e: Exception) {
                logger.error("Error accepting PC connection", e)
            }
        }
    }
    
    /**
     * Handle individual PC connection
     */
    private suspend fun handleConnection(connection: PCConnection) {
        try {
            logger.debug("Handling PC connection: ${connection.connectionId}")
            
            while (isRunning.get() && !connection.clientSocket.isClosed) {
                try {
                    // Read command from PC
                    val commandJson = connection.inputStream.readUTF()
                    val command = parseCommand(commandJson)
                    
                    // Process command
                    processCommand(connection, command)
                    commandsProcessed.incrementAndGet()
                    
                } catch (e: EOFException) {
                    logger.debug("PC connection closed: ${connection.connectionId}")
                    break
                } catch (e: Exception) {
                    logger.error("Error handling PC connection", e)
                    val errorResponse = PCResponse.Error("Command processing error: ${e.message}", 400)
                    sendResponse(connection, errorResponse)
                }
            }
        } finally {
            // Cleanup connection
            activeConnections.remove(connection.connectionId)
            try {
                connection.clientSocket.close()
            } catch (e: Exception) {
                logger.debug("Error closing PC connection: ${e.message}")
            }
            logger.info("PC connection closed: ${connection.connectionId}")
        }
    }
    
    /**
     * Process PC commands
     */
    private suspend fun processCommand(connection: PCConnection, command: PCCommand) {
        when (command) {
            is PCCommand.StartStreaming -> {
                handleStartStreaming(connection, command)
            }
            is PCCommand.StopStreaming -> {
                handleStopStreaming(connection, command)
            }
            is PCCommand.ConfigureDevice -> {
                handleConfigureDevice(connection, command)
            }
            is PCCommand.RequestDeviceInfo -> {
                handleRequestDeviceInfo(connection, command)
            }
            is PCCommand.RequestFileTransfer -> {
                handleRequestFileTransfer(connection, command)
            }
            is PCCommand.ListDevices -> {
                handleListDevices(connection)
            }
            is PCCommand.GetStatus -> {
                handleGetStatus(connection)
            }
            is PCCommand.Authenticate -> {
                handleAuthenticate(connection, command)
            }
        }
    }
    
    // Command handlers
    private suspend fun handleStartStreaming(connection: PCConnection, command: PCCommand.StartStreaming) {
        logger.info("Starting streaming to PC for devices: ${command.deviceIds}")
        
        val updatedConnection = connection.copy(streamingMode = command.mode)
        activeConnections[connection.connectionId] = updatedConnection
        activeStreams.incrementAndGet()
        
        val response = PCResponse.Success("Streaming started for devices: ${command.deviceIds}")
        sendResponse(connection, response)
    }
    
    private suspend fun handleStopStreaming(connection: PCConnection, command: PCCommand.StopStreaming) {
        logger.info("Stopping streaming to PC for devices: ${command.deviceIds}")
        
        val updatedConnection = connection.copy(streamingMode = StreamingMode.NONE)
        activeConnections[connection.connectionId] = updatedConnection
        activeStreams.decrementAndGet()
        
        val response = PCResponse.Success("Streaming stopped for devices: ${command.deviceIds}")
        sendResponse(connection, response)
    }
    
    private suspend fun handleListDevices(connection: PCConnection) {
        // This would be called by the main ShimmerRecorder to provide device list
        val response = PCResponse.Success("Device list request received")
        sendResponse(connection, response)
    }
    
    private suspend fun handleGetStatus(connection: PCConnection) {
        val status = getStatistics()
        val response = PCResponse.Status(status)
        sendResponse(connection, response)
    }
    
    private suspend fun handleAuthenticate(connection: PCConnection, command: PCCommand.Authenticate) {
        val isValid = validateAuthToken(command.token)
        if (isValid) {
            val updatedConnection = connection.copy(isAuthenticated = true)
            activeConnections[connection.connectionId] = updatedConnection
            
            val response = PCResponse.Success("Authentication successful")
            sendResponse(connection, response)
        } else {
            val response = PCResponse.Error("Authentication failed", 401)
            sendResponse(connection, response)
        }
    }
    
    // Additional command handlers would be implemented here...
    private suspend fun handleConfigureDevice(connection: PCConnection, command: PCCommand.ConfigureDevice) {
        // Implementation for device configuration
        val response = PCResponse.Success("Device configuration request received")
        sendResponse(connection, response)
    }
    
    private suspend fun handleRequestDeviceInfo(connection: PCConnection, command: PCCommand.RequestDeviceInfo) {
        // Implementation for device info request
        val response = PCResponse.Success("Device info request received")
        sendResponse(connection, response)
    }
    
    private suspend fun handleRequestFileTransfer(connection: PCConnection, command: PCCommand.RequestFileTransfer) {
        // Implementation for file transfer request
        val response = PCResponse.Success("File transfer request received")
        sendResponse(connection, response)
    }
    
    /**
     * Send response to PC
     */
    private suspend fun sendResponse(connection: PCConnection, response: PCResponse) {
        try {
            val json = serializeResponse(response)
            connection.outputStream.writeUTF(json)
            connection.outputStream.flush()
        } catch (e: Exception) {
            logger.error("Error sending response to PC", e)
        }
    }
    
    /**
     * Monitor PC connections for health and timeouts
     */
    private suspend fun monitorConnections() {
        while (isRunning.get()) {
            try {
                val currentTime = System.currentTimeMillis()
                val connectionsToRemove = mutableListOf<String>()
                
                activeConnections.forEach { (connectionId, connection) ->
                    val connectionAge = currentTime - connection.connectedAt
                    
                    // Check for timeout
                    if (connectionAge > config.connectionTimeout && !connection.isAuthenticated) {
                        connectionsToRemove.add(connectionId)
                        logger.warning("PC connection timeout: $connectionId")
                    }
                    
                    // Send heartbeat
                    if (connectionAge % config.heartbeatInterval == 0L) {
                        try {
                            val heartbeat = PCResponse.Success("heartbeat")
                            sendResponse(connection, heartbeat)
                        } catch (e: Exception) {
                            connectionsToRemove.add(connectionId)
                            logger.debug("PC connection lost: $connectionId")
                        }
                    }
                }
                
                // Remove timed out connections
                connectionsToRemove.forEach { connectionId ->
                    activeConnections.remove(connectionId)?.let { connection ->
                        try {
                            connection.clientSocket.close()
                        } catch (e: Exception) {
                            // Ignore
                        }
                    }
                }
                
                delay(config.heartbeatInterval)
            } catch (e: Exception) {
                logger.error("Error monitoring PC connections", e)
                delay(5000) // Wait before retrying
            }
        }
    }
    
    // Utility methods
    private fun generateConnectionId(): String = "PC_${System.currentTimeMillis()}_${(1000..9999).random()}"
    
    private fun parseCommand(json: String): PCCommand {
        // Simple JSON parsing - in production, use a proper JSON library
        return when {
            json.contains("StartStreaming") -> PCCommand.StartStreaming(emptyList(), StreamingMode.REAL_TIME)
            json.contains("StopStreaming") -> PCCommand.StopStreaming(emptyList())
            json.contains("ListDevices") -> PCCommand.ListDevices
            json.contains("GetStatus") -> PCCommand.GetStatus
            else -> PCCommand.GetStatus
        }
    }
    
    private fun serializeResponse(response: PCResponse): String {
        // Simple JSON serialization - in production, use a proper JSON library
        return when (response) {
            is PCResponse.Success -> """{"type":"success","message":"${response.message}"}"""
            is PCResponse.Error -> """{"type":"error","message":"${response.message}","code":${response.code}}"""
            is PCResponse.Status -> """{"type":"status","data":${response.status}}"""
            else -> """{"type":"response","message":"Response sent"}"""
        }
    }
    
    private fun validatePairingCode(code: String): Boolean {
        // Implement your pairing code validation logic
        return code.isNotEmpty() && code.length >= 4
    }
    
    private fun validateAuthToken(token: String): Boolean {
        // Implement your authentication token validation logic
        return token.isNotEmpty()
    }
    
    private fun notifyDevicePairedWithPC(deviceId: String, paired: Boolean) {
        // This would notify the main system that a device is now paired with PC
        logger.info("Device $deviceId PC pairing status: $paired")
    }
    
    /**
     * Cleanup all PC communication resources
     */
    fun cleanup() {
        runBlocking {
            stopServer()
        }
        streamingQueues.clear()
        logger.info("PCCommunicationHandler cleanup completed")
    }
}