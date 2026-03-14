// Smart Donation Portal - Material UI JS

document.addEventListener('DOMContentLoaded', () => {
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
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = target; }, 120);
    });

    // Ripple effect centered on click
    const addRipple = (el) => {
        el.addEventListener('click', e => {
            const rect = el.getBoundingClientRect();
            const ripple = document.createElement('span');
            ripple.className = 'ripple-wave';
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
            el.appendChild(ripple);
            setTimeout(() => ripple.remove(), 500);
        });
    };
    document.querySelectorAll('.ripple, .md-btn').forEach(addRipple);

    // Quick amount buttons
    document.querySelectorAll('.quick-amt').forEach(btn => {
        btn.addEventListener('click', () => {
            const amountField = document.getElementById('amount-field');
            if (amountField) amountField.value = btn.dataset.amt;
            document.querySelectorAll('.quick-amt').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
});
