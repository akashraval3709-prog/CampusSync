(function () {
    "use strict";

    // ---------- Element References ----------
    const overlay = document.getElementById("addStudentOverlay");
    const openBtn = document.getElementById("addStudentBtn");
    const closeBtn = document.getElementById("closeModalBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const form = document.getElementById("addStudentForm");
    const submitBtn = document.getElementById("submitStudentBtn");

    // Safety check: if any critical element is missing, log it clearly and stop.
    if (!overlay || !openBtn || !form || !submitBtn) {
        console.error("[student_form.js] Missing required element(s):", {
            overlay: !!overlay,
            openBtn: !!openBtn,
            closeBtn: !!closeBtn,
            cancelBtn: !!cancelBtn,
            form: !!form,
            submitBtn: !!submitBtn
        });
        return;
    }

    // NOTE: roll_number and enrollment_no are NOT collected here —
    // they are auto-generated server-side in /admin/api/students/add
    const fields = {
        full_name: document.getElementById("full_name"),
        email: document.getElementById("email"),
        mobile: document.getElementById("mobile"),
        dob: document.getElementById("dob"),
        course: document.getElementById("course"),
        semester: document.getElementById("semester"),
        division: document.getElementById("division"),
        academic_year: document.getElementById("academic_year"),
    };

    // ---------- Validation Rules ----------
    const validators = {
        full_name: (value) => {
            if (!value.trim()) return "Full name is required.";
            if (value.trim().length < 3) return "Name must be at least 3 characters.";
            if (!/^[A-Za-z ]+$/.test(value.trim())) return "Only alphabets and spaces allowed.";
            return "";
        },
        email: (value) => {
            if (!value.trim()) return "Email is required.";
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(value.trim())) return "Enter a valid email address.";
            return "";
        },
        mobile: (value) => {
            if (!value.trim()) return "Mobile number is required.";
            if (!/^\d{10}$/.test(value.trim())) return "Mobile number must be exactly 10 digits.";
            return "";
        },
        dob: (value) => {
            if (!value) return "";
            const selectedDate = new Date(value);
            const today = new Date();
            if (selectedDate >= today) return "Date of birth must be in the past.";
            return "";
        },
        course: (value) => {
            if (!value) return "Please select a course.";
            return "";
        },
        semester: (value) => {
            if (!value) return "Please select a semester.";
            return "";
        },
        division: (value) => {
            if (!value) return "Please select a division.";
            return "";
        },
        academic_year: (value) => {
            if (!value || !value.trim()) return "Academic Year is required.";
            if (value.trim().length > 20) return "Academic Year cannot exceed 20 characters.";
            return "";
        },
    };

    // ---------- Show error message under field ----------
    function showError(fieldName, message) {
        const errorEl = document.getElementById("err_" + fieldName);
        const inputEl = fields[fieldName];
        if (inputEl) {
            if (message) {
                inputEl.classList.add("invalid");
            } else {
                inputEl.classList.remove("invalid");
            }
        }
        if (errorEl) {
            errorEl.textContent = message || "";
        }
    }

    // ---------- Validate single field ----------
    function validateField(fieldName) {
        if (!fields[fieldName]) return true;
        const value = fields[fieldName].value;
        const errorMessage = validators[fieldName](value);
        showError(fieldName, errorMessage);
        return errorMessage === "";
    }

    // ---------- Validate entire form ----------
    function validateForm() {
        let isFormValid = true;
        Object.keys(fields).forEach((fieldName) => {
            const fieldIsValid = validateField(fieldName);
            if (!fieldIsValid) isFormValid = false;
        });
        return isFormValid;
    }

    // ---------- Check if all required fields are filled (for submit button state) ----------
    function isFormFilled() {
        return (
            fields.full_name.value.trim() !== "" &&
            fields.email.value.trim() !== "" &&
            fields.mobile.value.trim() !== "" &&
            fields.course.value !== "" &&
            fields.semester.value !== "" &&
            fields.division.value !== "" &&
            (!fields.academic_year || fields.academic_year.value.trim() !== "")
        );
    }

    // ---------- Enable/disable submit button dynamically ----------
    function updateSubmitState() {
        submitBtn.disabled = !isFormFilled();
    }

    // ---------- Attach blur (on-leave) validation to every field ----------
    Object.keys(fields).forEach((fieldName) => {
        if (!fields[fieldName]) return;

        fields[fieldName].addEventListener("blur", () => {
            validateField(fieldName);
        });

        fields[fieldName].addEventListener("input", () => {
            updateSubmitState();
        });
    });

    // Mobile field: allow digits only while typing
    if (fields.mobile) {
        fields.mobile.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "").slice(0, 10);
        });
    }

    // ---------- Calculate Academic Year Based on Selected Semester ----------
    function calculateAcademicYearForSemester(semValue, baseAcademicYear) {
        if (!semValue || !baseAcademicYear) return baseAcademicYear || "2026-27";
        const startYear = parseInt(baseAcademicYear.split("-")[0], 10);
        if (isNaN(startYear)) return baseAcademicYear;

        const sem = parseInt(semValue, 10);
        let offset = 0;
        if (sem === 1 || sem === 2) {
            offset = 0; // 1st Year BCA (Admitted in current academic year)
        } else if (sem === 3 || sem === 4) {
            offset = 1; // 2nd Year BCA (Admitted 1 year prior)
        } else if (sem === 5 || sem === 6) {
            offset = 2; // 3rd Year BCA (Admitted 2 years prior)
        }

        const calcStart = startYear - offset;
        const calcEnd = calcStart + 1;
        return `${calcStart}-${String(calcEnd).slice(-2)}`;
    }

    const initialAcademicYear = fields.academic_year
        ? (fields.academic_year.getAttribute("data-central-year") || fields.academic_year.defaultValue || "2026-27")
        : "2026-27";

    // Auto-update Academic Year when Semester changes
    if (fields.semester && fields.academic_year) {
        fields.semester.addEventListener("change", function () {
            const baseYear = fields.academic_year.getAttribute("data-central-year") || initialAcademicYear || "2026-27";
            if (this.value) {
                const calculatedYear = calculateAcademicYearForSemester(this.value, baseYear);
                fields.academic_year.value = calculatedYear;
            } else {
                fields.academic_year.value = baseYear;
            }
            validateField("academic_year");
            updateSubmitState();
        });
    }

    // ---------- Modal open/close ----------
    function openModal() {
        overlay.style.display = "flex";
        overlay.classList.remove("hidden");
        requestAnimationFrame(() => overlay.classList.add("show"));

        if (fields.semester && fields.academic_year && fields.semester.value) {
            const baseYear = fields.academic_year.getAttribute("data-central-year") || initialAcademicYear || "2026-27";
            fields.academic_year.value = calculateAcademicYearForSemester(fields.semester.value, baseYear);
        }
    }

    function closeModal() {
        overlay.classList.remove("show");
        setTimeout(() => {
            overlay.classList.add("hidden");
            overlay.style.display = "none";
        }, 200);
        resetForm();
    }

    function resetForm() {
        form.reset();
        const baseYear = (fields.academic_year && fields.academic_year.getAttribute("data-central-year")) || initialAcademicYear || "2026-27";
        if (fields.academic_year) {
            fields.academic_year.value = baseYear;
        }
        Object.keys(fields).forEach((fieldName) => showError(fieldName, ""));
        submitBtn.disabled = true;
    }

    // ---------- Event bindings (all null-safe) ----------
    openBtn.addEventListener("click", function (e) {
        e.preventDefault();
        openModal();
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", closeModal);
    }

    // NOTE: Outside-click-to-close is intentionally NOT implemented.
    // Modal must only close via the "Cancel" button or the "X" (close) button.

    // ---------- Form submit ----------
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (!validateForm()) return;

        submitBtn.disabled = true;
        submitBtn.textContent = "Adding...";

        const payload = {
            full_name: fields.full_name.value.trim(),
            email: fields.email.value.trim(),
            mobile: fields.mobile.value.trim(),
            dob: fields.dob.value || null,
            course: fields.course.value,
            semester: fields.semester.value,
            division: fields.division.value,
            academic_year: fields.academic_year ? fields.academic_year.value.trim() : "",
        };

        fetch("/admin/api/students/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ body }) => {
                if (body.success) {
                    showNotification({
                        type: "success",
                        title: "Student Added Successfully",
                        message: body.message || "Student record created successfully."
                    });
                    closeModal();
                    if (typeof loadStudents === "function") loadStudents();
                } else {
                    if (body.errors && typeof body.errors === 'object') {
                        Object.keys(body.errors).forEach((errKey) => {
                            showError(errKey, body.errors[errKey]);
                        });
                    }
                    showNotification({
                        type: "danger",
                        title: "Form Submission Failed",
                        message: body.message || "Failed to add student. Please correct the errors."
                    });
                }
            })
            .catch((error) => {
                console.error(error);
                showNotification({
                    type: "danger",
                    title: "Server Error",
                    message: "Something went wrong while communicating with the server. Please try again."
                });
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = "Add Student";
            });
    });
})();
