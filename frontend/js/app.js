document.addEventListener('DOMContentLoaded', () => {
    const aadhaarInput = document.getElementById('aadhaar-number');
    const captchaInput = document.getElementById('captcha-input');
    const loginBtn = document.getElementById('login-btn');
    const verifyCaptchaBtn = document.getElementById('verify-captcha-btn');
    const refreshCaptchaBtn = document.getElementById('refresh-captcha-btn');
    
    const formContainer = document.getElementById('form-container');
    const successState = document.getElementById('success-state');
    const blockState = document.getElementById('block-state');
    const blockRiskScore = document.getElementById('block-risk-score');
    
    const captchaGroup = document.getElementById('captcha-group');
    const captchaTextDisplay = document.getElementById('captcha-text');
    const captchaError = document.getElementById('captcha-error');

    let currentCaptcha = "";

    // Generate random CAPTCHA
    function generateCaptcha() {
        const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
        let captcha = '';
        for (let i = 0; i < 5; i++) {
            captcha += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        currentCaptcha = captcha;
        captchaTextDisplay.textContent = captcha.split('').join(' ');
        captchaInput.value = '';
        captchaGroup.classList.remove('has-error');
        captchaError.style.display = 'none';
    }

    const isValidAadhaar = () => {
        const value = aadhaarInput.value.trim();
        return /^\d{12}$/.test(value);
    };

    function updateLoginButtonState() {
        if (isValidAadhaar()) {
            loginBtn.classList.add('active');
        } else {
            loginBtn.classList.remove('active');
        }
    }

    // Call initially and use delayed checks for browser autofill
    updateLoginButtonState();
    setTimeout(updateLoginButtonState, 100);
    setTimeout(updateLoginButtonState, 500);
    setTimeout(updateLoginButtonState, 1000);

    // Bind to all relevant events to catch autofill and user interaction
    ['input', 'change', 'blur', 'focus'].forEach(evt => {
        aadhaarInput.addEventListener(evt, updateLoginButtonState);
    });

    window.addEventListener('pageshow', updateLoginButtonState);

    aadhaarInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        updateLoginButtonState();
    });

    aadhaarInput.addEventListener('blur', () => {
        const group = aadhaarInput.closest('.input-group');
        if (aadhaarInput.value.trim().length === 0) {
            group.classList.add('has-error');
        } else {
            group.classList.remove('has-error');
        }
    });

    refreshCaptchaBtn.addEventListener('click', generateCaptcha);

    verifyCaptchaBtn.addEventListener('click', () => {
        const entered = captchaInput.value.trim().toLowerCase();
        if (entered === currentCaptcha.toLowerCase()) {
            formContainer.style.display = 'none';
            successState.style.display = 'block';
        } else {
            captchaGroup.classList.add('has-error');
            captchaError.style.display = 'block';
        }
    });

    // Initialize NVAS CAPTCHA behavior tracking
    if (typeof NvasCaptcha !== 'undefined') {
        NvasCaptcha.init({ endpoint: 'http://127.0.0.1:8000/verify' });
    }

    // Create a debug info container
    const debugContainer = document.createElement('div');
    debugContainer.style.marginTop = '20px';
    debugContainer.style.padding = '10px';
    debugContainer.style.backgroundColor = '#f8f9fa';
    debugContainer.style.border = '1px solid #ddd';
    debugContainer.style.fontSize = '12px';
    debugContainer.style.fontFamily = 'monospace';
    debugContainer.style.whiteSpace = 'pre-wrap';
    debugContainer.innerHTML = '<strong>NVAS Debug Info:</strong><br/>Waiting for verification...';
    document.querySelector('.login-card').appendChild(debugContainer);

    loginBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        if (!isValidAadhaar()) {
            aadhaarInput.closest('.input-group').classList.add('has-error');
            return;
        }

        if (typeof NvasCaptcha === 'undefined') {
            alert("NvasCaptcha package is not loaded!");
            return;
        }

        const originalText = loginBtn.textContent;
        loginBtn.textContent = 'Verifying...';
        
        // Prevent double clicks during verification
        loginBtn.style.pointerEvents = 'none';

        try {
            const result = await NvasCaptcha.verify();
            
            // Display debug info
            debugContainer.innerHTML = `<strong>NVAS Debug Info:</strong><br/>Risk Score: ${result.riskScore}<br/>Action: ${result.action.toUpperCase()}<br/>Reason: ${result.reason}<br/>Model: ${result.modelVersion}`;

            // Handle the decision
            if (result.action === 'allow') {
                formContainer.style.display = 'none';
                successState.style.display = 'block';
            } else if (result.action === 'captcha') {
                loginBtn.style.display = 'none';
                aadhaarInput.disabled = true;
                captchaGroup.style.display = 'block';
                generateCaptcha();
            } else if (result.action === 'block') {
                formContainer.style.display = 'none';
                blockRiskScore.textContent = `Risk Score: ${result.riskScore}`;
                blockState.style.display = 'block';
            }
        } catch (error) {
            console.error(error);
            // Handle error safely
            debugContainer.innerHTML = `<strong>NVAS Debug Error:</strong><br/>${error.message}`;
            alert("Verification failed. Please try again.");
            loginBtn.textContent = originalText;
        } finally {
            loginBtn.style.pointerEvents = 'auto';
        }
    });
});
