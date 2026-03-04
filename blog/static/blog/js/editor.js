// Editor functionality - auto-save, points management, reference pane

const WORTH_STEALING_TEXT_MAX = 500;

document.addEventListener('DOMContentLoaded', function() {
    const postForm = document.getElementById('post-form');
    const pointsContainer = document.getElementById('points-container');
    const addPointBtn = document.getElementById('add-point-btn');
    const saveIndicator = document.getElementById('save-indicator');
    const referencePane = document.getElementById('reference-pane');
    const closeReferenceBtn = document.getElementById('close-reference');
    const postSearch = document.getElementById('post-search');
    const insertQuoteBtn = document.getElementById('insert-quote-btn');
    const commentaryTextarea = document.getElementById('id_commentary');
    
    let autosaveInterval;
    let postId = window.postId || null;
    let autosaveUrl = window.autosaveUrl || null;
    
    // Initialize points if needed
    function initializePoints() {
        const points = pointsContainer.querySelectorAll('.point-editor');
        if (points.length === 0) {
            for (let i = 0; i < 10; i++) {
                addPoint();
            }
        }
        // Set initial character counters for all point textareas
        pointsContainer.querySelectorAll('.point-text-input').forEach(function(ta) {
            updatePointCharCount(ta);
        });
    }
    
    // Add point
    function addPoint() {
        const pointCount = pointsContainer.querySelectorAll('.point-editor').length;
        if (pointCount >= 10) {
            alert('Maximum 10 points allowed');
            return;
        }
        
        const pointIndex = pointCount;
        const pointDiv = document.createElement('div');
        pointDiv.className = 'point-editor';
        pointDiv.setAttribute('data-point-index', pointIndex);
        pointDiv.innerHTML = `
            <div class="point-header">
                <span class="point-number-badge">${pointCount + 1}</span>
                <button type="button" class="btn-remove-point" onclick="removePoint(${pointIndex})">Remove</button>
            </div>
            <input type="text" 
                   class="point-title-input" 
                   placeholder="Point title"
                   data-point-field="title">
            <textarea class="point-text-input" 
                      placeholder="Point description"
                      rows="3"
                      data-point-field="text"
                      maxlength="${WORTH_STEALING_TEXT_MAX}"></textarea>
            <div class="point-char-count" aria-live="polite"><span class="point-char-remaining">${WORTH_STEALING_TEXT_MAX}</span> characters remaining</div>
        `;
        pointsContainer.appendChild(pointDiv);
        updatePointNumbers();
        updatePointCharCount(pointDiv.querySelector('.point-text-input'));
    }
    
    // Remove point
    window.removePoint = function(index) {
        const point = pointsContainer.querySelector(`[data-point-index="${index}"]`);
        if (point) {
            point.remove();
            updatePointNumbers();
        }
    };
    
    // Update "characters remaining" for one Worth Stealing point
    function updatePointCharCount(textarea) {
        if (!textarea) return;
        const pointEditor = textarea.closest('.point-editor');
        const remainingEl = pointEditor?.querySelector('.point-char-remaining');
        if (!remainingEl) return;
        const len = (textarea.value || '').length;
        const remaining = Math.max(0, WORTH_STEALING_TEXT_MAX - len);
        remainingEl.textContent = remaining;
        const countDiv = pointEditor.querySelector('.point-char-count');
        if (countDiv) {
            countDiv.classList.toggle('char-count-warning', remaining <= 50);
            countDiv.classList.toggle('char-count-zero', remaining === 0);
        }
    }

    // Update point numbers
    function updatePointNumbers() {
        const points = pointsContainer.querySelectorAll('.point-editor');
        points.forEach((point, index) => {
            point.setAttribute('data-point-index', index);
            const badge = point.querySelector('.point-number-badge');
            if (badge) {
                badge.textContent = index + 1;
            }
            const removeBtn = point.querySelector('.btn-remove-point');
            if (removeBtn) {
                removeBtn.setAttribute('onclick', `removePoint(${index})`);
            }
        });
    }
    
    // Get points data
    function getPointsData() {
        const points = [];
        const pointEditors = pointsContainer.querySelectorAll('.point-editor');
        pointEditors.forEach(point => {
            const title = point.querySelector('.point-title-input').value.trim();
            const text = point.querySelector('.point-text-input').value.trim();
            if (title || text) {
                points.push({ title, text });
            }
        });
        // Ensure we have 10 points
        while (points.length < 10) {
            points.push({ title: '', text: '' });
        }
        return points.slice(0, 10);
    }
    
    // Auto-save
    function autosave() {
        if (!autosaveUrl || !postForm) return;
        
        const guestIds = Array.from(document.querySelectorAll('input[name="guests"]:checked')).map(function(cb) { return cb.value; });
        const tagIds = Array.from(document.querySelectorAll('input[name="tags"]:checked')).map(function(cb) { return cb.value; });
        const formData = {
            title: document.getElementById('id_title')?.value || '',
            publish_date: document.getElementById('id_publish_date')?.value || '',
            author_id: document.getElementById('id_author')?.value || '',
            book_id: document.getElementById('id_book')?.value || '',
            series_order: document.getElementById('id_series_order')?.value || null,
            guest_ids: guestIds,
            tag_ids: tagIds,
            points: getPointsData(),
            commentary: document.getElementById('id_commentary')?.value || ''
        };
        
        fetch(autosaveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                saveIndicator.textContent = 'Saved';
                saveIndicator.classList.add('saved');
                setTimeout(() => {
                    saveIndicator.textContent = '';
                    saveIndicator.classList.remove('saved');
                }, 2000);
                
                // Update post ID if this was a new post
                if (!postId && data.post_id) {
                    postId = data.post_id;
                    autosaveUrl = `/write/autosave/${postId}/`;
                }
            }
        })
        .catch(error => {
            console.error('Autosave error:', error);
        });
    }
    
    // Setup auto-save
    if (postForm && autosaveUrl) {
        // Auto-save on form changes (include checkbox lists for guests/tags)
        const formInputs = postForm.querySelectorAll('input, textarea, select');
        formInputs.forEach(input => {
            input.addEventListener('change', autosave);
            input.addEventListener('input', function() {
                clearTimeout(autosaveInterval);
                autosaveInterval = setTimeout(autosave, 2000);
            });
        });
        document.querySelectorAll('#guests-list input[type="checkbox"], #tags-list input[type="checkbox"]').forEach(function(cb) {
            cb.addEventListener('change', autosave);
        });
        
        // Auto-save every 30 seconds
        setInterval(autosave, 30000);
    }
    
    // Update points JSON before form submission
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            const pointsJson = document.getElementById('points-json');
            if (pointsJson) {
                pointsJson.value = JSON.stringify(getPointsData());
            }
        });
    }
    
    // Reference pane functionality
    const sidebarPosts = document.querySelectorAll('.sidebar-post-item');
    sidebarPosts.forEach(postItem => {
        postItem.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            // In a real implementation, you'd fetch the post content via AJAX
            // For now, we'll just show the pane
            referencePane.style.display = 'block';
            document.getElementById('reference-content').innerHTML = `
                <h4>${this.querySelector('h4').textContent}</h4>
                <p class="post-meta-small">${this.querySelector('.post-meta-small').textContent}</p>
                <p>${this.querySelector('.post-excerpt').textContent}</p>
                <p><em>Full reference view would load here via AJAX</em></p>
            `;
        });
    });
    
    if (closeReferenceBtn) {
        closeReferenceBtn.addEventListener('click', function() {
            referencePane.style.display = 'none';
        });
    }
    
    // Preview button (now a link, so no JS needed)
    
    // Post search
    if (postSearch) {
        postSearch.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const posts = document.querySelectorAll('.sidebar-post-item');
            posts.forEach(post => {
                const text = post.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    post.style.display = 'block';
                } else {
                    post.style.display = 'none';
                }
            });
        });
    }
    
    // Insert Quote functionality
    if (insertQuoteBtn && commentaryTextarea) {
        insertQuoteBtn.addEventListener('click', function() {
            const textarea = commentaryTextarea;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const selectedText = textarea.value.substring(start, end);
            
            // If text is selected, wrap it in a quote block
            // Otherwise, insert a quote template
            let quoteText;
            if (selectedText.trim()) {
                // Wrap selected text in blockquote
                const lines = selectedText.split('\n');
                quoteText = lines.map(line => {
                    // Don't add > if line is already a blockquote
                    if (line.trim().startsWith('>')) {
                        return line;
                    }
                    // Preserve leading whitespace but add > 
                    const trimmed = line.trimStart();
                    const leadingWhitespace = line.substring(0, line.length - trimmed.length);
                    return leadingWhitespace + '> ' + trimmed;
                }).join('\n');
                
                // Add attribution line if not present
                if (!quoteText.includes('\n> \n> —')) {
                    quoteText += '\n> \n> — Author Name';
                }
            } else {
                // Insert a quote template with attribution placeholder
                quoteText = '> Your quote text here\n> \n> — Author Name\n\n';
            }
            
            // Insert the quote at cursor position
            const beforeText = textarea.value.substring(0, start);
            const afterText = textarea.value.substring(end);
            const newText = beforeText + quoteText + afterText;
            
            textarea.value = newText;
            
            // Set cursor position at the start of the quote (or attribution if selected text was used)
            let newCursorPos;
            if (selectedText.trim()) {
                // Position cursor at the attribution line
                newCursorPos = textarea.value.indexOf('— Author Name', start);
                if (newCursorPos > 0) {
                    // Select "Author Name" for easy editing
                    textarea.setSelectionRange(newCursorPos + 2, newCursorPos + 12);
                } else {
                    textarea.setSelectionRange(start + quoteText.length, start + quoteText.length);
                }
            } else {
                // Position cursor at the start of the quote text
                newCursorPos = textarea.value.indexOf('Your quote text here', start);
                if (newCursorPos > 0) {
                    textarea.setSelectionRange(newCursorPos, newCursorPos + 20);
                } else {
                    newCursorPos = start + quoteText.indexOf('> ') + 2;
                    textarea.setSelectionRange(newCursorPos, newCursorPos);
                }
            }
            
            textarea.focus();
            
            // Trigger change event for auto-save
            textarea.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }
    
    // Worth Stealing character counter: update on input
    if (pointsContainer) {
        pointsContainer.addEventListener('input', function(e) {
            if (e.target.classList.contains('point-text-input')) {
                updatePointCharCount(e.target);
            }
        });
    }

    // Initialize
    if (addPointBtn) {
        addPointBtn.addEventListener('click', addPoint);
    }
    
    initializePoints();
});

