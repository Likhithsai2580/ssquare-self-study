// ... existing code ...

function updateNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            const notificationCount = data.length;
            const notificationBadge = document.getElementById('notification-badge');
            if (notificationBadge) {
                notificationBadge.textContent = notificationCount;
                notificationBadge.style.display = notificationCount > 0 ? 'inline' : 'none';
            }
            // Update notification list in the UI
            const notificationList = document.getElementById('notification-list');
            if (notificationList) {
                notificationList.innerHTML = data.map(notification => `
                    <li>${notification.message}</li>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Initialize notifications on page load
document.addEventListener('DOMContentLoaded', () => {
    updateNotifications();
});

// ... rest of the existing code ...