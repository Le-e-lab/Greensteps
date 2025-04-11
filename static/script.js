// Add error handling and user feedback
document.addEventListener('DOMContentLoaded', function() {
    // Update impact meter on page load
    const co2Element = document.getElementById('co2-saved');
    if (co2Element) {
        const co2Saved = parseFloat(co2Element.textContent);
        updateImpactMeter(co2Saved);
    }

    // Handle form submissions
    const actionForm = document.querySelector('.action-form');
    if (actionForm) {
        actionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            
            const formData = new FormData(this);
            
            fetch('/log-action', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to submit action. Please try again.');
            })
            .finally(() => {
                submitButton.disabled = false;
            });
        });
    }
});

function updateImpactMeter(kg) {
    const meter = document.querySelector('.meter-fill');
    const percentage = Math.min((kg / 10) * 1, 100);
    meter.style.width = `${percentage}%`;
}

document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('activityModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModal = document.getElementById('closeModal');
    const activityOptions = document.querySelectorAll('.activity-option');
    const selectedActivityInput = document.getElementById('selectedActivity');
    const activityForm = document.getElementById('activityForm');
    
    // Open modal
    openModalBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
    });
    
    // Close modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Select activity option
    activityOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            activityOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Set the hidden input value
            selectedActivityInput.value = this.dataset.value;
        });
    });
    
    // Form submission validation
    activityForm.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (!selectedActivityInput.value) {
            e.preventDefault();
            submitBtn.textContent = 'Please select an activity';
            submitBtn.style.backgroundColor = '#e53e3e';
            setTimeout(() => {
                submitBtn.textContent = 'Save Activity';
                submitBtn.style.backgroundColor = '#38a169';
            }, 2000);
            return;
        }
        
        submitBtn.innerHTML = `<div class="spinner"></div> Saving...`;
        submitBtn.disabled = true;
    });
});

// Add after modal submission
function showSuccessNotification(action) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `
        <span>✅</span>
        Logged ${action} successfully!
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Update form submission in app.py to redirect with action type

// Add after DOMContentLoaded event
function showAchievementNotification(badgeName) {
    const notification = document.createElement('div');
    notification.className = 'achievement-notification';
    notification.innerHTML = `
        🎉 <strong>New Achievement Unlocked!</strong><br>
        ${badgeName}
    `;
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.style.display = 'flex', 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Check for newly unlocked badges on page load
document.querySelectorAll('.badge.unlocked').forEach(badge => {
    if(badge.classList.contains('newly-unlocked')) {
        const badgeName = badge.querySelector('p').textContent;
        showAchievementNotification(badgeName);
    }
});