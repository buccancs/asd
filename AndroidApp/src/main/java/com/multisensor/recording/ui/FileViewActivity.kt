package com.multisensor.recording.ui

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import com.multisensor.recording.R
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

/**
 * File View Activity - MVVM-based file browser for multi-sensor recording sessions
 * 
 * Refactored to follow proper MVVM architecture:
 * - Activity is a passive observer of ViewModel state
 * - All business logic moved to FileViewViewModel
 * - Uses StateFlow for reactive UI updates
 * - Forwards user events to ViewModel
 */
@AndroidEntryPoint
class FileViewActivity : AppCompatActivity() {
    
    private val viewModel: FileViewViewModel by viewModels()
    
    @Inject
    lateinit var logger: Logger

    // UI Components
    private lateinit var sessionsRecyclerView: RecyclerView
    private lateinit var filesRecyclerView: RecyclerView
    private lateinit var sessionInfoText: TextView
    private lateinit var searchEditText: EditText
    private lateinit var filterSpinner: Spinner
    private lateinit var progressBar: ProgressBar
    private lateinit var emptyStateText: TextView
    private lateinit var refreshButton: Button

    // Adapters
    private lateinit var sessionsAdapter: SessionsAdapter
    private lateinit var filesAdapter: FilesAdapter

    // Date formatter
    private val dateFormatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

    companion object {
        private const val AUTHORITY = "com.multisensor.recording.fileprovider"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_file_view)

        setupActionBar()
        initializeViews()
        setupRecyclerViews()
        setupEventListeners()
        observeUiState()

        logger.info("FileViewActivity created with MVVM architecture")
    }

    override fun onDestroy() {
        super.onDestroy()
        logger.info("FileViewActivity destroyed")
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.file_view_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            R.id.action_refresh -> {
                viewModel.refreshSessions()
                true
            }
            R.id.action_delete_all -> {
                showDeleteAllDialog()
                true
            }
            R.id.action_export_all -> {
                showMessage("Export functionality coming soon")
                true
            }
            android.R.id.home -> {
                onBackPressedDispatcher.onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }

    private fun setupActionBar() {
        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
            title = "File Browser"
        }
    }

    private fun initializeViews() {
        sessionsRecyclerView = findViewById(R.id.sessions_recycler_view)
        filesRecyclerView = findViewById(R.id.files_recycler_view)
        sessionInfoText = findViewById(R.id.session_info_text)
        searchEditText = findViewById(R.id.search_edit_text)
        filterSpinner = findViewById(R.id.filter_spinner)
        progressBar = findViewById(R.id.progress_bar)
        emptyStateText = findViewById(R.id.empty_state_text)
        refreshButton = findViewById(R.id.refresh_button)
    }

    private fun setupRecyclerViews() {
        // Sessions RecyclerView
        sessionsAdapter = SessionsAdapter { session ->
            viewModel.selectSession(session)
        }
        sessionsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = sessionsAdapter
        }

        // Files RecyclerView
        filesAdapter = FilesAdapter { fileItem ->
            handleFileClick(fileItem)
        }
        filesRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = filesAdapter
        }
    }

    private fun setupEventListeners() {
        // Search functionality
        searchEditText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                viewModel.onSearchQueryChanged(s.toString())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        // Filter spinner
        val filterOptions = arrayOf("All Files", "Video Files", "RAW Images", "Thermal Data", "Recent Sessions")
        val filterAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, filterOptions)
        filterAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        filterSpinner.adapter = filterAdapter
        
        filterSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                viewModel.applyFilter(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        // Refresh button
        refreshButton.setOnClickListener {
            viewModel.refreshSessions()
        }
    }

    /**
     * Observe ViewModel UiState using modern StateFlow pattern
     */
    private fun observeUiState() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    render(state)
                }
            }
        }
    }

    /**
     * Single function to render the entire UI based on the state
     */
    private fun render(state: FileViewUiState) {
        // Loading states
        progressBar.visibility = if (state.isLoadingSessions || state.isLoadingFiles) View.VISIBLE else View.GONE
        
        // Empty state
        emptyStateText.visibility = if (state.showEmptyState) View.VISIBLE else View.GONE
        
        // Update sessions list
        sessionsAdapter.submitList(state.sessions)
        
        // Update files list
        filesAdapter.submitList(state.sessionFiles)
        
        // Update session info
        state.selectedSession?.let { session ->
            updateSessionInfo(session)
        } ?: run {
            sessionInfoText.text = "No session selected"
        }
        
        // Handle error messages
        state.errorMessage?.let { error ->
            showError(error)
            viewModel.clearError()
        }
    }

    private fun updateSessionInfo(session: SessionItem) {
        val info = buildString {
            append("Session: ${session.sessionId}\n")
            append("Name: ${session.name}\n")
            append("Start: ${dateFormatter.format(Date(session.startTime))}\n")
            if (session.endTime > 0) {
                append("End: ${dateFormatter.format(Date(session.endTime))}\n")
                append("Duration: ${session.formattedDuration}\n")
            } else {
                append("Status: ${session.status}\n")
            }
            append("Files: ${session.fileCount}\n")
            append("Size: ${formatFileSize(session.totalSize)}\n")
            append("Devices: ${session.deviceTypes.joinToString(", ")}")
        }
        sessionInfoText.text = info
    }

    private fun handleFileClick(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle(fileItem.file.name)
            .setMessage("File size: ${formatFileSize(fileItem.file.length())}\nLast modified: ${dateFormatter.format(Date(fileItem.file.lastModified()))}")
            .setPositiveButton("Open") { _, _ ->
                openFile(fileItem)
            }
            .setNeutralButton("Share") { _, _ ->
                shareFile(fileItem)
            }
            .setNegativeButton("Delete") { _, _ ->
                confirmDeleteFile(fileItem)
            }
            .show()
    }

    private fun openFile(fileItem: FileItem) {
        try {
            val uri = FileProvider.getUriForFile(this, AUTHORITY, fileItem.file)
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, getMimeType(fileItem.type))
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(intent, "Open with"))
        } catch (e: Exception) {
            showError("Failed to open file: ${e.message}")
        }
    }

    private fun shareFile(fileItem: FileItem) {
        try {
            val uri = FileProvider.getUriForFile(this, AUTHORITY, fileItem.file)
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = getMimeType(fileItem.type)
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(intent, "Share file"))
        } catch (e: Exception) {
            showError("Failed to share file: ${e.message}")
        }
    }

    private fun confirmDeleteFile(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle("Delete File")
            .setMessage("Are you sure you want to delete ${fileItem.file.name}?")
            .setPositiveButton("Delete") { _, _ ->
                viewModel.deleteFile(fileItem)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showDeleteAllDialog() {
        AlertDialog.Builder(this)
            .setTitle("Delete All Sessions")
            .setMessage("Are you sure you want to delete all recording sessions? This action cannot be undone.")
            .setPositiveButton("Delete All") { _, _ ->
                viewModel.deleteAllSessions()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun formatDuration(durationMs: Long): String {
        val seconds = durationMs / 1000
        val minutes = seconds / 60
        val hours = minutes / 60
        return when {
            hours > 0 -> String.format("%d:%02d:%02d", hours, minutes % 60, seconds % 60)
            minutes > 0 -> String.format("%d:%02d", minutes, seconds % 60)
            else -> "${seconds}s"
        }
    }

    private fun formatFileSize(bytes: Long): String {
        return when {
            bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
            bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> "$bytes B"
        }
    }

    private fun getMimeType(fileType: FileType): String {
        return when (fileType) {
            FileType.VIDEO -> "video/*"
            FileType.RAW_IMAGE -> "image/*"
            FileType.THERMAL_DATA -> "text/plain"
        }
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
}
