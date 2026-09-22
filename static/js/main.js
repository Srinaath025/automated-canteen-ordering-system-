// CanteenFlow UI Enhancements & Interactions

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.custom-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // 2. Quantity Stepper Handler
    document.querySelectorAll('.qty-stepper').forEach(stepper => {
        const minusBtn = stepper.querySelector('.qty-minus');
        const plusBtn = stepper.querySelector('.qty-plus');
        const input = stepper.querySelector('.qty-input');

        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let val = parseInt(input.value) || 1;
                const min = parseInt(input.min) || 1;
                if (val > min) {
                    input.value = val - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });

            plusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let val = parseInt(input.value) || 1;
                const max = parseInt(input.max) || 99;
                if (val < max) {
                    input.value = val + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });

    // 3. Payment Method Switcher (QR Code / UPI)
    const paymentMethodSelect = document.getElementById('payment-method');
    const qrSection = document.getElementById('qr-section');
    const cardSection = document.getElementById('card-section');

    if (paymentMethodSelect) {
        const updatePaymentView = () => {
            const method = paymentMethodSelect.value;
            if (qrSection) {
                qrSection.style.display = (method === 'qr_code' || method === 'upi') ? 'block' : 'none';
            }
            if (cardSection) {
                cardSection.style.display = (method === 'credit_card' || method === 'debit_card') ? 'block' : 'none';
            }
        };

        paymentMethodSelect.addEventListener('change', updatePaymentView);
        updatePaymentView(); // Run on initial load
    }

    // 4. Registration Password Match Validator
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password');
            if (confirmPassword && password !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match! Please check and try again.');
                confirmPassword.focus();
            }
        });
    }
});
