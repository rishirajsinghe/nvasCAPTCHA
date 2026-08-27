document.addEventListener('DOMContentLoaded', () => {
    const aadhaarInput = document.getElementById('aadhaar-number');
    const captchaInput = document.getElementById('captcha-input');
    const loginBtn = document.getElementById('login-btn');
    const inputGroups = document.querySelectorAll('.input-group');

    // Basic validation to enable/disable button
    function checkInputs() {
        const isAadhaarValid = aadhaarInput.value.trim().length > 0;
        const isCaptchaValid = captchaInput.value.trim().length > 0;

        if (isAadhaarValid && isCaptchaValid) {
            loginBtn.disabled = false;
            loginBtn.classList.add('active');
        } else {
            loginBtn.disabled = true;
            loginBtn.classList.remove('active');
        }
    }

    // Only allow numbers for Aadhaar
    aadhaarInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        checkInputs();
    });

    captchaInput.addEventListener('input', () => {
        checkInputs();
    });

    // Simulate validation on blur
    aadhaarInput.addEventListener('blur', () => {
        const group = aadhaarInput.closest('.input-group');
        if (aadhaarInput.value.trim().length === 0) {
            group.classList.add('has-error');
        } else {
            group.classList.remove('has-error');
        }
    });

    captchaInput.addEventListener('blur', () => {
        const group = captchaInput.closest('.captcha-input-wrapper').closest('.input-group');
        if (captchaInput.value.trim().length === 0) {
            group.classList.add('has-error');
        } else {
            group.classList.remove('has-error');
        }
    });
});
