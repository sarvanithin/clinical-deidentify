document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const apiStatus = document.getElementById('api-status');
    const statusDot = apiStatus.querySelector('.status-dot');
    const statusText = apiStatus.querySelector('.status-text');

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const textInput = document.getElementById('text-input');

    const processBtn = document.getElementById('process-btn');
    const clearBtn = document.getElementById('clear-btn');
    const resultsPanel = document.getElementById('results-panel');
    const outputText = document.getElementById('output-text');
    const legend = document.getElementById('legend');
    const copyBtn = document.getElementById('copy-btn');

    let currentFile = null;

    // Init
    checkApiStatus();

    // API Health Check
    async function checkApiStatus() {
        try {
            const resp = await fetch('/health');
            const data = await resp.json();
            if (data.status === 'healthy') {
                statusDot.classList.add('healthy');
                statusText.textContent = 'Backend Online';
            }
        } catch (e) {
            statusDot.classList.remove('healthy');
            statusText.textContent = 'Backend Offline';
        }
    }

    // Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    dropZone.addEventListener('dragover', () => dropZone.classList.add('drag-over'));
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

    dropZone.addEventListener('drop', e => {
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0]);
    });

    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'txt' && ext !== 'pdf') {
            alert('Please upload a .txt or .pdf file.');
            return;
        }

        currentFile = file;
        textInput.value = `File selected: ${file.name}`;
        textInput.disabled = true;

        // Show immediate indicator for PDF
        if (ext === 'pdf') {
            textInput.value += "\nNote: Text will be extracted upon processing.";
        } else {
            // Pre-read txt files for preview
            const reader = new FileReader();
            reader.onload = (e) => {
                textInput.value = e.target.result;
                textInput.disabled = false;
            };
            reader.readAsText(file);
        }
    }

    // Processing
    processBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text && !currentFile) return;

        // UI State
        processBtn.disabled = true;
        processBtn.querySelector('.btn-text').textContent = 'Processing...';
        processBtn.querySelector('.loader').hidden = false;

        try {
            let response;
            if (currentFile && (currentFile.name.endsWith('.pdf') || textInput.disabled)) {
                // Upload file
                const formData = new FormData();
                formData.append('file', currentFile);
                response = await fetch('/deidentify/file', {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Process text
                response = await fetch('/deidentify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
            }

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'API Error');
            }

            const result = await response.json();
            displayResults(result);
        } catch (error) {
            alert('Failed to process: ' + error.message);
        } finally {
            processBtn.disabled = false;
            processBtn.querySelector('.btn-text').textContent = 'De-identify PHI';
            processBtn.querySelector('.loader').hidden = true;
        }
    });

    function displayResults(data) {
        resultsPanel.hidden = false;

        // Render de-identified text with highlights
        // To make it interactive, we replace tokens with styled spans
        let displayHtml = data.deidentified;

        // Gather unique labels for the legend
        const labels = new Set();
        data.entities.forEach(ent => labels.add(ent.label));

        // Update Legend
        legend.innerHTML = '';
        labels.forEach(label => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `<span class="legend-dot"></span>${label}`;
            legend.appendChild(item);
        });

        // Simple masking visualization
        // Find entities in the deidentified text (e.g., [PER]) and highlight them
        const protectedLabels = Array.from(labels).map(l => `\\[${l}\\]`).join('|');
        if (protectedLabels) {
            const regex = new RegExp(`(${protectedLabels})`, 'g');
            displayHtml = displayHtml.replace(regex, '<span class="entity-highlight">$1</span>');
        }

        outputText.innerHTML = displayHtml;
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }

    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        resultsPanel.hidden = true;
        fileInput.value = '';
        currentFile = null;
        textInput.disabled = false;
    });

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(outputText.innerText);
        const originalIcon = copyBtn.innerHTML;
        copyBtn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" style="color:var(--success)"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
        setTimeout(() => copyBtn.innerHTML = originalIcon, 2000);
    });
});
