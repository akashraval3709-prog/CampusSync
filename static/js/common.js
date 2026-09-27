// CampusSync – common.js (Ultra-Smooth Mobile & Responsive Interactions)

(function () {
    'use strict';

    function initSidebarNavigation() {
        const btn       = document.getElementById('sidebarCollapse');
        const sidebar   = document.getElementById('sidebar');
        let   backdrop  = document.getElementById('sidebarBackdrop');

        if (!sidebar) return;

        // Ensure backdrop exists in the DOM
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'sidebarBackdrop';
            backdrop.className = 'sidebar-backdrop';
            document.body.appendChild(backdrop);
        }

        // Restore collapsed state on desktop viewports (>= 992px)
        if (window.innerWidth >= 992 && localStorage.getItem('sidebar-collapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }

        // Helper to open mobile sidebar
        function openSidebar() {
            sidebar.classList.add('active');
            backdrop.classList.add('is-visible');
            document.body.classList.add('sidebar-open');
            if (btn) btn.setAttribute('aria-expanded', 'true');
        }

        // Helper to close mobile sidebar
        function closeSidebar() {
            sidebar.classList.remove('active');
            backdrop.classList.remove('is-visible');
            document.body.classList.remove('sidebar-open');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        }

        // Helper to toggle sidebar state
        function toggleSidebar(e) {
            if (e) {
                if (e._campusSidebarHandled) return;
                e._campusSidebarHandled = true;
                if (e.preventDefault) e.preventDefault();
                if (e.stopPropagation) e.stopPropagation();
            }
            if (window.innerWidth < 992) {
                if (sidebar.classList.contains('active')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            } else {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
            }
        }

        // Bind hamburger toggle button (only if not already bound via onclick attribute)
        if (btn) {
            btn.setAttribute('aria-expanded', sidebar.classList.contains('active') ? 'true' : 'false');
            if (!btn.getAttribute('onclick')) {
                btn.removeEventListener('click', btn._sidebarClickHandler);
                btn._sidebarClickHandler = toggleSidebar;
                btn.addEventListener('click', toggleSidebar);
            }
        }

        // Bind mobile close button inside sidebar header (#sidebarCloseBtn)
        const closeBtn = document.getElementById('sidebarCloseBtn');
        if (closeBtn) {
            closeBtn.removeEventListener('click', closeBtn._sidebarCloseHandler);
            closeBtn._sidebarCloseHandler = function (e) {
                e.preventDefault();
                closeSidebar();
            };
            closeBtn.addEventListener('click', closeBtn._sidebarCloseHandler);
        }

        // Backdrop tap to dismiss
        backdrop.removeEventListener('click', backdrop._sidebarBackdropHandler);
        backdrop._sidebarBackdropHandler = function () {
            closeSidebar();
        };
        backdrop.addEventListener('click', backdrop._sidebarBackdropHandler);

        // Auto-close on link navigation on mobile
        sidebar.querySelectorAll('ul.components li a:not([data-bs-toggle="collapse"])').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth < 992) {
                    closeSidebar();
                }
            });
        });

        // Touch Swipe-to-Close Gesture on Sidebar (Butter-smooth touch)
        let touchStartX = 0;
        let touchStartY = 0;
        sidebar.addEventListener('touchstart', function (e) {
            if (e.touches && e.touches.length > 0) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
            }
        }, { passive: true });

        sidebar.addEventListener('touchend', function (e) {
            if (e.changedTouches && e.changedTouches.length > 0) {
                const diffX = touchStartX - e.changedTouches[0].clientX;
                const diffY = Math.abs(touchStartY - e.changedTouches[0].clientY);
                // Swiped left by > 50px horizontally with minimal vertical drag
                if (diffX > 50 && diffY < 80 && window.innerWidth < 992) {
                    closeSidebar();
                }
            }
        }, { passive: true });

        // Close on ESC key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active') && window.innerWidth < 992) {
                closeSidebar();
            }
        });

        // Highlight active link
        const currentPath = window.location.pathname;
        sidebar.querySelectorAll('ul.components li a').forEach(function (link) {
            if (link.getAttribute('href') === currentPath) {
                link.closest('li').classList.add('active');
            }
        });

        // Expose helpers globally
        window.openCampusSidebar = openSidebar;
        window.closeCampusSidebar = closeSidebar;
        window.toggleCampusSidebar = toggleSidebar;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebarNavigation);
    } else {
        initSidebarNavigation();
    }

    // Re-check on window resize across breakpoint
    window.addEventListener('resize', function () {
        const sidebar = document.getElementById('sidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (window.innerWidth >= 992 && sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            if (backdrop) backdrop.classList.remove('is-visible');
            document.body.classList.remove('sidebar-open');
        }
    });
})();

// Helper to escape HTML characters for safety in title/messages
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * CampusSync Reusable Flash Messages System
 * Displays animated Bootstrap 5 alert cards at the top of the HTML page.
 *
 * @param {string} type - 'success', 'danger' (or 'error'), 'warning', 'info'
 * @param {string} title - Main header title of the alert
 * @param {string|HTMLElement} message - Text or HTML message content
 * @param {number} [autoHideMs] - Optional auto-hide timeout in ms (default based on type)
 */
function showFlash(type, title, message, autoHideMs) {
    let alertType = (type || 'info').toLowerCase();
    if (alertType === 'error') alertType = 'danger';

    const iconMap = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };
    const iconClass = iconMap[alertType] || 'bi-info-circle-fill';

    if (autoHideMs === undefined || autoHideMs === null) {
        const defaultDurations = {
            success: 5000,
            danger: 8000,
            warning: 6000,
            info: 5000
        };
        autoHideMs = defaultDurations[alertType] || 5000;
    }

    let container = document.getElementById('flashContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'flashContainer';
        container.className = 'flash-container';

        const contentEl = document.getElementById('content') || document.querySelector('.content-body') || document.body;
        const pageHeader = contentEl.querySelector('.page-header');
        if (pageHeader) {
            contentEl.insertBefore(container, pageHeader);
        } else if (contentEl.firstChild) {
            contentEl.insertBefore(container, contentEl.firstChild);
        } else {
            contentEl.appendChild(container);
        }
    }

    const flashCard = document.createElement('div');
    flashCard.className = `flash-card alert alert-${alertType} flash-enter`;

    let messageHtml = '';
    if (typeof message === 'string') {
        if (!/<[a-z][\s\S]*>/i.test(message)) {
            messageHtml = message.replace(/\n/g, '<br>');
        } else {
            messageHtml = message;
        }
    } else if (message) {
        messageHtml = message.outerHTML || String(message);
    }

    flashCard.innerHTML = `
        <i class="bi ${iconClass} flash-icon"></i>
        <div class="flash-content">
            ${title ? `<div class="flash-title">${escapeHtml(title)}</div>` : ''}
            <div class="flash-message">${messageHtml}</div>
        </div>
        <button type="button" class="flash-close" aria-label="Close">
            <i class="bi bi-x-lg"></i>
        </button>
    `;

    const closeBtn = flashCard.querySelector('.flash-close');
    let dismissTimer = null;

    function dismissFlash() {
        if (dismissTimer) clearTimeout(dismissTimer);
        flashCard.classList.remove('flash-enter');
        flashCard.classList.add('flash-exit');
        flashCard.addEventListener('animationend', () => {
            if (flashCard.parentNode) {
                flashCard.parentNode.removeChild(flashCard);
            }
        });
    }

    closeBtn.addEventListener('click', dismissFlash);

    if (autoHideMs > 0) {
        dismissTimer = setTimeout(dismissFlash, autoHideMs);
    }

    container.appendChild(flashCard);
}

/**
 * Smart helper to display Excel Import Flash Messages
 * Standardized for response objects containing { added, skipped, errors, message }
 */
function showImportFlash(data) {
    if (!data) return;

    const added = data.added !== undefined ? data.added : 0;
    const skipped = data.skipped !== undefined ? data.skipped : 0;
    const errors = Array.isArray(data.errors) ? data.errors : [];

    let type = 'success';
    let title = 'Student Import Completed';

    if (added === 0) {
        type = 'danger';
        title = 'Student Import Failed';
    } else if (skipped > 0 || errors.length > 0) {
        type = 'warning';
        title = 'Student Import Completed';
    } else {
        type = 'success';
        title = 'Student Import Completed';
    }

    let html = `<div><strong>Added :</strong> ${added}</div>`;
    html += `<div><strong>Skipped :</strong> ${skipped}</div>`;

    if (errors.length > 0) {
        html += `<div class="flash-details">`;
        html += `<strong>Details :</strong>`;
        html += `<ul class="mb-0">`;
        const displayErrors = errors.slice(0, 5);
        displayErrors.forEach(err => {
            html += `<li>${escapeHtml(err)}</li>`;
        });
        if (errors.length > 5) {
            html += `<li><em>...and ${errors.length - 5} more issues.</em></li>`;
        }
        html += `</ul></div>`;
    } else if (data.message && added === 0) {
        html += `<div class="mt-1">${escapeHtml(data.message)}</div>`;
    }

    showFlash(type, title, html);
}

// Expose functions globally
window.showFlash = showFlash;
window.showImportFlash = showImportFlash;

