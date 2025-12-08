/**
 * InvoiceFlow Enhanced Form Handling
 * Real-time validation, async submission, and accessibility
 */

import Utils from './utils.js';
import Toast from './toast.js';

const VALIDATION_RULES = {
  required: {
    validate: (value) => value.trim().length > 0,
    message: 'This field is required'
  },
  email: {
    validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message: 'Please enter a valid email address'
  },
  minLength: {
    validate: (value, param) => value.length >= parseInt(param),
    message: (param) => `Must be at least ${param} characters`
  },
  maxLength: {
    validate: (value, param) => value.length <= parseInt(param),
    message: (param) => `Must be no more than ${param} characters`
  },
  pattern: {
    validate: (value, param) => new RegExp(param).test(value),
    message: 'Please match the requested format'
  },
  match: {
    validate: (value, param) => {
      const target = document.querySelector(param);
      return target && value === target.value;
    },
    message: 'Fields do not match'
  },
  phone: {
    validate: (value) => /^[\d\s\-\+\(\)]{10,}$/.test(value),
    message: 'Please enter a valid phone number'
  },
  url: {
    validate: (value) => {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },
    message: 'Please enter a valid URL'
  },
  number: {
    validate: (value) => !isNaN(parseFloat(value)) && isFinite(value),
    message: 'Please enter a valid number'
  },
  min: {
    validate: (value, param) => parseFloat(value) >= parseFloat(param),
    message: (param) => `Value must be at least ${param}`
  },
  max: {
    validate: (value, param) => parseFloat(value) <= parseFloat(param),
    message: (param) => `Value must be no more than ${param}`
  }
};

class FormValidator {
  constructor(form, options = {}) {
    this.form = typeof form === 'string' ? document.querySelector(form) : form;
    if (!this.form) return;

    this.options = {
      validateOnBlur: true,
      validateOnInput: true,
      showSuccessState: true,
      focusFirstError: true,
      scrollToError: true,
      debounceDelay: 300,
      ...options
    };

    this.fields = new Map();
    this.errors = new Map();
    this.init();
  }

  init() {
    this.form.setAttribute('novalidate', '');
    this.form.classList.add('form-enhanced');

    const inputs = this.form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => this.setupField(input));

    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  setupField(input) {
    const id = input.id || Utils.generateId('field');
    input.id = id;

    const wrapper = input.closest('.form-group') || input.parentElement;
    wrapper.classList.add('form-field-wrapper');

    let errorContainer = wrapper.querySelector('.field-error');
    if (!errorContainer) {
      errorContainer = document.createElement('div');
      errorContainer.className = 'field-error';
      errorContainer.setAttribute('role', 'alert');
      errorContainer.setAttribute('aria-live', 'polite');
      wrapper.appendChild(errorContainer);
    }

    input.setAttribute('aria-describedby', `${id}-error`);
    errorContainer.id = `${id}-error`;

    this.fields.set(id, { input, wrapper, errorContainer });

    if (this.options.validateOnBlur) {
      input.addEventListener('blur', () => this.validateField(input));
    }

    if (this.options.validateOnInput) {
      const debouncedValidate = Utils.debounce(
        () => this.validateField(input),
        this.options.debounceDelay
      );
      input.addEventListener('input', debouncedValidate);
    }

    input.addEventListener('focus', () => {
      wrapper.classList.add('field-focused');
    });

    input.addEventListener('blur', () => {
      wrapper.classList.remove('field-focused');
      if (input.value) {
        wrapper.classList.add('field-filled');
      } else {
        wrapper.classList.remove('field-filled');
      }
    });
  }

  validateField(input) {
    const rules = this.getFieldRules(input);
    const value = input.value;
    const fieldData = this.fields.get(input.id);

    if (!fieldData) return true;

    for (const rule of rules) {
      const ruleConfig = VALIDATION_RULES[rule.name];
      if (!ruleConfig) continue;

      const isValid = ruleConfig.validate(value, rule.param);
      
      if (!isValid) {
        const message = typeof ruleConfig.message === 'function'
          ? ruleConfig.message(rule.param)
          : (rule.customMessage || ruleConfig.message);
        
        this.showError(input, message);
        return false;
      }
    }

    this.clearError(input);
    return true;
  }

  getFieldRules(input) {
    const rules = [];

    if (input.required || input.hasAttribute('data-required')) {
      rules.push({ name: 'required' });
    }

    if (input.type === 'email') {
      rules.push({ name: 'email' });
    }

    if (input.minLength > 0) {
      rules.push({ name: 'minLength', param: input.minLength });
    }

    if (input.maxLength > 0 && input.maxLength < 524288) {
      rules.push({ name: 'maxLength', param: input.maxLength });
    }

    if (input.pattern) {
      rules.push({ 
        name: 'pattern', 
        param: input.pattern,
        customMessage: input.title || null
      });
    }

    if (input.min !== '') {
      rules.push({ name: 'min', param: input.min });
    }

    if (input.max !== '') {
      rules.push({ name: 'max', param: input.max });
    }

    const dataRules = input.dataset.validate;
    if (dataRules) {
      dataRules.split('|').forEach(rule => {
        const [name, param] = rule.split(':');
        rules.push({ name, param });
      });
    }

    return rules;
  }

  showError(input, message) {
    const fieldData = this.fields.get(input.id);
    if (!fieldData) return;

    const { wrapper, errorContainer } = fieldData;
    
    wrapper.classList.remove('field-valid');
    wrapper.classList.add('field-invalid');
    input.setAttribute('aria-invalid', 'true');
    errorContainer.textContent = message;
    
    this.errors.set(input.id, message);
  }

  clearError(input) {
    const fieldData = this.fields.get(input.id);
    if (!fieldData) return;

    const { wrapper, errorContainer } = fieldData;
    
    wrapper.classList.remove('field-invalid');
    input.setAttribute('aria-invalid', 'false');
    errorContainer.textContent = '';
    
    if (this.options.showSuccessState && input.value) {
      wrapper.classList.add('field-valid');
    }
    
    this.errors.delete(input.id);
  }

  validateAll() {
    let isValid = true;
    let firstInvalid = null;

    this.fields.forEach(({ input }) => {
      const fieldValid = this.validateField(input);
      if (!fieldValid && isValid) {
        isValid = false;
        firstInvalid = input;
      }
    });

    if (!isValid && firstInvalid) {
      if (this.options.focusFirstError) {
        firstInvalid.focus();
      }
      if (this.options.scrollToError) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    return isValid;
  }

  async handleSubmit(e) {
    e.preventDefault();

    if (!this.validateAll()) {
      Toast.error('Validation Error', 'Please fix the errors in the form');
      return;
    }

    const submitBtn = this.form.querySelector('[type="submit"]');
    const originalText = submitBtn?.textContent;
    
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="btn-spinner"></span>
        <span>Processing...</span>
      `;
    }

    try {
      const formData = new FormData(this.form);
      const action = this.form.action;
      const method = this.form.method.toUpperCase();

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      const response = await fetch(action, {
        method,
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          ...(csrfToken && { 'X-CSRFToken': csrfToken })
        }
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        Toast.success('Success', data.message || 'Form submitted successfully');
        
        if (data.redirect) {
          window.location.href = data.redirect;
        } else if (this.options.resetOnSuccess !== false) {
          this.form.reset();
          this.fields.forEach(({ wrapper }) => {
            wrapper.classList.remove('field-valid', 'field-filled');
          });
        }

        this.form.dispatchEvent(new CustomEvent('form:success', { detail: data }));
      } else {
        if (data.errors) {
          Object.entries(data.errors).forEach(([field, messages]) => {
            const input = this.form.querySelector(`[name="${field}"]`);
            if (input) {
              this.showError(input, Array.isArray(messages) ? messages[0] : messages);
            }
          });
        }
        
        Toast.error('Error', data.message || 'Something went wrong');
        this.form.dispatchEvent(new CustomEvent('form:error', { detail: data }));
      }
    } catch (error) {
      console.error('Form submission error:', error);
      Toast.error('Network Error', 'Please check your connection and try again');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    }
  }

  reset() {
    this.form.reset();
    this.errors.clear();
    this.fields.forEach(({ wrapper, errorContainer }) => {
      wrapper.classList.remove('field-valid', 'field-invalid', 'field-filled');
      errorContainer.textContent = '';
    });
  }

  destroy() {
    this.form.removeAttribute('novalidate');
    this.form.classList.remove('form-enhanced');
    this.fields.clear();
    this.errors.clear();
  }
}

export function initForms(selector = 'form[data-enhanced]') {
  const forms = document.querySelectorAll(selector);
  return Array.from(forms).map(form => new FormValidator(form));
}

export { FormValidator, VALIDATION_RULES };
export default FormValidator;
