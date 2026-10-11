document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('url-input');
    if (input) {
        input.focus();
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && input) {
            input.value = '';
            input.focus();
        }
    });
});
