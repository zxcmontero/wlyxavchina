document.addEventListener('DOMContentLoaded', function () {
    var deleteForms = document.querySelectorAll('.js-confirm-delete');
    var mainContent = document.querySelector('#main-content');
    var navToggle = document.querySelector('[data-nav-toggle]');
    var navMenu = document.querySelector('[data-nav-menu]');
    var navOverlay = document.querySelector('[data-nav-overlay]');

    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var message = form.dataset.confirm || 'Вы уверены?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    if (navToggle && navMenu) {
        var isMobileMenuMode = function () {
            return window.innerWidth <= 768;
        };

        var getFirstMenuLink = function () {
            return navMenu.querySelector('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])');
        };

        var syncMenuAccessibility = function () {
            var isMobile = isMobileMenuMode();
            var isOpen = navMenu.classList.contains('is-open');

            navMenu.setAttribute('aria-hidden', isMobile && !isOpen ? 'true' : 'false');
            navToggle.setAttribute('aria-label', isOpen ? 'Закрыть меню' : 'Открыть меню');

            if (navOverlay) {
                navOverlay.setAttribute('aria-hidden', isMobile && isOpen ? 'false' : 'true');
            }
        };

        var setMenuState = function (isOpen, options) {
            var isMobile = isMobileMenuMode();
            var shouldOpen = Boolean(isMobile && isOpen);
            var shouldMoveFocus = options && options.moveFocus;
            var shouldReturnFocus = options && options.returnFocus;

            navMenu.classList.toggle('is-open', shouldOpen);
            navToggle.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
            document.body.classList.toggle('has-open-menu', shouldOpen);
            syncMenuAccessibility();

            if (shouldOpen && shouldMoveFocus) {
                var firstMenuLink = getFirstMenuLink();
                if (firstMenuLink) {
                    firstMenuLink.focus();
                }
            }

            if (!shouldOpen && shouldReturnFocus) {
                navToggle.focus();

                if (document.activeElement !== navToggle && mainContent) {
                    mainContent.focus();
                }
            }
        };

        var closeMenu = function () {
            setMenuState(false);
        };

        navToggle.addEventListener('click', function () {
            var willOpen = !navMenu.classList.contains('is-open');
            setMenuState(willOpen, { moveFocus: willOpen, returnFocus: !willOpen });
        });

        navMenu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                if (navMenu.classList.contains('is-open')) {
                    closeMenu();
                }
            });
        });

        if (navOverlay) {
            navOverlay.addEventListener('click', function () {
                setMenuState(false, { returnFocus: true });
            });
        }

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && navMenu.classList.contains('is-open')) {
                setMenuState(false, { returnFocus: true });
            }
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                closeMenu();
            }
        });

        syncMenuAccessibility();
    }
});