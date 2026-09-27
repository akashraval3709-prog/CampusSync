/**
 * CampusSync – Custom Professional ERP Notification Modal JS
 * Reusable modal popup component for the entire Admin Panel.
 */

(function () {
    "use strict";

    // Helper to safely escape HTML
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * Categorizes error strings into standardized ERP error summary counts.
     */
    function categorizeErrors(errorsArray) {
        const categories = {
            "Duplicate Email": 0,
            "Duplicate Mobile": 0,
            "Invalid DOB": 0,
            "Invalid Semester": 0,
            "Missing Fields": 0,
            "Invalid Course": 0,
            "Invalid Email": 0,
            "Other Issues": 0
        };

        if (!Array.isArray(errorsArray)) return categories;

        errorsArray.forEach(errStr => {
            const str = String(errStr).toLowerCase();
            if (str.includes("duplicate email")) {
                categories["Duplicate Email"]++;
            } else if (str.includes("duplicate mobile") || str.includes("mobile number")) {
                categories["Duplicate Mobile"]++;
            } else if (str.includes("dob") || str.includes("date of birth")) {
                categories["Invalid DOB"]++;
            } else if (str.includes("semester")) {
                categories["Invalid Semester"]++;
            } else if (str.includes("missing") || str.includes("required")) {
                categories["Missing Fields"]++;
            } else if (str.includes("course")) {
                categories["Invalid Course"]++;
            } else if (str.includes("email")) {
                categories["Invalid Email"]++;
            } else {
                categories["Other Issues"]++;
            }
        });

        return categories;
    }

    /**
     * Main Global Notification API
     *
     * @param {Object} config
     * @param {string} config.type - 'success', 'danger'|'error', 'warning', 'info'
     * @param {string} [config.title] - Header title
     * @param {string} [config.subtitle] - Header subtitle
     * @param {string} [config.message] - Main message string
     * @param {number} [config.added] - Count of added records
     * @param {number} [config.skipped] - Count of skipped records
     * @param {Array<string>} [config.errors] - Array of error messages
     */
    function showNotification(config) {
        if (!config) config = {};

        // DOM elements
        const overlay = document.getElementById("erpNotificationOverlay");
        const card = document.getElementById("erpNotificationCard");
        const iconWrapper = document.getElementById("erpModalIconWrapper");
        const icon = document.getElementById("erpModalIcon");
        const titleEl = document.getElementById("erpModalTitle");
        const subtitleEl = document.getElementById("erpModalSubtitle");
        const messageEl = document.getElementById("erpModalMessage");
        const statsGrid = document.getElementById("erpModalStatsGrid");
        const statAdded = document.getElementById("erpStatAdded");
        const statSkipped = document.getElementById("erpStatSkipped");
        const statErrors = document.getElementById("erpStatErrors");
        const errorSummary = document.getElementById("erpModalErrorSummary");
        const summaryList = document.getElementById("erpSummaryList");
        const detailsContainer = document.getElementById("erpModalDetailsContainer");
        const detailsToggle = document.getElementById("erpModalDetailsToggle");
        const detailsContent = document.getElementById("erpModalDetailsContent");
        const detailsList = document.getElementById("erpDetailsList");
        const detailsChevron = document.getElementById("erpDetailsChevron");
        const okBtn = document.getElementById("erpModalOkBtn");
        const closeBtn = document.getElementById("erpModalCloseBtn");

        if (!overlay || !card) {
            console.error("[notification_modal.js] Modal elements missing in DOM.");
            return;
        }

        // Determine type logic if added/skipped are provided
        let type = (config.type || "info").toLowerCase();
        if (type === "error") type = "danger";

        const added = config.added !== undefined ? Number(config.added) : null;
        const skipped = config.skipped !== undefined ? Number(config.skipped) : null;
        const errors = Array.isArray(config.errors) ? config.errors : [];

        // Auto-configure smart title, theme & message for import responses
        if (added !== null && skipped !== null) {
            if (added > 0 && skipped === 0 && errors.length === 0) {
                type = "success";
                if (!config.title) config.title = "Student Import Completed";
                if (!config.message) config.message = "All students imported successfully.";
            } else if (added > 0 && (skipped > 0 || errors.length > 0)) {
                type = "warning";
                if (!config.title) config.title = "Import Completed with Warnings";
                if (!config.message) config.message = "Students imported successfully but some records were skipped.";
            } else if (added === 0) {
                type = "danger";
                if (!config.title) config.title = "Import Failed";
                if (!config.message) config.message = "No valid students could be imported.";
            }
        }

        // Icon & theme styling
        const themeMap = {
            success: { icon: "bi-check-circle-fill", class: "success" },
            danger: { icon: "bi-x-circle-fill", class: "danger" },
            warning: { icon: "bi-exclamation-triangle-fill", class: "warning" },
            info: { icon: "bi-info-circle-fill", class: "info" }
        };
        const activeTheme = themeMap[type] || themeMap.info;

        iconWrapper.className = `erp-modal-icon-wrapper ${activeTheme.class}`;
        icon.className = `bi ${activeTheme.icon}`;

        titleEl.textContent = config.title || (type === "success" ? "Success" : type === "danger" ? "Error" : type === "warning" ? "Warning" : "Information");
        if (config.isHtml || (config.message && /<[a-z][\s\S]*>/i.test(config.message))) {
            messageEl.innerHTML = config.message;
        } else {
            messageEl.innerHTML = config.message ? escapeHtml(config.message).replace(/\n/g, "<br>") : "";
        }

        // Statistics Cards
        if (added !== null || skipped !== null || errors.length > 0) {
            statsGrid.style.display = "grid";
            statAdded.textContent = added !== null ? added : 0;
            statSkipped.textContent = skipped !== null ? skipped : 0;
            statErrors.textContent = errors.length;
        } else {
            statsGrid.style.display = "none";
        }

        // Categorized Error Summary
        if (errors.length > 0) {
            errorSummary.style.display = "block";
            summaryList.innerHTML = "";
            const categoryCounts = categorizeErrors(errors);
            let hasCategories = false;

            Object.keys(categoryCounts).forEach(cat => {
                const count = categoryCounts[cat];
                if (count > 0) {
                    hasCategories = true;
                    const item = document.createElement("div");
                    item.className = "erp-summary-item";
                    item.innerHTML = `<span>${escapeHtml(cat)}</span><span class="erp-summary-badge">${count}</span>`;
                    summaryList.appendChild(item);
                }
            });

            if (!hasCategories) {
                errorSummary.style.display = "none";
            }
        } else {
            errorSummary.style.display = "none";
        }

        // Row Details Collapsible
        if (errors.length > 0) {
            detailsContainer.style.display = "block";
            detailsContent.style.display = "none"; // collapsed by default
            if (detailsChevron) detailsChevron.className = "bi bi-chevron-down ms-1";
            detailsList.innerHTML = "";

            errors.forEach(err => {
                const div = document.createElement("div");
                div.className = "erp-details-item";
                div.textContent = err;
                detailsList.appendChild(div);
            });
        } else {
            detailsContainer.style.display = "none";
        }

        // Setup Details Toggle Button
        detailsToggle.onclick = function (e) {
            e.preventDefault();
            const isHidden = detailsContent.style.display === "none";
            if (isHidden) {
                detailsContent.style.display = "block";
                if (detailsChevron) detailsChevron.className = "bi bi-chevron-up ms-1";
            } else {
                detailsContent.style.display = "none";
                if (detailsChevron) detailsChevron.className = "bi bi-chevron-down ms-1";
            }
        };

        // Open Modal Animation
        document.body.classList.add("erp-modal-open");
        overlay.style.display = "flex";
        overlay.classList.remove("closing");

        // Reflow to ensure animation triggers
        void overlay.offsetWidth;
        overlay.classList.add("active");

        // Close Modal Handler function
        function closeModal() {
            overlay.classList.remove("active");
            overlay.classList.add("closing");

            setTimeout(() => {
                overlay.style.display = "none";
                overlay.classList.remove("closing");
                document.body.classList.remove("erp-modal-open");
            }, 180);
        }

        // Bind OK and Close (X) buttons
        okBtn.onclick = function () { closeModal(); };
        if (closeBtn) closeBtn.onclick = function () { closeModal(); };

        // Prevent closing on outside click or ESC key (explicit requirement)
        overlay.onclick = function (e) {
            if (e.target === overlay) {
                e.stopPropagation();
            }
        };
    }

    // Expose globally
    window.showNotification = showNotification;
    window.showFlash = function (type, title, message) {
        showNotification({ type: type, title: title, message: message });
    };
})();
