// Results page javascript
document.addEventListener('DOMContentLoaded', () => {
    // Get task_id and type from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    const type = urlParams.get('type');
    
    const loading = document.getElementById('loading');
    const resultsGrid = document.getElementById('resultsGrid');
    
    // If task_id is provided, poll for status
    if (taskId) {
        pollTaskStatus(taskId);
    } else {
        // Otherwise fetch all recent memes
        fetchAllMemes();
    }
    
    // Poll the server for task status
    function pollTaskStatus(taskId) {
        fetch(`http://127.0.0.1:5000/status/${taskId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.ready) {
                    // If not ready, poll again after a delay
                    setTimeout(() => pollTaskStatus(taskId), 1500);
                } else {
                    // Hide loading indicator
                    loading.style.display = 'none';
                    
                    if (data.success) {
                        // Show the memes
                        displayMemes(data.memes);
                    } else {
                        // Show error message
                        resultsGrid.innerHTML = `
                            <div class="no-results">
                                <h3>Error</h3>
                                <p>${data.error || 'An error occurred while generating memes'}</p>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                loading.style.display = 'none';
                resultsGrid.innerHTML = `
                    <div class="no-results">
                        <h3>Connection Error</h3>
                        <p>Failed to connect to the server. Please check if the server is running.</p>
                    </div>
                `;
                console.error('Error fetching status:', error);
            });
    }
    
    // Fetch all available memes
    function fetchAllMemes() {
        fetch('http://127.0.0.1:5000/get_all_memes')
            .then(res => res.json())
            .then(data => {
                loading.style.display = 'none';
                displayMemes(data.memes);
            })
            .catch(error => {
                loading.style.display = 'none';
                resultsGrid.innerHTML = `
                    <div class="no-results">
                        <h3>Connection Error</h3>
                        <p>Failed to connect to the server. Please check if the server is running.</p>
                    </div>
                `;
                console.error('Error fetching memes:', error);
            });
    }
    
    // Display the memes in the grid
    function displayMemes(memes) {
        if (!memes || memes.length === 0) {
            resultsGrid.innerHTML = `
                <div class="no-results">
                    <h3>No memes found</h3>
                    <p>No memes were generated or found in the output folders.</p>
                </div>
            `;
            return;
        }
        
        resultsGrid.innerHTML = memes.map((url, index) => {
            const isVideo = url.match(/\.(mp4|webm)$/i);
            return `
                <div class="meme-card">
                    ${isVideo 
                        ? `<video 
                            width="100%" 
                            height="auto" 
                            controls 
                            crossorigin="anonymous"
                            preload="metadata"
                            style="background: #000;"
                          >
                            <source src="${url}" type="${url.toLowerCase().endsWith('.mp4') ? 'video/mp4' : 'video/webm'}">
                            Your browser does not support the video tag.
                          </video>` 
                        : `<img src="${url}" alt="Meme ${index + 1}" loading="lazy">`
                    }
                    <div class="meme-actions">
                        <button class="view-btn" onclick="openMeme('${url}')" data-tooltip="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="download-btn" onclick="downloadMeme('${url}')" data-tooltip="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="share-btn" onclick="shareMeme('${url}')" data-tooltip="Share">
                            <i class="fas fa-share-alt"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
});

// Open the meme in a new tab
function openMeme(url) {
    window.open(url, '_blank');
}

// Download the meme
function downloadMeme(url) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const a = document.createElement('a');
            const url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = url.split('/').pop();
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error downloading file:', error);
            alert('Failed to download the file. Please try again.');
        });
}

// Share meme (using Web Share API if available)
async function shareMeme(url) {
    try {
        // Fetch the image/video file
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Determine the file type and name
        const isVideo = url.match(/\.(mp4|webm)$/i);
        const fileName = url.split('/').pop();
        const fileType = isVideo ? 'video/mp4' : 'image/jpeg';
        
        // Create a File object from the blob
        const file = new File([blob], fileName, { type: fileType });

        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            // Share the actual file if supported
            await navigator.share({
                title: 'Check out this AI-generated meme!',
                text: 'Here\'s a meme I created with AI Meme Generator',
                files: [file]
            });
        } else if (navigator.share) {
            // Fallback to URL sharing if file sharing not supported
            await navigator.share({
                title: 'Check out this AI-generated meme!',
                text: 'Here\'s a meme I created with AI Meme Generator',
                url: url
            });
        } else {
            // Fallback for browsers that don't support sharing
            fallbackShare(url);
        }
    } catch (error) {
        console.error('Error sharing:', error);
        fallbackShare(url);
    }
}

// Fallback share method
function fallbackShare(url) {
    // Try to download the file directly
    const a = document.createElement('a');
    a.href = url;
    a.download = url.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Also copy the link as backup
    copyMemeLink(url);
    alert('Meme downloaded and link copied to clipboard!');
}

// Copy meme link to clipboard
function copyMemeLink(url) {
    // Create temporary input for copying
    const tempInput = document.createElement('input');
    tempInput.value = url;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    
    // Show brief feedback
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.textContent = 'Link copied!';
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 1500);
    }, 10);
}