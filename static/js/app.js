/**
 * Transcript Processor App
 * Main JavaScript for Flask frontend
 */

let currentSessionId = null;

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

const fileInput = document.getElementById('file-input');
const fileDropZone = document.querySelector('.file-drop-zone');
const fileInfoDisplay = document.getElementById('file-info');
const processBtn = document.getElementById('process-btn');

// File drag and drop
fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropZone.classList.add('dragover');
});

fileDropZone.addEventListener('dragleave', () => {
    fileDropZone.classList.remove('dragover');
});

fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

/**
 * Handle file selection and upload
 */
async function handleFileSelect(file) {
    if (!file.name.endsWith('.csv')) {
        showStatus('❌ Only CSV files are allowed', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showStatus(`❌ ${data.error}`, 'error');
            return;
        }

        currentSessionId = data.session_id;
        
        // Display file info
        document.getElementById('filename').textContent = data.filename;
        document.getElementById('filerows').textContent = data.rows;
        document.getElementById('filecolumns').textContent = data.columns.join(', ');
        fileInfoDisplay.style.display = 'block';
        
        // Enable process button
        processBtn.disabled = false;
        
        showStatus(`✅ File uploaded successfully: ${data.rows} rows`, 'success');
    } catch (error) {
        showStatus(`❌ Upload error: ${error.message}`, 'error');
    }
}

// ============================================================================
// PROCESSING
// ============================================================================

const enableSummary = document.getElementById('enable-summary');
const maxWords = document.getElementById('max-words');
const sliderValue = document.getElementById('slider-value');

// Update slider value display
maxWords.addEventListener('input', (e) => {
    sliderValue.textContent = e.target.value;
});

// Process button click
processBtn.addEventListener('click', processFile);

/**
 * Process the uploaded file
 */
async function processFile() {
    if (!currentSessionId) {
        showStatus('❌ No file loaded', 'error');
        return;
    }

    processBtn.disabled = true;
    processBtn.innerHTML = '⏳ Processing...';

    try {
        const response = await fetch(`/api/process/${currentSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                enable_summary: enableSummary.checked,
                max_words: parseInt(maxWords.value)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error);
        }

        // Display results
        displayResults(data);
        showStatus(`✅ Processing complete! ${data.rows_processed} rows processed`, 'success');

    } catch (error) {
        showStatus(`❌ Processing error: ${error.message}`, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '🚀 Process Transcript';
    }
}

/**
 * Display processing results
 */
function displayResults(data) {
    const resultsSection = document.getElementById('results-section');
    const analyticsOutput = document.getElementById('analytics-output');
    const summaryOutput = document.getElementById('summary-output');

    analyticsOutput.textContent = data.analytics || 'No analytics available';
    summaryOutput.textContent = data.summary || 'No summary generated';

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================================
// TAB SWITCHING
// ============================================================================

const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        btn.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    });
});

// ============================================================================
// DOWNLOAD
// ============================================================================

const downloadBtn = document.getElementById('download-btn');

if (downloadBtn) {
    downloadBtn.addEventListener('click', downloadResults);
}

/**
 * Download results as CSV
 */
function downloadResults() {
    if (!currentSessionId) {
        showStatus('❌ No session available', 'error');
        return;
    }

    window.location.href = `/api/download/${currentSessionId}`;
}

// ============================================================================
// STATUS MESSAGES
// ============================================================================

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    const statusSection = document.getElementById('status-section');
    const statusMessage = document.getElementById('status-message');
    
    statusMessage.textContent = message;
    statusSection.className = `status-section alert alert-${type}`;
    statusSection.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusSection.style.display = 'none';
        }, 5000);
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Transcript Processor App loaded');
});
