package com.multisensor.recording.network

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.util.Logger
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import org.junit.Test
import java.lang.reflect.Method

/**
 * Simple verification tests for timestamp extraction functionality in EnhancedJsonSocketClient
 * 
 * Test Categories:
 * - Timestamp extraction from different message types
 * - Handling of messages without timestamp fields
 */
class EnhancedJsonSocketClientTimestampValidationTest {

    @Test
    fun `test timestamp extraction method exists and handles different message types correctly`() {
        // Given
        val mockLogger = mockk<Logger>(relaxed = true)
        val mockNetworkConfig = mockk<NetworkConfiguration> {
            every { getServerIp() } returns "192.168.1.100"
            every { getJsonPort() } returns 8080
            every { setServerIp(any()) } just runs
            every { setJsonPort(any()) } just runs
        }
        
        // Create EnhancedJsonSocketClient instance
        val enhancedJsonSocketClient = EnhancedJsonSocketClient(mockLogger, mockNetworkConfig)
        
        // Use reflection to access the private method
        val extractTimestampMethod = EnhancedJsonSocketClient::class.java.getDeclaredMethod(
            "extractTimestampFromMessage", 
            JsonMessage::class.java
        )
        extractTimestampMethod.isAccessible = true
        
        // Test PreviewFrameMessage
        val expectedTimestamp = 1234567890L
        val previewMessage = PreviewFrameMessage(
            cam = "rgb",
            timestamp = expectedTimestamp,
            image = "base64encodedimage"
        )
        
        val extractedPreviewTimestamp = extractTimestampMethod.invoke(
            enhancedJsonSocketClient, 
            previewMessage
        ) as Long?
        
        assertThat(extractedPreviewTimestamp).isEqualTo(expectedTimestamp)
        
        // Test SensorDataMessage
        val sensorExpectedTimestamp = 9876543210L
        val sensorMessage = SensorDataMessage(
            timestamp = sensorExpectedTimestamp,
            values = mapOf("temperature" to 25.5)
        )
        
        val extractedSensorTimestamp = extractTimestampMethod.invoke(
            enhancedJsonSocketClient,
            sensorMessage
        ) as Long?
        
        assertThat(extractedSensorTimestamp).isEqualTo(sensorExpectedTimestamp)
        
        // Test StatusMessage (should return null)
        val statusMessage = StatusMessage(
            battery = 85,
            recording = true
        )
        
        val extractedStatusTimestamp = extractTimestampMethod.invoke(
            enhancedJsonSocketClient,
            statusMessage
        ) as Long?
        
        assertThat(extractedStatusTimestamp).isNull()
        
        // Test SetStimulusTimeCommand
        val stimulusTime = 5555555555L
        val stimulusCommand = SetStimulusTimeCommand(time = stimulusTime)
        
        val extractedStimulusTimestamp = extractTimestampMethod.invoke(
            enhancedJsonSocketClient,
            stimulusCommand
        ) as Long?
        
        assertThat(extractedStimulusTimestamp).isEqualTo(stimulusTime)
        
        // Test SyncTimeCommand  
        val pcTimestamp = 7777777777L
        val syncCommand = SyncTimeCommand(pc_timestamp = pcTimestamp)
        
        val extractedSyncTimestamp = extractTimestampMethod.invoke(
            enhancedJsonSocketClient,
            syncCommand
        ) as Long?
        
        assertThat(extractedSyncTimestamp).isEqualTo(pcTimestamp)
    }
    
    @Test
    fun `test implementation compiles and method signature is correct`() {
        // This test simply verifies that the enhanced client can be instantiated
        // and that our implementation compiles without errors
        val mockLogger = mockk<Logger>(relaxed = true)
        val mockNetworkConfig = mockk<NetworkConfiguration> {
            every { getServerIp() } returns "localhost"
            every { getJsonPort() } returns 8080
            every { setServerIp(any()) } just runs
            every { setJsonPort(any()) } just runs
        }
        
        val client = EnhancedJsonSocketClient(mockLogger, mockNetworkConfig)
        
        // Verify the client was created successfully
        assertThat(client).isNotNull()
        assertThat(client.isConnected()).isFalse()
        
        // Verify the method signature exists
        val method = EnhancedJsonSocketClient::class.java.getDeclaredMethod(
            "extractTimestampFromMessage", 
            JsonMessage::class.java
        )
        assertThat(method).isNotNull()
        assertThat(method.returnType).isEqualTo(Long::class.javaObjectType)
    }
}