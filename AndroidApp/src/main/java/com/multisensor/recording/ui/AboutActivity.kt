package com.multisensor.recording.ui

import android.content.Intent
import android.net.Uri
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
import com.multisensor.recording.databinding.ActivityAboutBinding
import com.multisensor.recording.BuildConfig
import dagger.hilt.android.AndroidEntryPoint

/**
 * About Activity - App Information and System Details
 * 
 * Provides comprehensive information about:
 * - App version and build information
 * - License information and open source credits
 * - Developer information and contact details
 * - System specifications and hardware info
 * - Legal information and privacy policy
 * - Links to documentation and support
 */
@AndroidEntryPoint
class AboutActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAboutBinding
    private lateinit var viewModel: AboutViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        binding = ActivityAboutBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        try {
            viewModel = ViewModelProvider(this)[AboutViewModel::class.java]
        } catch (e: Exception) {
            showError("Failed to initialize about: ${e.message}")
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
            title = "About"
            subtitle = "Multi-Sensor Recording System"
        }
        
        setupAppInfo()
        setupLinks()
        setupSystemInfo()
    }

    private fun setupAppInfo() {
        // Display basic app information
        binding.appVersionText.text = "Version ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})"
        binding.buildTypeText.text = "Build: ${BuildConfig.BUILD_TYPE}"
        binding.buildTimeText.text = "Built: ${viewModel.getBuildDate()}"
        
        // App description
        binding.appDescriptionText.text = getString(com.multisensor.recording.R.string.app_description)
    }

    private fun setupLinks() {
        // GitHub repository link
        binding.githubLinkButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/buccancs/bucika_gsr"))
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open GitHub: ${e.message}")
            }
        }
        
        // Documentation link
        binding.documentationLinkButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/buccancs/bucika_gsr/wiki"))
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open documentation: ${e.message}")
            }
        }
        
        // Support email
        binding.supportEmailButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_SENDTO).apply {
                    data = Uri.parse("mailto:")
                    putExtra(Intent.EXTRA_EMAIL, arrayOf("support@multisensor-recording.com"))
                    putExtra(Intent.EXTRA_SUBJECT, "Multi-Sensor Recording App Support")
                    putExtra(Intent.EXTRA_TEXT, "Please describe your issue or question:")
                }
                
                if (intent.resolveActivity(packageManager) != null) {
                    startActivity(intent)
                } else {
                    showError("No email app available")
                }
            } catch (e: Exception) {
                showError("Failed to open email: ${e.message}")
            }
        }
        
        // License information
        binding.licenseLinkButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/buccancs/bucika_gsr/blob/main/LICENSE"))
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open license: ${e.message}")
            }
        }
        
        // Privacy policy
        binding.privacyPolicyButton.setOnClickListener {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/buccancs/bucika_gsr/blob/main/PRIVACY.md"))
                startActivity(intent)
            } catch (e: Exception) {
                showError("Failed to open privacy policy: ${e.message}")
            }
        }
    }

    private fun setupSystemInfo() {
        // System info will be populated by ViewModel
        binding.refreshSystemInfoButton.setOnClickListener {
            try {
                viewModel.refreshSystemInfo()
                showMessage("System information refreshed")
            } catch (e: Exception) {
                showError("Failed to refresh system info: ${e.message}")
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

    private fun updateUI(uiState: AboutUiState) {
        updateSystemInfo(uiState)
        updateHardwareInfo(uiState)
        updateLegalInfo(uiState)
        updateCredits(uiState)
    }

    private fun updateSystemInfo(uiState: AboutUiState) {
        binding.androidVersionText.text = "Android ${uiState.androidVersion} (API ${uiState.androidApiLevel})"
        binding.deviceModelText.text = "${uiState.deviceManufacturer} ${uiState.deviceModel}"
        binding.deviceBoardText.text = "Board: ${uiState.deviceBoard}"
        binding.deviceArchitectureText.text = "Architecture: ${uiState.deviceArchitecture}"
        binding.kernelVersionText.text = "Kernel: ${uiState.kernelVersion}"
        binding.javaVersionText.text = "Java: ${uiState.javaVersion}"
    }

    private fun updateHardwareInfo(uiState: AboutUiState) {
        binding.totalMemoryText.text = "Total RAM: ${uiState.totalMemory}"
        binding.availableMemoryText.text = "Available RAM: ${uiState.availableMemory}"
        binding.totalStorageText.text = "Total Storage: ${uiState.totalStorage}"
        binding.availableStorageText.text = "Available Storage: ${uiState.availableStorage}"
        binding.processorInfoText.text = "Processor: ${uiState.processorInfo}"
        binding.screenResolutionText.text = "Screen: ${uiState.screenResolution}"
        binding.screenDensityText.text = "Density: ${uiState.screenDensity} DPI"
        
        // Camera info
        if (uiState.cameraInfo.isNotEmpty()) {
            binding.cameraInfoText.text = "Cameras:\n${uiState.cameraInfo.joinToString("\n") { "• $it" }}"
        } else {
            binding.cameraInfoText.text = "Camera information unavailable"
        }
        
        // Sensor info
        if (uiState.sensorInfo.isNotEmpty()) {
            binding.sensorInfoText.text = "Sensors:\n${uiState.sensorInfo.joinToString("\n") { "• $it" }}"
        } else {
            binding.sensorInfoText.text = "Sensor information unavailable"
        }
    }

    private fun updateLegalInfo(uiState: AboutUiState) {
        binding.copyrightText.text = uiState.copyrightInfo
        binding.licenseText.text = uiState.licenseInfo
        
        if (uiState.thirdPartyLicenses.isNotEmpty()) {
            binding.thirdPartyLicensesText.text = "Third-party Libraries:\n${uiState.thirdPartyLicenses.joinToString("\n") { "• $it" }}"
        } else {
            binding.thirdPartyLicensesText.text = "No third-party licenses to display"
        }
    }

    private fun updateCredits(uiState: AboutUiState) {
        binding.developersText.text = buildString {
            append("Development Team:\n")
            uiState.developers.forEach { developer ->
                append("• ${developer.name}")
                if (developer.role.isNotEmpty()) {
                    append(" - ${developer.role}")
                }
                append("\n")
            }
        }
        
        if (uiState.contributors.isNotEmpty()) {
            binding.contributorsText.text = buildString {
                append("Contributors:\n")
                uiState.contributors.forEach { contributor ->
                    append("• $contributor\n")
                }
            }
        } else {
            binding.contributorsText.text = "Special thanks to all contributors"
        }
        
        if (uiState.acknowledgments.isNotEmpty()) {
            binding.acknowledgementsText.text = buildString {
                append("Acknowledgments:\n")
                uiState.acknowledgments.forEach { ack ->
                    append("• $ack\n")
                }
            }
        } else {
            binding.acknowledgementsText.text = ""
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
        android.util.Log.e("AboutActivity", error)
    }
}