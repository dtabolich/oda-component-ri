// Form validation and UX improvements
document.addEventListener('DOMContentLoaded', function() {
  // Format phone number input
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
      // Remove non-numeric characters except +
      let value = e.target.value.replace(/[^\d+]/g, '');
      
      // Ensure + is only at the beginning
      if (value.includes('+')) {
        const parts = value.split('+');
        value = '+' + parts.filter(p => p).join('');
      }
      
      e.target.value = value;
    });

    // Validate phone format on blur
    input.addEventListener('blur', function(e) {
      const value = e.target.value;
      if (value && !/^[\+]?[0-9]{10,20}$/.test(value)) {
        showFieldError(e.target, 'Please enter a valid phone number (10-20 digits)');
      } else {
        clearFieldError(e.target);
      }
    });
  });

  // Format verification code input
  const codeInputs = document.querySelectorAll('.code-input');
  codeInputs.forEach(input => {
    input.addEventListener('input', function(e) {
      // Only allow numbers
      e.target.value = e.target.value.replace(/[^\d]/g, '');
      
      // Auto-submit when 6 digits are entered
      if (e.target.value.length === 6) {
        // Small delay to show the last digit
        setTimeout(() => {
          const form = e.target.closest('form');
          if (form) {
            submitFormWithLoading(form);
          }
        }, 300);
      }
    });
  });

  // Form submission with loading state
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Please wait...';
        submitBtn.classList.add('loading');
      }
    });
  });

  // Auto-focus on first input
  const firstInput = document.querySelector('.form-input');
  if (firstInput) {
    firstInput.focus();
  }
});

// Helper functions
function showFieldError(input, message) {
  clearFieldError(input);
  
  input.classList.add('error');
  const errorSpan = document.createElement('span');
  errorSpan.className = 'field-error';
  errorSpan.textContent = message;
  
  input.parentNode.appendChild(errorSpan);
}

function clearFieldError(input) {
  input.classList.remove('error');
  const existingError = input.parentNode.querySelector('.field-error');
  if (existingError) {
    existingError.remove();
  }
}

function submitFormWithLoading(form) {
  const submitBtn = form.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Please wait...';
    submitBtn.classList.add('loading');
  }
  form.submit();
}

// Handle browser back button
window.addEventListener('pageshow', function(event) {
  if (event.persisted) {
    // Page was loaded from cache, reload to get fresh flow
    window.location.reload();
  }
});

// Show notification (if needed)
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `message ${type}`;
  notification.textContent = message;
  
  const container = document.querySelector('.auth-card, .dashboard-card');
  if (container) {
    container.insertBefore(notification, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => notification.remove(), 300);
    }, 5000);
  }
}
