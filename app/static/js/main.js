// Smart Donation Portal – Main JS

// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert?.close();
    }, 5000);
});

// File upload preview label
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function () {
        const label = this.nextElementSibling;
        if (label && label.tagName === 'LABEL') {
            label.textContent = this.files[0]?.name || 'Choose file';
        }
    });
});

// Confirm on danger actions (handled inline via onclick, but here as fallback)
document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
        if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
});

// Progress bar animation on load
window.addEventListener('load', () => {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = target; }, 100);
    });
});
