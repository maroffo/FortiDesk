// ABOUTME: Client-side utilities for FortiDesk (alerts, form validation, HTMX integration)
// ABOUTME: Re-initializes Bootstrap components after HTMX content swaps

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(function() {
                const alertInstance = new bootstrap.Alert(alert);
                alertInstance.close();
            }, 5000);
        }
    });

    // Form validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Re-initialize Bootstrap components after HTMX swaps new content into the DOM
document.addEventListener('htmx:afterSwap', function(event) {
    // Re-initialize tooltips on swapped content
    var tooltipElements = event.detail.target.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    // Re-initialize dismissible alerts on swapped content
    var alertElements = event.detail.target.querySelectorAll('.alert-dismissible');
    alertElements.forEach(function(el) {
        new bootstrap.Alert(el);
    });
});