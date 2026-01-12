// Archive page filter functionality

document.addEventListener('DOMContentLoaded', function() {
    // Newsletter form submission
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(newsletterForm);
            const messageDiv = document.getElementById('newsletter-message');
            
            fetch(newsletterForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = data.message;
                    messageDiv.style.color = '#4caf50';
                    newsletterForm.reset();
                } else {
                    messageDiv.textContent = 'Something went wrong. Please try again.';
                    messageDiv.style.color = '#d32f2f';
                }
            })
            .catch(error => {
                messageDiv.textContent = 'Something went wrong. Please try again.';
                messageDiv.style.color = '#d32f2f';
            });
        });
    }
});

