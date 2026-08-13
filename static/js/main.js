// Client-side interactions & utilities for CertifyCloud
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Copy to clipboard helper
    const copyBtns = document.querySelectorAll('.btn-copy');
    copyBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-clipboard-target');
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
                const textToCopy = targetEl.innerText || targetEl.value;
                navigator.clipboard.writeText(textToCopy).then(function() {
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                    btn.classList.add('btn-success');
                    setTimeout(function() {
                        btn.innerHTML = originalText;
                        btn.classList.remove('btn-success');
                    }, 2000);
                });
            }
        });
    });
});
