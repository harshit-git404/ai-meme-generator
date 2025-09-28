// Results page javascript
document.addEventListener('DOMContentLoaded', () => {
    // Get task_id and type from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    const type = urlParams.get('type');
    
    const loading = document.getElementById('loading');
    const resultsGrid = document.getElementById('resultsGrid');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Set up refresh button
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loading.style.display = 'block';
            resultsGrid.innerHTML = '';
            if (taskId) {
                pollTaskStatus(taskId);
            } else {
                fetchAllMemes();
            }
        });
    }
    
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
                        ? `<video src="${url}" controls preload="metadata" poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M8 5v14l11-7z' fill='%23ffffff'/%3E%3C/svg%3E"></video>` 
                        : `<img src="${url}" alt="Meme ${index + 1}" loading="lazy">`
                    }
                    <div class="meme-actions">
                        <button class="download-btn" onclick="downloadMeme('${url}')">Download</button>
                        <button class="share-btn" onclick="shareMeme('${url}')">Share</button>
                        <button class="copy-btn" onclick="copyMemeLink('${url}')">Copy Link</button>
                    </div>
                </div>
            `;
        }).join('');
    }
});

// Download the meme
function downloadMeme(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = url.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Share meme (using Web Share API if available)
function shareMeme(url) {
    if (navigator.share) {
        navigator.share({
            title: 'Check out this AI-generated meme!',
            text: 'Here\'s a meme I created with AI Meme Generator',
            url: url,
        })
        .catch(error => {
            console.error('Error sharing:', error);
            fallbackShare(url);
        });
    } else {
        fallbackShare(url);
    }
}

// Fallback share method
function fallbackShare(url) {
    copyMemeLink(url);
    alert('Link copied to clipboard. You can now paste and share it!');
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