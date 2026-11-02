// আপনজন (Aponjon) Main JavaScript Client
document.addEventListener('DOMContentLoaded', function () {
    // Dropdown toggle for notifications
    const notifBtn = document.getElementById('notif-dropdown-btn');
    const notifMenu = document.getElementById('notif-dropdown-menu');

    if (notifBtn && notifMenu) {
        notifBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            notifMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', function (e) {
            if (!notifMenu.contains(e.target) && !notifBtn.contains(e.target)) {
                notifMenu.classList.add('hidden');
            }
        });
    }

    // Auto-dismiss Django alert messages after 5 seconds
    const alerts = document.querySelectorAll('.auto-dismiss');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });
});
