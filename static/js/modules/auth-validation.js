(function() {
    'use strict';

    const ValidationRules = {
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        username: {
            minLength: 3,
            maxLength: 150,
            pattern: /^[\w.@+-]+$/,
            messages: {
                minLength: 'Username must be at least 3 characters',
                maxLength: 'Username cannot exceed 150 characters',
                pattern: 'Username contains invalid characters'
            }
        },
        password: {
            minLength: 12,
            requirements: {
                length: { test: (p) => p.length >= 12, label: 'At least 12 characters' },
                lowercase: { test: (p) => /[a-z]/.test(p), label: 'One lowercase letter' },
                uppercase: { test: (p) => /[A-Z]/.test(p), label: 'One uppercase letter' },
                number: { test: (p) => /[0-9]/.test(p), label: 'One number' },
                special: { test: (p) => /[^a-zA-Z0-9]/.test(p), label: 'One special character' }
            }
        }
    };

    class FormValidator {
        constructor(form) {
            this.form = form;
            this.inputs = form.querySelectorAll('.auth-input');
            this.submitBtn = form.querySelector('.auth-submit-btn');
            this.init();
        }

        init() {
            this.inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.handleInput(input));
            });

            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        handleInput(input) {
            const group = input.closest('.auth-input-group');
            if (group?.classList.contains('has-error')) {
                this.validateField(input);
            }
        }

        validateField(input) {
            const group = input.closest('.auth-input-group');
            const errorEl = group?.querySelector('.auth-error-message');
            const fieldName = input.name;
            let isValid = true;
            let message = '';

            if (input.required && !input.value.trim()) {
                isValid = false;
                message = 'This field is required';
            } else if (input.value.trim()) {
                const validation = this.getFieldValidation(fieldName, input.value);
                isValid = validation.isValid;
                message = validation.message;
            }

            this.updateFieldState(group, isValid, message, errorEl, input.value.trim());
            return isValid;
        }

        getFieldValidation(fieldName, value) {
            switch (fieldName) {
                case 'email':
                    return {
                        isValid: ValidationRules.email.pattern.test(value),
                        message: !ValidationRules.email.pattern.test(value) ? ValidationRules.email.message : ''
                    };

                case 'username':
                    if (value.length < ValidationRules.username.minLength) {
                        return { isValid: false, message: ValidationRules.username.messages.minLength };
                    }
                    if (value.length > ValidationRules.username.maxLength) {
                        return { isValid: false, message: ValidationRules.username.messages.maxLength };
                    }
                    if (!ValidationRules.username.pattern.test(value)) {
                        return { isValid: false, message: ValidationRules.username.messages.pattern };
                    }
                    return { isValid: true, message: '' };

                case 'password1':
                    const { score, checks } = this.getPasswordStrength(value);
                    const meetsLength = checks.length;
                    const isStrongEnough = meetsLength && score >= 3;
                    return {
                        isValid: isStrongEnough,
                        message: !meetsLength ? 'Password must be at least 12 characters' : 
                                 (score < 3 ? 'Password needs more complexity' : '')
                    };

                case 'password2':
                    const password1 = this.form.querySelector('#id_password1');
                    if (password1 && value !== password1.value) {
                        return { isValid: false, message: 'Passwords do not match' };
                    }
                    return { isValid: true, message: '' };

                default:
                    return { isValid: true, message: '' };
            }
        }

        getPasswordScore(password) {
            const { score } = this.getPasswordStrength(password);
            return score;
        }

        getPasswordStrength(password) {
            let score = 0;
            const checks = {};
            Object.entries(ValidationRules.password.requirements).forEach(([key, req]) => {
                checks[key] = req.test(password);
                if (checks[key]) score++;
            });
            return { score, checks };
        }

        updateFieldState(group, isValid, message, errorEl, hasValue) {
            if (!group) return;
            
            group.classList.toggle('has-error', !isValid);
            group.classList.toggle('is-valid', isValid && hasValue);
            
            if (errorEl) {
                errorEl.textContent = message;
            }
        }

        handleSubmit(e) {
            let isFormValid = true;

            this.inputs.forEach(input => {
                if (input.required && !this.validateField(input)) {
                    isFormValid = false;
                }
            });

            const termsCheckbox = this.form.querySelector('input[name="terms"]');
            if (termsCheckbox && termsCheckbox.required && !termsCheckbox.checked) {
                isFormValid = false;
                termsCheckbox.closest('.auth-checkbox')?.classList.add('has-error');
            }

            if (!isFormValid) {
                e.preventDefault();
                const firstError = this.form.querySelector('.has-error .auth-input, .has-error input[type="checkbox"]');
                firstError?.focus();
                
                this.announceError('Please correct the errors in the form');
                return;
            }

            if (this.submitBtn) {
                this.submitBtn.classList.add('is-loading');
                this.submitBtn.disabled = true;
            }
        }

        announceError(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('role', 'alert');
            announcement.setAttribute('aria-live', 'assertive');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            document.body.appendChild(announcement);
            
            setTimeout(() => announcement.remove(), 1000);
        }
    }

    class PasswordStrengthMeter {
        constructor(passwordInput) {
            this.input = passwordInput;
            this.strengthContainer = document.querySelector('.auth-password-strength');
            this.strengthText = document.querySelector('.auth-strength-text');
            this.requirements = document.querySelectorAll('.auth-requirement');
            this.confirmInput = document.querySelector('#id_password2');
            
            if (this.input) {
                this.init();
            }
        }

        init() {
            this.input.addEventListener('input', () => this.update());
            
            if (this.confirmInput) {
                this.confirmInput.addEventListener('input', () => this.checkMatch());
            }
        }

        update() {
            const password = this.input.value;
            
            if (!password) {
                this.strengthContainer?.classList.remove('is-visible');
                this.requirements.forEach(req => req.classList.remove('is-met'));
                return;
            }

            this.strengthContainer?.classList.add('is-visible');
            
            let score = 0;
            const checks = {};
            
            Object.entries(ValidationRules.password.requirements).forEach(([key, req]) => {
                checks[key] = req.test(password);
                if (checks[key]) score++;
            });

            this.requirements.forEach(req => {
                const requirement = req.dataset.requirement;
                req.classList.toggle('is-met', checks[requirement]);
            });

            const segments = document.querySelectorAll('.auth-strength-segment');
            segments.forEach((seg, i) => {
                seg.classList.toggle('is-active', i < score);
            });

            let level = 'weak';
            let text = 'Weak password';
            
            if (score >= 5) { level = 'strong'; text = 'Strong password'; }
            else if (score >= 4) { level = 'good'; text = 'Good password'; }
            else if (score >= 2) { level = 'fair'; text = 'Fair password'; }

            if (this.strengthContainer) {
                this.strengthContainer.dataset.level = level;
            }
            if (this.strengthText) {
                this.strengthText.textContent = text;
            }

            if (this.confirmInput?.value) {
                this.checkMatch();
            }
        }

        checkMatch() {
            if (!this.confirmInput) return;
            
            const group = this.confirmInput.closest('.auth-input-group');
            const errorEl = document.getElementById('password2-error');
            const matches = this.input.value === this.confirmInput.value;

            if (this.confirmInput.value) {
                group?.classList.toggle('has-error', !matches);
                group?.classList.toggle('is-valid', matches);
                if (errorEl) {
                    errorEl.textContent = matches ? '' : 'Passwords do not match';
                }
            }
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        if (loginForm) {
            new FormValidator(loginForm);
        }

        if (signupForm) {
            new FormValidator(signupForm);
            const password1 = document.getElementById('id_password1');
            if (password1) {
                new PasswordStrengthMeter(password1);
            }
        }

        document.querySelectorAll('.auth-input').forEach(input => {
            input.addEventListener('focus', function() {
                this.closest('.auth-input-group')?.classList.add('is-focused');
            });
            input.addEventListener('blur', function() {
                this.closest('.auth-input-group')?.classList.remove('is-focused');
            });
        });

        document.querySelectorAll('.auth-password-toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const input = document.getElementById(targetId);
                if (!input) return;

                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                this.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
                this.classList.toggle('is-visible', isPassword);
            });
        });
    });
})();
