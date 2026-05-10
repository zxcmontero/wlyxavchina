document.addEventListener('DOMContentLoaded', function () {
    var deleteForms = document.querySelectorAll('.js-confirm-delete');

    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var message = form.dataset.confirm || 'Вы уверены?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
});