/* CampusSync - Admin JS */

document.addEventListener('DOMContentLoaded', function () {
    console.log("Admin module loaded.");

    // 1. Password Show/Hide Toggle
    const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
    togglePasswordBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                const icon = this.querySelector('i');
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                }
            }
        });
    });

    // 2. Profile Photo Live Preview
    const profileFileInput = document.getElementById('profile_photo');
    const profileImgPreview = document.getElementById('profileImagePreview');
    const avatarPlaceholder = document.getElementById('profileAvatarPlaceholder');

    if (profileFileInput && profileImgPreview) {
        profileFileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (evt) {
                    profileImgPreview.src = evt.target.result;
                    profileImgPreview.classList.remove('d-none');
                    if (avatarPlaceholder) {
                        avatarPlaceholder.classList.add('d-none');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
