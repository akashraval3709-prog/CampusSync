/**
 * CampusSync ERP - Faculty Management JavaScript
 * File: static/js/admin-faculty.js
 * 
 * 100% Database-Driven Script for Faculty Directory, Real-Time Filters,
 * Search, Add/Edit Modal with Subject & Division Assignment, View Modal,
 * and Delete Actions.
 */

// ── 1. Global State Variables (Loaded dynamically from MySQL) ──────
let MASTER_SUBJECTS = [];
let facultyList = [];
let statCounts = {
    total: 0,
    active: 0,
    inactive: 0,
    subjects: 0
};

// Current Modal & Interaction State
let currentEditingId = null;
let currentDeletingId = null;
let selectedPhotoFile = null;
let currentPhotoBase64 = null;
let activeSubjectSelections = []; // array of { code, name, semester, divisions: ['A', ...] }
let activeSemesterFilter = 'all';
let searchDebounceTimer = null;

// ── 2. DOM Initialization ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();
    loadFacultyData();
});

// ── 3. Event Listeners ─────────────────────────────────────────────
function initializeEventListeners() {
    // Top-right Add Faculty button
    const addBtn = document.getElementById('openAddFacultyBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function () {
            openAddFacultyModal();
        });
    }

    // Filter controls: Live search with debounce
    const searchInput = document.getElementById('facultySearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                loadFacultyData();
            }, 300);
        });
    }

    // Status filter
    const statusFilter = document.getElementById('facultyStatusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function () {
            loadFacultyData();
        });
    }

    // Department filter
    const deptFilter = document.getElementById('facultyDeptFilter');
    if (deptFilter) {
        deptFilter.addEventListener('change', function () {
            loadFacultyData();
        });
    }

    // Reset filter button
    const resetFilterBtn = document.getElementById('resetFilterBtn');
    if (resetFilterBtn) {
        resetFilterBtn.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            if (statusFilter) statusFilter.value = 'all';
            if (deptFilter) deptFilter.value = 'all';
            loadFacultyData();
        });
    }

    // Select all checkboxes
    const checkAll = document.getElementById('selectAllFaculty');
    if (checkAll) {
        checkAll.addEventListener('change', function () {
            const checkboxes = document.querySelectorAll('.faculty-row-checkbox');
            checkboxes.forEach(cb => cb.checked = checkAll.checked);
        });
    }

    // Photo Upload & Preview
    const photoInput = document.getElementById('facultyPhotoInput');
    if (photoInput) {
        photoInput.addEventListener('change', function (e) {
            handlePhotoUpload(e);
        });
    }

    const removePhotoBtn = document.getElementById('btnRemovePhoto');
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener('click', function () {
            resetPhotoPreview();
        });
    }

    // Subject Search inside Modal
    const modalSubjectSearch = document.getElementById('modalSubjectSearch');
    if (modalSubjectSearch) {
        modalSubjectSearch.addEventListener('input', function () {
            renderSubjectAssignmentList();
        });
    }

    // Modal Semester Filter Buttons
    const semPills = document.querySelectorAll('.sem-filter-btn');
    semPills.forEach(btn => {
        btn.addEventListener('click', function () {
            semPills.forEach(b => {
                b.classList.remove('btn-primary');
                b.classList.add('btn-outline-secondary');
            });
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-primary');
            activeSemesterFilter = this.getAttribute('data-sem') || 'all';
            renderSubjectAssignmentList();
        });
    });

    // Faculty Form Submission
    const facultyForm = document.getElementById('facultyForm');
    if (facultyForm) {
        facultyForm.addEventListener('submit', function (e) {
            e.preventDefault();
            handleFacultyFormSubmit();
        });
    }

    // Delete Confirmation Button
    const confirmDeleteBtn = document.getElementById('confirmDeleteFacultyBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            executeDeleteFaculty();
        });
    }
}

// ── 4. Load Live Data from Flask Backend ───────────────────────────
async function loadFacultyData() {
    const search = document.getElementById('facultySearchInput')?.value.trim() || '';
    const status = document.getElementById('facultyStatusFilter')?.value || 'all';
    const dept = document.getElementById('facultyDeptFilter')?.value || 'all';

    const url = new URL('/admin/faculty/data', window.location.origin);
    if (search) url.searchParams.set('search', search);
    if (status !== 'all') url.searchParams.set('status', status);
    if (dept !== 'all') url.searchParams.set('dept', dept);

    try {
        const response = await fetch(url.toString(), {
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            facultyList = data.faculty || [];
            statCounts = data.stats || { total: 0, active: 0, inactive: 0, subjects: 0 };
            if (data.subjects) {
                MASTER_SUBJECTS = data.subjects;
            }

            updateStatDisplay();
            renderFacultyTable();
            renderSubjectAssignmentList();
        } else {
            displayToast('danger', 'Error', data.message || 'Failed to load faculty data.');
        }
    } catch (err) {
        console.error('Error fetching faculty data:', err);
        displayToast('danger', 'Connection Error', 'Could not load faculty data from server.');
    }
}

// ── 5. Statistics Cards Display ────────────────────────────────────
function updateStatDisplay() {
    const elTotal = document.getElementById('statTotalFaculty');
    const elActive = document.getElementById('statActiveFaculty');
    const elInactive = document.getElementById('statInactiveFaculty');
    const elSubjects = document.getElementById('statSubjectsAssigned');

    if (elTotal) elTotal.textContent = statCounts.total;
    if (elActive) elActive.textContent = statCounts.active;
    if (elInactive) elInactive.textContent = statCounts.inactive;
    if (elSubjects) elSubjects.textContent = statCounts.subjects;
}

// ── 6. Render Faculty Table with Database Records ───────────────────
function renderFacultyTable() {
    const tbody = document.getElementById('facultyTableBody');
    const emptyState = document.getElementById('facultyEmptyState');
    const tableContainer = document.getElementById('facultyTableContainer');
    const countBadge = document.getElementById('facultyCountBadge');
    if (!tbody) return;

    if (countBadge) {
        countBadge.textContent = `${facultyList.length} Faculty Member${facultyList.length === 1 ? '' : 's'}`;
    }

    tbody.innerHTML = '';

    if (facultyList.length === 0) {
        if (tableContainer) tableContainer.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (tableContainer) tableContainer.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';

    facultyList.forEach(faculty => {
        const tr = document.createElement('tr');

        // Initials avatar fallback
        const initials = faculty.fullName ? faculty.fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'FA';
        const avatarHtml = faculty.photo
            ? `<img src="${faculty.photo}" alt="${escapeHtml(faculty.fullName)}" class="faculty-avatar" style="object-fit: cover;">`
            : `<div class="faculty-avatar">${initials}</div>`;

        // Assigned subjects tags
        const subCount = faculty.assignedSubjects ? faculty.assignedSubjects.length : 0;
        let subjectsHtml = '';
        if (subCount > 0) {
            const badgesHtml = faculty.assignedSubjects.slice(0, 2).map(s =>
                `<span class="subject-mini-tag" title="${escapeHtml(s.name)} (Sem ${s.semester} - Div ${s.divisions.join(', ')})">${escapeHtml(s.name)} <small class="text-muted">(${s.divisions.join(',')})</small></span>`
            ).join(' ');
            const moreBadge = subCount > 2 ? `<span class="badge bg-light text-muted border">+${subCount - 2} more</span>` : '';

            subjectsHtml = `
                <div>
                    <span class="subject-summary-badge mb-1">
                        <i class="bi bi-journal-check text-primary"></i> ${subCount} Subject${subCount === 1 ? '' : 's'}
                    </span>
                    <div class="d-flex flex-wrap gap-1 mt-1">
                        ${badgesHtml} ${moreBadge}
                    </div>
                </div>
            `;
        } else {
            subjectsHtml = `<span class="text-muted small fst-italic">None Assigned</span>`;
        }

        // Status pill
        const isAct = faculty.status === 'Active';
        const statusHtml = `
            <span class="status-pill ${isAct ? 'active' : 'inactive'}">
                <span class="status-dot"></span>
                ${faculty.status}
            </span>
        `;

        tr.innerHTML = `
            <td class="ps-3" style="width: 40px;">
                <input type="checkbox" class="form-check-input faculty-row-checkbox" value="${faculty.id}">
            </td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    ${avatarHtml}
                    <div>
                        <div class="faculty-name">${escapeHtml(faculty.fullName)}</div>
                        <span class="faculty-code-badge">${escapeHtml(faculty.code)}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="fw-semibold text-secondary font-monospace">${escapeHtml(faculty.code)}</span>
            </td>
            <td>
                <a href="mailto:${escapeHtml(faculty.email)}" class="text-decoration-none text-dark small">
                    <i class="bi bi-envelope text-muted me-1"></i>${escapeHtml(faculty.email)}
                </a>
            </td>
            <td>
                <span class="small text-secondary font-monospace">
                    <i class="bi bi-telephone text-muted me-1"></i>${escapeHtml(faculty.mobile)}
                </span>
            </td>
            <td>
                <span class="badge bg-light text-dark border">${escapeHtml(faculty.qualification || '-')}</span>
            </td>
            <td>
                <span class="small fw-semibold text-dark">${escapeHtml(faculty.designation || '-')}</span>
            </td>
            <td>
                <span class="dept-badge">${escapeHtml(faculty.department || '-')}</span>
            </td>
            <td>
                ${subjectsHtml}
            </td>
            <td>
                ${statusHtml}
            </td>
            <td class="pe-3 text-end">
                <div class="action-btn-group d-inline-flex gap-1">
                    <button type="button" class="btn btn-outline-primary btn-view" title="View Profile" onclick="openViewFacultyModal(${faculty.id})">
                        <i class="bi bi-eye-fill"></i>
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-edit" title="Edit Faculty" onclick="openEditFacultyModal(${faculty.id})">
                        <i class="bi bi-pencil-fill"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger btn-delete" title="Delete Faculty" onclick="openDeleteFacultyModal(${faculty.id})">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

// ── 7. Add / Edit Faculty Modal Logic ───────────────────────────────
function openAddFacultyModal() {
    currentEditingId = null;
    selectedPhotoFile = null;
    currentPhotoBase64 = null;

    const form = document.getElementById('facultyForm');
    if (form) form.reset();

    document.getElementById('facultyModalTitle').innerHTML = '<i class="bi bi-person-plus-fill me-2 text-primary"></i>Add New Faculty';
    document.getElementById('saveFacultyBtn').innerHTML = '<i class="bi bi-check-lg me-1"></i>Save Faculty';

    // Suggest next available faculty code
    let nextNum = 1;
    if (facultyList && facultyList.length > 0) {
        const numbers = facultyList
            .map(f => parseInt((f.code || '').replace(/\D/g, '')))
            .filter(n => !isNaN(n));
        if (numbers.length > 0) {
            nextNum = Math.max(...numbers) + 1;
        }
    }
    const nextCode = `FAC${String(nextNum).padStart(3, '0')}`;
    const codeInput = document.getElementById('faculty_code');
    if (codeInput) codeInput.value = nextCode;

    // Reset photo & subjects
    resetPhotoPreview();
    activeSubjectSelections = [];
    activeSemesterFilter = 'all';
    renderSubjectAssignmentList();
    updateSelectedSubjectsSummary();

    const modalEl = document.getElementById('facultyFormModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
}

async function openEditFacultyModal(id) {
    currentEditingId = id;
    selectedPhotoFile = null;
    currentPhotoBase64 = null;

    document.getElementById('facultyModalTitle').innerHTML = '<i class="bi bi-pencil-square me-2 text-primary"></i>Edit Faculty';
    document.getElementById('saveFacultyBtn').innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Update Faculty';

    try {
        const res = await fetch(`/admin/faculty/${id}`);
        const data = await res.json();
        if (!data.success || !data.faculty) {
            displayToast('danger', 'Error', 'Could not load faculty details.');
            return;
        }

        const faculty = data.faculty;

        // Populate fields
        document.getElementById('full_name').value = faculty.fullName || '';
        document.getElementById('faculty_code').value = faculty.code || '';
        document.getElementById('email').value = faculty.email || '';
        document.getElementById('mobile').value = faculty.mobile || '';
        document.getElementById('gender').value = faculty.gender || 'Male';
        document.getElementById('dob').value = faculty.dob || '';

        document.getElementById('qualification').value = faculty.qualification || '';
        document.getElementById('designation').value = faculty.designation || 'Assistant Professor';
        document.getElementById('department').value = faculty.department || 'BCA';
        document.getElementById('joining_date').value = faculty.joiningDate || '';
        document.getElementById('status').value = faculty.status || 'Active';

        document.getElementById('address').value = faculty.address || '';
        document.getElementById('city').value = faculty.city || '';
        document.getElementById('state').value = faculty.state || '';
        document.getElementById('pincode').value = faculty.pincode || '';

        // Photo Preview
        const previewImg = document.getElementById('photoPreviewImage');
        const placeholder = document.getElementById('photoPreviewPlaceholder');
        const removeBtn = document.getElementById('btnRemovePhoto');

        if (faculty.photo) {
            if (previewImg) { previewImg.src = faculty.photo; previewImg.style.display = 'block'; }
            if (placeholder) placeholder.style.display = 'none';
            if (removeBtn) removeBtn.style.display = 'flex';
        } else {
            resetPhotoPreview();
        }

        // Assigned subjects
        activeSubjectSelections = JSON.parse(JSON.stringify(faculty.assignedSubjects || []));
        activeSemesterFilter = 'all';
        renderSubjectAssignmentList();
        updateSelectedSubjectsSummary();

        const modalEl = document.getElementById('facultyFormModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        }
    } catch (err) {
        console.error('Error fetching single faculty:', err);
        displayToast('danger', 'Error', 'Failed to retrieve faculty from server.');
    }
}

// ── 8. Profile Photo Preview Handling ───────────────────────────────
function handlePhotoUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (PNG, JPG, JPEG, WEBP).');
        return;
    }

    selectedPhotoFile = file;

    const reader = new FileReader();
    reader.onload = function (event) {
        currentPhotoBase64 = event.target.result;
        const previewImg = document.getElementById('photoPreviewImage');
        const placeholder = document.getElementById('photoPreviewPlaceholder');
        const removeBtn = document.getElementById('btnRemovePhoto');

        if (previewImg) {
            previewImg.src = currentPhotoBase64;
            previewImg.style.display = 'block';
        }
        if (placeholder) placeholder.style.display = 'none';
        if (removeBtn) removeBtn.style.display = 'flex';
    };
    reader.readAsDataURL(file);
}

function resetPhotoPreview() {
    selectedPhotoFile = null;
    currentPhotoBase64 = null;
    const photoInput = document.getElementById('facultyPhotoInput');
    if (photoInput) photoInput.value = '';

    const previewImg = document.getElementById('photoPreviewImage');
    const placeholder = document.getElementById('photoPreviewPlaceholder');
    const removeBtn = document.getElementById('btnRemovePhoto');

    if (previewImg) {
        previewImg.src = '';
        previewImg.style.display = 'none';
    }
    if (placeholder) placeholder.style.display = 'flex';
    if (removeBtn) removeBtn.style.display = 'none';
}

// ── 9. Subject Assignment UI & Dynamic Filtering ───────────────────
function renderSubjectAssignmentList() {
    const container = document.getElementById('modalSubjectList');
    if (!container) return;

    const searchTerm = (document.getElementById('modalSubjectSearch')?.value || '').toLowerCase().trim();

    // Filter subjects fetched from database
    const filteredSubjects = MASTER_SUBJECTS.filter(sub => {
        const matchSearch = !searchTerm ||
            (sub.name || '').toLowerCase().includes(searchTerm) ||
            (sub.code || '').toLowerCase().includes(searchTerm);

        const matchSem = (activeSemesterFilter === 'all') || (sub.semester === parseInt(activeSemesterFilter));

        return matchSearch && matchSem;
    });

    container.innerHTML = '';

    if (filteredSubjects.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-journal-x fs-3 d-block mb-1"></i>
                <span class="small">No subjects found in database matching criteria.</span>
            </div>
        `;
        return;
    }

    // Group subjects semester-wise
    const grouped = {};
    filteredSubjects.forEach(sub => {
        if (!grouped[sub.semester]) grouped[sub.semester] = [];
        grouped[sub.semester].push(sub);
    });

    Object.keys(grouped).sort((a, b) => a - b).forEach(sem => {
        const semHeader = document.createElement('div');
        semHeader.className = 'subject-group-header d-flex justify-content-between align-items-center';
        semHeader.innerHTML = `
            <span><i class="bi bi-mortarboard me-1"></i>Semester ${sem}</span>
            <span class="badge bg-secondary" style="font-size: 0.65rem;">${grouped[sem].length} Subjects</span>
        `;
        container.appendChild(semHeader);

        grouped[sem].forEach(sub => {
            const isSelected = activeSubjectSelections.some(s => s.code === sub.code);
            const selectedItem = activeSubjectSelections.find(s => s.code === sub.code);
            const currentDivisions = selectedItem ? selectedItem.divisions : ['A'];

            const itemCard = document.createElement('div');
            itemCard.className = `subject-item-card d-flex flex-wrap align-items-center justify-content-between gap-2 ${isSelected ? 'is-selected' : ''}`;
            itemCard.id = `subItemCard_${sub.code}`;

            const renderDivisionChip = (divLetter) => {
                const conflict = getDivisionConflict(sub.code, divLetter);
                const isTaken = conflict !== null;
                const isSel = currentDivisions.includes(divLetter);
                const titleText = isTaken
                    ? `Assigned to ${escapeHtml(conflict.faculty_name)} (${escapeHtml(conflict.faculty_code)})`
                    : `Assign Division ${divLetter}`;

                return `
                    <span class="division-chip ${isTaken ? 'taken' : ''} ${isSel ? 'selected' : ''}" 
                          title="${titleText}"
                          onclick="toggleSubjectDivision('${sub.code}', '${divLetter}')">
                        ${divLetter}${isTaken ? ' <i class="bi bi-lock-fill" style="font-size: 0.65rem;"></i>' : ''}
                    </span>
                `;
            };

            itemCard.innerHTML = `
                <div class="form-check m-0 d-flex align-items-center gap-2">
                    <input class="form-check-input subject-checkbox" type="checkbox" 
                           id="chk_${sub.code}" value="${sub.code}" 
                           ${isSelected ? 'checked' : ''} 
                           onchange="toggleSubjectSelection('${sub.code}', ${sub.semester})">
                    <label class="form-check-label mb-0" for="chk_${sub.code}" style="cursor: pointer;">
                        <span class="fw-bold text-dark small">${escapeHtml(sub.code)}</span> — 
                        <span class="small text-secondary">${escapeHtml(sub.name)}</span>
                    </label>
                </div>

                <div class="division-pill-group" id="divGroup_${sub.code}" style="display: ${isSelected ? 'flex' : 'none'};">
                    <span class="text-muted" style="font-size: 0.7rem; font-weight: 600;">Div:</span>
                    ${renderDivisionChip('A')}
                    ${renderDivisionChip('B')}
                    ${renderDivisionChip('C')}
                </div>
            `;

            container.appendChild(itemCard);
        });
    });
}

function getDivisionConflict(subCode, division) {
    const sub = MASTER_SUBJECTS.find(s => s.code === subCode);
    if (!sub || !sub.assigned_divisions) return null;

    const assignedInfo = sub.assigned_divisions[division];
    if (!assignedInfo) return null;

    // If editing faculty and it's assigned to the faculty currently being edited, it's not a conflict
    if (currentEditingId !== null && Number(assignedInfo.faculty_id) === Number(currentEditingId)) {
        return null;
    }

    return assignedInfo; // { faculty_id, faculty_name, faculty_code }
}

function toggleSubjectSelection(code, semester) {
    const sub = MASTER_SUBJECTS.find(s => s.code === code);
    if (!sub) return;

    const existingIndex = activeSubjectSelections.findIndex(s => s.code === code);
    const card = document.getElementById(`subItemCard_${code}`);
    const divGroup = document.getElementById(`divGroup_${code}`);
    const chk = document.getElementById(`chk_${code}`);

    if (existingIndex > -1) {
        activeSubjectSelections.splice(existingIndex, 1);
        if (card) card.classList.remove('is-selected');
        if (divGroup) divGroup.style.display = 'none';
    } else {
        const allDivs = ['A', 'B', 'C'];
        const availableDivs = allDivs.filter(d => !getDivisionConflict(code, d));

        if (availableDivs.length === 0) {
            // All divisions are already assigned to other faculty members!
            if (chk) chk.checked = false;

            const conflictLines = allDivs.map(d => {
                const c = getDivisionConflict(code, d);
                return c ? `• Division ${d}: Prof. ${c.faculty_name} (${c.faculty_code})` : '';
            }).filter(Boolean).join('<br>');

            if (typeof showNotification === 'function') {
                showNotification({
                    type: 'danger',
                    title: 'All Divisions Already Assigned',
                    subtitle: 'Subject Fully Allocated',
                    isHtml: true,
                    message: `All divisions for <strong>[${escapeHtml(sub.code)}] ${escapeHtml(sub.name)}</strong> are already assigned to other faculty members:<br><br>${conflictLines}<br><br><small class="text-danger">Two faculty members cannot be assigned the same subject in the same division.</small>`
                });
            } else {
                alert(`All divisions for [${sub.code}] ${sub.name} are already assigned to other faculty members.`);
            }
            return;
        }

        // Pick the first available division
        const defaultDiv = availableDivs[0];
        activeSubjectSelections.push({
            code: sub.code,
            name: sub.name,
            semester: sub.semester,
            divisions: [defaultDiv]
        });
        if (card) card.classList.add('is-selected');
        if (divGroup) {
            divGroup.style.display = 'flex';
            const chips = divGroup.querySelectorAll('.division-chip');
            chips.forEach(chip => {
                const letter = chip.textContent.trim().charAt(0);
                if (letter === defaultDiv) {
                    chip.classList.add('selected');
                } else {
                    chip.classList.remove('selected');
                }
            });
        }
    }

    updateSelectedSubjectsSummary();
}

function toggleSubjectDivision(code, division) {
    const sub = MASTER_SUBJECTS.find(s => s.code === code);
    if (!sub) return;

    const conflict = getDivisionConflict(code, division);
    if (conflict) {
        if (typeof showNotification === 'function') {
            showNotification({
                type: 'danger',
                title: 'Subject Already Assigned',
                subtitle: 'Duplicate Division Allocation Prevented',
                isHtml: true,
                message: `Subject <strong>[${escapeHtml(sub.code)}] ${escapeHtml(sub.name)}</strong> for <strong>Division ${division}</strong> is already assigned to <strong>Prof. ${escapeHtml(conflict.faculty_name)}</strong> (${escapeHtml(conflict.faculty_code)}).<br><br><span class="text-danger fw-semibold">Two faculty members cannot teach the same subject in the same division.</span>`
            });
        } else {
            alert(`Cannot Assign: Subject [${sub.code}] for Division ${division} is already assigned to Prof. ${conflict.faculty_name} (${conflict.faculty_code}).`);
        }
        return;
    }

    const item = activeSubjectSelections.find(s => s.code === code);
    if (!item) return;

    const divIndex = item.divisions.indexOf(division);
    if (divIndex > -1) {
        if (item.divisions.length > 1) {
            item.divisions.splice(divIndex, 1);
        } else {
            if (typeof showNotification === 'function') {
                showNotification({
                    type: 'warning',
                    title: 'Minimum Division Required',
                    subtitle: 'Assignment Requirement',
                    message: `At least one division must remain selected for <strong>[${escapeHtml(sub.code)}] ${escapeHtml(sub.name)}</strong>. To remove the subject entirely, uncheck its checkbox.`
                });
            }
            return;
        }
    } else {
        item.divisions.push(division);
        item.divisions.sort();
    }

    const divGroup = document.getElementById(`divGroup_${code}`);
    if (divGroup) {
        const chips = divGroup.querySelectorAll('.division-chip');
        chips.forEach(chip => {
            const letter = chip.textContent.trim().charAt(0);
            if (item.divisions.includes(letter)) {
                chip.classList.add('selected');
            } else {
                chip.classList.remove('selected');
            }
        });
    }

    updateSelectedSubjectsSummary();
}

function unselectSubject(code) {
    const index = activeSubjectSelections.findIndex(s => s.code === code);
    if (index > -1) {
        activeSubjectSelections.splice(index, 1);
    }

    const chk = document.getElementById(`chk_${code}`);
    if (chk) chk.checked = false;

    const card = document.getElementById(`subItemCard_${code}`);
    if (card) card.classList.remove('is-selected');

    const divGroup = document.getElementById(`divGroup_${code}`);
    if (divGroup) divGroup.style.display = 'none';

    updateSelectedSubjectsSummary();
}

function updateSelectedSubjectsSummary() {
    const countEl = document.getElementById('selectedSubjectCount');
    const listEl = document.getElementById('selectedSubjectChips');
    if (!countEl || !listEl) return;

    countEl.textContent = activeSubjectSelections.length;

    if (activeSubjectSelections.length === 0) {
        listEl.innerHTML = `<span class="text-muted small fst-italic">No subjects selected yet. Click any checkbox above to assign.</span>`;
        return;
    }

    listEl.innerHTML = '';
    activeSubjectSelections.forEach(sub => {
        const chip = document.createElement('span');
        chip.className = 'selected-subject-chip';
        chip.innerHTML = `
            <span><i class="bi bi-check2 text-primary me-1"></i><strong>${escapeHtml(sub.name)}</strong> (Sem ${sub.semester} - Div ${sub.divisions.join(', ')})</span>
            <span class="chip-remove" onclick="unselectSubject('${sub.code}')" title="Remove Subject">
                <i class="bi bi-x-circle-fill"></i>
            </span>
        `;
        listEl.appendChild(chip);
    });
}

// ── 10. Form Submission to Backend (Add / Edit) ─────────────────────
async function handleFacultyFormSubmit() {
    const fullName = document.getElementById('full_name')?.value.trim();
    const code = document.getElementById('faculty_code')?.value.trim();
    const email = document.getElementById('email')?.value.trim();
    const mobile = document.getElementById('mobile')?.value.trim();
    const gender = document.getElementById('gender')?.value || 'Male';
    const dob = document.getElementById('dob')?.value || '';
    const qualification = document.getElementById('qualification')?.value.trim();
    const designation = document.getElementById('designation')?.value;
    const department = document.getElementById('department')?.value;
    const joiningDate = document.getElementById('joining_date')?.value || '';
    const status = document.getElementById('status')?.value || 'Active';
    const address = document.getElementById('address')?.value.trim();
    const city = document.getElementById('city')?.value.trim();
    const state = document.getElementById('state')?.value.trim();
    const pincode = document.getElementById('pincode')?.value.trim();

    if (!fullName || !code || !email || !mobile || !designation || !department) {
        alert('Please fill in all required fields marked with an asterisk (*).');
        return;
    }

    if (!/^\d{10}$/.test(mobile)) {
        alert('Please enter a valid 10-digit mobile number.');
        return;
    }

    const saveBtn = document.getElementById('saveFacultyBtn');
    const originalBtnHtml = saveBtn ? saveBtn.innerHTML : 'Save';
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
    }

    // Build FormData
    const formData = new FormData();
    formData.append('full_name', fullName);
    formData.append('faculty_code', code);
    formData.append('email', email);
    formData.append('mobile', mobile);
    formData.append('gender', gender);
    formData.append('dob', dob);
    formData.append('qualification', qualification);
    formData.append('designation', designation);
    formData.append('department', department);
    formData.append('joining_date', joiningDate);
    formData.append('status', status);
    formData.append('address', address);
    formData.append('city', city);
    formData.append('state', state);
    formData.append('pincode', pincode);
    formData.append('assigned_subjects', JSON.stringify(activeSubjectSelections));

    if (selectedPhotoFile) {
        formData.append('photo', selectedPhotoFile);
    }

    const url = currentEditingId
        ? `/admin/faculty/${currentEditingId}/update`
        : '/admin/faculty/create';

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            const modalEl = document.getElementById('facultyFormModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            displayToast('success', currentEditingId ? 'Faculty Updated' : 'Faculty Added', data.message);
            await loadFacultyData();
        } else {
            if (typeof showNotification === 'function') {
                showNotification({
                    type: 'danger',
                    title: 'Assignment Error',
                    subtitle: 'Validation Conflict',
                    message: data.message || 'Failed to save faculty record.'
                });
            } else {
                displayToast('danger', 'Validation Error', data.message || 'Failed to save faculty record.');
            }
        }
    } catch (err) {
        console.error('Error submitting faculty form:', err);
        displayToast('danger', 'Error', 'An unexpected network error occurred.');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalBtnHtml;
        }
    }
}

// ── 11. View Details Modal with Database Data ───────────────────────
async function openViewFacultyModal(id) {
    try {
        const res = await fetch(`/admin/faculty/${id}`);
        const data = await res.json();
        if (!data.success || !data.faculty) {
            displayToast('danger', 'Error', 'Could not load faculty details.');
            return;
        }

        const faculty = data.faculty;

        // Header avatar & basic info
        const avatarEl = document.getElementById('viewFacultyAvatar');
        const initials = faculty.fullName ? faculty.fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'FA';

        if (avatarEl) {
            avatarEl.innerHTML = faculty.photo
                ? `<img src="${faculty.photo}" alt="${escapeHtml(faculty.fullName)}" class="view-avatar-large" style="object-fit: cover;">`
                : `<div class="view-avatar-large">${initials}</div>`;
        }

        document.getElementById('viewFacultyName').textContent = faculty.fullName;
        document.getElementById('viewFacultyCodeBadge').textContent = faculty.code;
        document.getElementById('viewFacultyDesignation').textContent = `${faculty.designation} (${faculty.department})`;

        // Status pill
        const statusEl = document.getElementById('viewFacultyStatusPill');
        if (statusEl) {
            const isAct = faculty.status === 'Active';
            statusEl.className = `status-pill ${isAct ? 'active' : 'inactive'}`;
            statusEl.innerHTML = `<span class="status-dot"></span>${faculty.status}`;
        }

        // Details Grid
        document.getElementById('viewEmail').textContent = faculty.email || '-';
        document.getElementById('viewMobile').textContent = faculty.mobile || '-';
        document.getElementById('viewGender').textContent = faculty.gender || '-';
        document.getElementById('viewDob').textContent = faculty.dob || '-';

        document.getElementById('viewQualification').textContent = faculty.qualification || '-';
        document.getElementById('viewDesignation').textContent = faculty.designation || '-';
        document.getElementById('viewDepartment').textContent = faculty.department || '-';
        document.getElementById('viewJoiningDate').textContent = faculty.joiningDate || '-';

        const fullAddr = [faculty.address, faculty.city, faculty.state, faculty.pincode].filter(Boolean).join(', ');
        document.getElementById('viewAddress').textContent = fullAddr || '-';

        // Assigned Subjects Table
        const subjectsTable = document.getElementById('viewAssignedSubjectsBody');
        if (subjectsTable) {
            subjectsTable.innerHTML = '';
            if (faculty.assignedSubjects && faculty.assignedSubjects.length > 0) {
                faculty.assignedSubjects.forEach(sub => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="ps-3"><strong class="text-primary font-monospace">${escapeHtml(sub.code)}</strong></td>
                        <td><span class="fw-semibold text-dark">${escapeHtml(sub.name)}</span></td>
                        <td><span class="badge bg-light text-dark border">Semester ${sub.semester}</span></td>
                        <td class="pe-3"><span class="badge bg-primary-subtle text-primary border border-primary-subtle">Division ${sub.divisions.join(', ')}</span></td>
                    `;
                    subjectsTable.appendChild(tr);
                });
            } else {
                subjectsTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center py-3 text-muted small fst-italic">No subjects assigned to this faculty member yet.</td>
                    </tr>
                `;
            }
        }

        const modalEl = document.getElementById('viewFacultyModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        }
    } catch (err) {
        console.error('Error viewing faculty:', err);
        displayToast('danger', 'Error', 'Failed to retrieve faculty from server.');
    }
}

// ── 12. Delete Confirmation Modal & Database Action ─────────────────
function openDeleteFacultyModal(id) {
    const faculty = facultyList.find(f => f.id === id);
    if (!faculty) return;

    currentDeletingId = id;
    document.getElementById('deleteFacultyName').textContent = faculty.fullName;
    document.getElementById('deleteFacultyCode').textContent = faculty.code;

    const modalEl = document.getElementById('deleteFacultyModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
}

async function executeDeleteFaculty() {
    if (!currentDeletingId) return;

    const confirmBtn = document.getElementById('confirmDeleteFacultyBtn');
    const originalBtnHtml = confirmBtn ? confirmBtn.innerHTML : 'Delete';
    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Deleting...';
    }

    try {
        const res = await fetch(`/admin/faculty/${currentDeletingId}/delete`, {
            method: 'POST',
            headers: { 'Accept': 'application/json' }
        });

        const data = await res.json();

        if (res.ok && data.success) {
            const modalEl = document.getElementById('deleteFacultyModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            displayToast('success', 'Faculty Deleted', data.message || 'Faculty record removed.');
            currentDeletingId = null;
            await loadFacultyData();
        } else {
            displayToast('danger', 'Delete Failed', data.message || 'Could not delete faculty.');
        }
    } catch (err) {
        console.error('Error deleting faculty:', err);
        displayToast('danger', 'Error', 'An unexpected network error occurred.');
    } finally {
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalBtnHtml;
        }
    }
}

// ── 13. Reusable Toast & Helper Functions ───────────────────────────
function displayToast(type, title, message) {
    if (typeof showFlash === 'function') {
        showFlash(type, title, message, 4500);
    } else {
        alert(`${title}: ${message}`);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

