// =====================
// Drag & Drop + File Picker
// =====================
function setupDragAndDrop(box, fileInput, displayInput, pickerTextEl) {
    const accept = fileInput.accept;
    const isVideo = accept.includes('video');
    const isImage = accept.includes('image');
    const plusIcon = displayInput.querySelector('.plus-icon');
    const dropzoneText = displayInput.querySelector('.dropzone-text');
    const uploadBtn = box.querySelector('.upload-btn');

    // Only the dropzone triggers file input
    displayInput.addEventListener('click', () => {
        if (!displayInput.classList.contains('disabled')) {
            fileInput.click();
        }
    });

    // Drag over
    box.addEventListener('dragover', e => {
        e.preventDefault();
        if (!displayInput.classList.contains('disabled')) {
            box.classList.add('dragover');
        }
    });

    // Drag leave
    box.addEventListener('dragleave', e => {
        e.preventDefault();
        box.classList.remove('dragover');
    });

    // Drop file
    box.addEventListener('drop', e => {
        e.preventDefault();
        box.classList.remove('dragover');
        if (displayInput.classList.contains('disabled')) return;
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if ((isVideo && !file.type.startsWith('video/')) ||
                (isImage && !file.type.startsWith('image/'))) {
                alert(isVideo ? "Please upload a video file." : "Please upload an image file.");
                return;
            }
            fileInput.files = files;
            plusIcon.style.display = 'none';
            dropzoneText.textContent = file.name;
            displayInput.classList.add('disabled');
            if (uploadBtn) uploadBtn.disabled = false; // Enable button after upload
        }
    });

    // File input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if ((isVideo && !file.type.startsWith('video/')) ||
                (isImage && !file.type.startsWith('image/'))) {
                alert(isVideo ? "Please upload a video file." : "Please upload an image file.");
                fileInput.value = '';
                plusIcon.style.display = '';
                dropzoneText.textContent = isVideo
                    ? "Drag & drop or click to select a video"
                    : "Drag & drop or click to select a photo";
                displayInput.classList.remove('disabled');
                if (uploadBtn) uploadBtn.disabled = true; // Disable button if invalid
                return;
            }
            plusIcon.style.display = 'none';
            dropzoneText.textContent = file.name;
            displayInput.classList.add('disabled');
            if (uploadBtn) uploadBtn.disabled = false; // Enable button after upload
        }
    });

    // Initially disable the button
    if (uploadBtn) uploadBtn.disabled = true;
}

// =====================
// Caption Modal Handling
// =====================
function setupCaptionModal(modalId, openBtn, saveBtn, cancelBtn, textArea) {
    const modal = document.getElementById(modalId);

    openBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    saveBtn.addEventListener('click', () => {
        const text = textArea.value.trim();
        if (text) {
            openBtn.dataset.caption = text; // Store caption in button
        }
        modal.style.display = 'none';
    });

    window.addEventListener('click', e => {
        if (e.target === modal) modal.style.display = 'none';
    });
}

// =====================
// Timestamp Handling
// =====================
function setupTimestampToggle(toggleBtn, container) {
    toggleBtn.addEventListener('change', () => {
        container.style.display = toggleBtn.checked ? 'flex' : 'none';
    });
}

function addTimestampRow(container, previewContainer) {
    const row = document.createElement('div');
    row.classList.add('timestamp-row');

    const startInput = document.createElement('input');
    startInput.type = 'text';
    startInput.placeholder = 'Start Time';

    const endInput = document.createElement('input');
    endInput.type = 'text';
    endInput.placeholder = 'End Time';

    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'X';
    removeBtn.style.background = 'red';
    removeBtn.style.color = '#fff';
    removeBtn.style.border = 'none';
    removeBtn.style.cursor = 'pointer';
    removeBtn.style.borderRadius = '4px';

    removeBtn.addEventListener('click', () => {
        container.removeChild(row);
        previewContainer.removeChild(previewDiv);
    });

    row.appendChild(startInput);
    row.appendChild(endInput);
    row.appendChild(removeBtn);
    container.appendChild(row);

    // Preview
    const previewDiv = document.createElement('div');
    previewDiv.textContent = `Start: ${startInput.value || '0'} - End: ${endInput.value || '0'}`;
    previewContainer.appendChild(previewDiv);

    startInput.addEventListener('input', () => {
        previewDiv.textContent = `Start: ${startInput.value || '0'} - End: ${endInput.value || '0'}`;
    });
    endInput.addEventListener('input', () => {
        previewDiv.textContent = `Start: ${startInput.value || '0'} - End: ${endInput.value || '0'}`;
    });
}

// =====================
// Upload Meme (Dummy for Frontend)
// =====================
function uploadMeme(fileInput, captionBtn, galleryContainer) {
    if (fileInput.files.length === 0) {
        alert('Please select a file!');
        return;
    }

    const file = fileInput.files[0];
    const caption = captionBtn.dataset.caption || '';

    const reader = new FileReader();
    reader.onload = function(e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = caption;
        galleryContainer.appendChild(img);
    };
    reader.readAsDataURL(file);
}

// =====================
// Clear Selection Functions
// =====================
function refreshYoutube() {
    const ytInput = document.getElementById('youtubeLink');
    if (ytInput) ytInput.value = '';
    setActiveUpload(null); // This will re-enable all boxes and disable the button
}
function refreshPhoto() {
    const fileInput = document.getElementById('photoFile');
    const dropzone = document.getElementById('photoDisplay');
    if (fileInput) fileInput.value = '';
    if (dropzone) {
        const plusIcon = dropzone.querySelector('.plus-icon');
        const dropzoneText = dropzone.querySelector('.dropzone-text');
        if (plusIcon) plusIcon.style.display = '';
        if (dropzoneText) dropzoneText.textContent = "Drag & drop or click to select a photo";
        dropzone.classList.remove('disabled');
    }
    setActiveUpload(null); // This will re-enable all boxes and disable the button
}
function refreshVideo() {
    const fileInput = document.getElementById('videoFile');
    const dropzone = document.getElementById('videoDisplay');
    if (fileInput) fileInput.value = '';
    if (dropzone) {
        const plusIcon = dropzone.querySelector('.plus-icon');
        const dropzoneText = dropzone.querySelector('.dropzone-text');
        if (plusIcon) plusIcon.style.display = '';
        if (dropzoneText) dropzoneText.textContent = "Drag & drop or click to select a video";
        dropzone.classList.remove('disabled');
    }
    setActiveUpload(null); // This will re-enable all boxes and disable the button
}

// =====================
// Initialize Everything
// =====================
document.addEventListener('DOMContentLoaded', () => {
    // Only set up drag & drop for boxes with file input and dropzone input
    document.querySelectorAll('.upload-box').forEach(box => {
        const fileInput = box.querySelector('input[type="file"]');
        const dropzoneInput = box.querySelector('.dropzone-input');
        const nameDisplay = box.querySelector('.file-name');

        // Only set up drag & drop if both fileInput and dropzoneInput exist
        if (fileInput && dropzoneInput) {
            setupDragAndDrop(box, fileInput, dropzoneInput, null, nameDisplay);
        }
    });

    let activeUploadType = null; // "youtube", "photo", or "video"

    function setActiveUpload(type) {
        activeUploadType = type;
        const mainBtn = document.getElementById('mainGenerateBtn');
        const photoBox = document.getElementById('photoBox');
        const videoBox = document.getElementById('videoBox');
        const youtubeBox = document.getElementById('youtubeBox');
        const photoInput = document.getElementById('photoFile');
        const videoInput = document.getElementById('videoFile');
        const ytInput = document.getElementById('youtubeLink');
        const photoDropzone = document.getElementById('photoDisplay');
        const videoDropzone = document.getElementById('videoDisplay');

        // Always reset all
        photoBox.classList.remove('disabled');
        videoBox.classList.remove('disabled');
        youtubeBox.classList.remove('disabled');
        photoDropzone.classList.remove('disabled');
        videoDropzone.classList.remove('disabled');
        if (photoInput) photoInput.disabled = false;
        if (videoInput) videoInput.disabled = false;
        if (ytInput) ytInput.disabled = false;

        // If no type, disable main button and return
        if (!type) {
            mainBtn.disabled = true;
            return;
        }

        // Otherwise, enable main button and disable others
        mainBtn.disabled = false;
        if (type === 'photo') {
            videoBox.classList.add('disabled');
            youtubeBox.classList.add('disabled');
            videoDropzone.classList.add('disabled');
            if (videoInput) videoInput.disabled = true;
            if (ytInput) ytInput.disabled = true;
        } else if (type === 'video') {
            photoBox.classList.add('disabled');
            youtubeBox.classList.add('disabled');
            photoDropzone.classList.add('disabled');
            if (photoInput) photoInput.disabled = true;
            if (ytInput) ytInput.disabled = true;
        } else if (type === 'youtube') {
            photoBox.classList.add('disabled');
            videoBox.classList.add('disabled');
            photoDropzone.classList.add('disabled');
            videoDropzone.classList.add('disabled');
            if (photoInput) photoInput.disabled = true;
            if (videoInput) videoInput.disabled = true;
        }
    }

    function showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }

    function showStatus(message) {
        // Optionally update loading text or use a modal for errors
        alert(message);
    }

    function pollTaskStatus(task_id) {
        fetch(`http://127.0.0.1:5000/status/${task_id}`)
            .then(res => res.json())
            .then(data => {
                if (!data.ready) {
                    setTimeout(() => pollTaskStatus(task_id), 1500);
                } else {
                    showLoading(false);
                    if (data.success) {
                        showOutputModal(data.memes); // Show output in a popup
                    } else {
                        showStatus("Error: " + (data.error || "Unknown error"));
                    }
                }
            })
            .catch(() => {
                showLoading(false);
                showStatus("Error connecting to server.");
            });
    }

    function uploadYoutube() {
        const ytInput = document.getElementById('youtubeLink');
        if (!ytInput.value.trim()) {
            showStatus("Please enter a YouTube link.");
            return;
        }
        showLoading(true);
        fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ youtubeLink: ytInput.value.trim() })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showStatus("Processing YouTube link...");
                pollTaskStatus(data.task_id);
            } else {
                showStatus("Error: " + (data.error || "Unknown error"));
            }
        })
        .catch(() => showStatus("Error connecting to server."));
    }

    function uploadPhoto() {
        const fileInput = document.getElementById('photoFile');
        if (!fileInput.files.length) {
            showStatus("Please select a photo.");
            return;
        }
        showLoading(true);
        const formData = new FormData();
        formData.append('photoFile', fileInput.files[0]);
        fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showStatus("Processing photo...");
                pollTaskStatus(data.task_id);
            } else {
                showStatus("Error: " + (data.error || "Unknown error"));
            }
        })
        .catch(() => showStatus("Error connecting to server."));
    }

    function uploadVideo() {
        const fileInput = document.getElementById('videoFile');
        if (!fileInput.files.length) {
            showStatus("Please select a video.");
            return;
        }
        showLoading(true);
        const formData = new FormData();
        formData.append('videoFile', fileInput.files[0]);
        fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showStatus("Processing video...");
                pollTaskStatus(data.task_id);
            } else {
                showStatus("Error: " + (data.error || "Unknown error"));
            }
        })
        .catch(() => showStatus("Error connecting to server."));
    }

    // --- YouTube logic ---
    const ytInput = document.getElementById('youtubeLink');
    if (ytInput) {
        ytInput.addEventListener('input', () => {
            if (ytInput.value.trim() !== '') {
                setActiveUpload('youtube');
            } else if (activeUploadType === 'youtube') {
                setActiveUpload(null);
            }
        });
    }

    // --- Photo logic ---
    const photoInput = document.getElementById('photoFile');
    const photoDropzone = document.getElementById('photoDisplay');
    if (photoInput && photoDropzone) {
        photoInput.addEventListener('change', () => {
            if (photoInput.files.length > 0) {
                setActiveUpload('photo');
            } else if (activeUploadType === 'photo') {
                setActiveUpload(null);
            }
        });
    }

    // --- Video logic ---
    const videoInput = document.getElementById('videoFile');
    const videoDropzone = document.getElementById('videoDisplay');
    if (videoInput && videoDropzone) {
        videoInput.addEventListener('change', () => {
            if (videoInput.files.length > 0) {
                setActiveUpload('video');
            } else if (activeUploadType === 'video') {
                setActiveUpload(null);
            }
        });
    }

    // --- Main Generate Meme button logic ---
    document.getElementById('mainGenerateBtn').addEventListener('click', () => {
        if (activeUploadType === 'youtube') {
            uploadYoutube();
        } else if (activeUploadType === 'photo') {
            uploadPhoto();
        } else if (activeUploadType === 'video') {
            uploadVideo();
        }
    });
});

function showOutputModal(memes) {
    const modal = document.getElementById('outputModal');
    const imagesDiv = document.getElementById('outputImages');
    imagesDiv.innerHTML = '';
    memes.forEach(url => {
        const img = document.createElement('img');
        img.src = url;
        imagesDiv.appendChild(img);
    });
    modal.style.display = 'flex';
}
function closeOutputModal() {
    document.getElementById('outputModal').style.display = 'none';
}

function showMemesPage(memes) {
    // Replace main content with memes grid
    document.body.innerHTML = `
      <div class="memes-page">
        <h2>Your Memes</h2>
        <div class="memes-grid">
          ${memes.map((url, idx) => `
            <div class="meme-card">
              ${url.match(/\.(mp4|webm)$/) ? 
                `<video src="${url}" controls></video>` :
                `<img src="${url}" alt="Meme ${idx+1}">`
              }
              <button onclick="downloadMeme('${url}')">Download</button>
              <button onclick="showCustomCaptionBox('${url}')">Custom Caption</button>
            </div>
          `).join('')}
        </div>
      </div>
      <div id="customCaptionModal" class="modal" style="display:none;">
        <div class="modal-content">
          <span class="close" onclick="closeCustomCaptionModal()">&times;</span>
          <h3>Enter Custom Caption</h3>
          <input type="text" id="customCaptionInput" placeholder="Your caption">
          <button onclick="submitCustomCaption()">Submit</button>
        </div>
      </div>
    `;
    window.selectedMemeForCaption = null;
}

function downloadMeme(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = url.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function showCustomCaptionBox(url) {
    window.selectedMemeForCaption = url;
    document.getElementById('customCaptionModal').style.display = 'flex';
}

function closeCustomCaptionModal() {
    document.getElementById('customCaptionModal').style.display = 'none';
}

function submitCustomCaption() {
    const caption = document.getElementById('customCaptionInput').value.trim();
    const meme_file = window.selectedMemeForCaption;
    if (!caption) return alert('Please enter a caption.');
    fetch('http://127.0.0.1:5000/custom_caption', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            meme_file: meme_file,
            caption: caption,
            custom: 'y'
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Custom caption submitted!');
            closeCustomCaptionModal();
        } else {
            alert('Error submitting caption.');
        }
    });
}

function showOutputPage() {
    fetch('http://127.0.0.1:5000/get_memes')
      .then(res => res.json())
      .then(data => showMemesPage(data.memes));
}
