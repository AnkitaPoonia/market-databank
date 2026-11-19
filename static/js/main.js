/**
 * Market Databank Platform - Main JavaScript Application File
 * Academic Project - INT253 Web Development in Python Using Django
 * Phase 1: Global Navigation & UI Interactivity
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss alert messages after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // 2. Highlight active sidebar navigation link based on current path
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  sidebarLinks.forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && (href === currentPath || (currentPath.startsWith(href) && href !== '/'))) {
      link.classList.add('active');
    }
  });

  // 3. Functional Keyboard Shortcut: Ctrl+K or Cmd+K focuses Global Search Input
  window.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      const searchInput = document.getElementById('globalSearchInput');
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // 4. Close mobile Offcanvas sidebar when any navigation link is clicked
  const sidebarOffcanvasEl = document.getElementById('sidebarOffcanvas');
  if (sidebarOffcanvasEl) {
    const offcanvasLinks = sidebarOffcanvasEl.querySelectorAll('.sidebar-link');
    offcanvasLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        const offcanvasInstance = bootstrap.Offcanvas.getInstance(sidebarOffcanvasEl);
        if (offcanvasInstance) {
          offcanvasInstance.hide();
        }
      });
    });
  }

  // 5. Demonstration of Client-Side Cookies (Unit VI practical demonstration)
  // Store user's last visited dashboard view preference
  const viewToggleButtons = document.querySelectorAll('[data-view-toggle]');
  viewToggleButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const view = this.getAttribute('data-view-toggle');
      document.cookie = `preferred_market_view=${view};path=/;max-age=${60 * 60 * 24 * 30}`;
    });
  });

  // 6. Enable Bootstrap tooltips everywhere
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 7. Password Visibility Toggle (Show / Hide Password)
  const passwordToggleBtns = document.querySelectorAll('.password-toggle-btn');
  passwordToggleBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-toggle-target');
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.getAttribute('type') === 'password';
        input.setAttribute('type', isPassword ? 'text' : 'password');
        const icon = this.querySelector('i');
        if (icon) {
          if (isPassword) {
            icon.className = 'bi bi-eye-slash text-primary';
            this.setAttribute('aria-label', 'Hide password');
          } else {
            icon.className = 'bi bi-eye text-muted';
            this.setAttribute('aria-label', 'Show password');
          }
        }
      }
    });
  });

  // 8. Interactive Password Strength & Django Validator Checklist
  const regPasswordInput = document.getElementById('id_password');
  const regUsernameInput = document.getElementById('id_username');
  const regEmailInput = document.getElementById('id_email');
  const strengthWrapper = document.getElementById('passwordStrengthWrapper');
  const strengthBar = document.getElementById('passwordStrengthBar');
  const strengthLabel = document.getElementById('passwordStrengthLabel');

  if (regPasswordInput && strengthWrapper && strengthBar && strengthLabel) {
    const commonPasswords = [
      'password', '12345678', '123456789', 'qwertyuiop', 'admin123',
      'welcome123', 'marketdatabank', 'password123', 'pass1234'
    ];

    function evaluatePassword() {
      const val = regPasswordInput.value;
      const username = regUsernameInput ? regUsernameInput.value.trim().toLowerCase() : '';
      const email = regEmailInput ? regEmailInput.value.trim().toLowerCase() : '';

      if (val.length === 0) {
        strengthWrapper.classList.add('d-none');
        resetChecklist();
        return;
      }

      strengthWrapper.classList.remove('d-none');

      // Requirement 1: Minimum Length (8+ chars)
      const isLengthValid = val.length >= 8;
      updateReq('req-length', isLengthValid);

      // Requirement 2: Not entirely numeric
      const isNotNumericOnly = !/^\d+$/.test(val) && /\D/.test(val);
      updateReq('req-numeric', isNotNumericOnly);

      // Requirement 3: Not similar to username or email
      let isNotSimilar = true;
      if (username.length >= 3 && val.toLowerCase().includes(username)) {
        isNotSimilar = false;
      }
      if (email.length >= 4) {
        const emailLocal = email.split('@')[0];
        if (emailLocal.length >= 3 && val.toLowerCase().includes(emailLocal)) {
          isNotSimilar = false;
        }
      }
      updateReq('req-similarity', isNotSimilar);

      // Requirement 4: Not common password
      const isNotCommon = !commonPasswords.includes(val.toLowerCase());
      updateReq('req-common', isNotCommon);

      // Calculate score (0 to 4 based on criteria)
      let score = 0;
      if (isLengthValid) score++;
      if (isNotNumericOnly) score++;
      if (isNotSimilar) score++;
      if (isNotCommon) score++;

      // Bonus complexity points
      const hasMixedCase = /[a-z]/.test(val) && /[A-Z]/.test(val);
      const hasSpecial = /[^A-Za-z0-9]/.test(val);
      const hasDigitsAndLetters = /\d/.test(val) && /[a-zA-Z]/.test(val);

      if (val.length < 8) {
        setStrength(25, 'bg-danger', 'Weak (Minimum 8 chars required)');
      } else if (score < 3 || !isNotNumericOnly || !isNotCommon) {
        setStrength(40, 'bg-danger', 'Weak');
      } else if (score === 4 && (hasMixedCase || hasSpecial || hasDigitsAndLetters) && val.length >= 10) {
        setStrength(100, 'bg-success', 'Strong');
      } else {
        setStrength(70, 'bg-warning', 'Medium');
      }
    }

    function updateReq(elementId, isValid) {
      const el = document.getElementById(elementId);
      if (el) {
        const icon = el.querySelector('.req-icon');
        if (isValid) {
          el.classList.add('req-met');
          if (icon) {
            icon.className = 'bi bi-check-circle-fill text-success req-icon';
          }
        } else {
          el.classList.remove('req-met');
          if (icon) {
            icon.className = 'bi bi-circle text-muted req-icon';
          }
        }
      }
    }

    function resetChecklist() {
      ['req-length', 'req-numeric', 'req-similarity', 'req-common'].forEach(function(id) {
        updateReq(id, false);
      });
      setStrength(0, 'bg-secondary', '');
    }

    function setStrength(percentage, bgClass, label) {
      strengthBar.style.width = percentage + '%';
      strengthBar.className = 'progress-bar password-strength-bar ' + bgClass;
      strengthLabel.textContent = label;
      if (bgClass === 'bg-danger') {
        strengthLabel.className = 'small fw-bold text-danger';
      } else if (bgClass === 'bg-warning') {
        strengthLabel.className = 'small fw-bold text-warning';
      } else if (bgClass === 'bg-success') {
        strengthLabel.className = 'small fw-bold text-success';
      } else {
        strengthLabel.className = 'small text-muted';
      }
    }

    regPasswordInput.addEventListener('input', evaluatePassword);
    if (regUsernameInput) regUsernameInput.addEventListener('input', evaluatePassword);
    if (regEmailInput) regEmailInput.addEventListener('input', evaluatePassword);
  }

  // 9. Grid / Table View Toggle for Explore Databank
  const viewToggleGrid = document.getElementById('viewToggleGrid');
  const viewToggleTable = document.getElementById('viewToggleTable');
  const exploreGridView = document.getElementById('exploreGridView');
  const exploreTableView = document.getElementById('exploreTableView');

  if (viewToggleGrid && viewToggleTable && exploreGridView && exploreTableView) {
    function setExploreView(view) {
      if (view === 'table') {
        exploreGridView.classList.add('d-none');
        exploreTableView.classList.remove('d-none');
        viewToggleTable.classList.add('active');
        viewToggleGrid.classList.remove('active');
        localStorage.setItem('preferred_explore_view', 'table');
      } else {
        exploreTableView.classList.add('d-none');
        exploreGridView.classList.remove('d-none');
        viewToggleGrid.classList.add('active');
        viewToggleTable.classList.remove('active');
        localStorage.setItem('preferred_explore_view', 'grid');
      }
    }

    viewToggleGrid.addEventListener('click', function () { setExploreView('grid'); });
    viewToggleTable.addEventListener('click', function () { setExploreView('table'); });

    // Restore saved preference if exists
    const savedView = localStorage.getItem('preferred_explore_view');
    if (savedView === 'table') {
      setExploreView('table');
    }
  }

  // 10. Description Live Character Counter
  const descInput = document.getElementById('id_description');
  const descCharCount = document.getElementById('descCharCount');
  if (descInput && descCharCount) {
    function updateCharCount() {
      const len = descInput.value.length;
      descCharCount.textContent = len + ' character' + (len === 1 ? '' : 's');
    }
    descInput.addEventListener('input', updateCharCount);
    updateCharCount();
  }

  // 11. Permission Card Radio Selection Sync
  const permCards = document.querySelectorAll('.permission-card');
  permCards.forEach(function (card) {
    const radio = card.querySelector('input[type="radio"]');
    if (radio) {
      if (radio.checked) card.classList.add('selected');
      card.addEventListener('click', function () {
        permCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        radio.checked = true;
      });
      radio.addEventListener('change', function () {
        permCards.forEach(c => c.classList.remove('selected'));
        if (radio.checked) card.classList.add('selected');
      });
    }
  });
});

/**
 * Client-Side Chart Image Export Utility
 * Exports real canvas content directly as PNG without backend overhead.
 */
function downloadChartImage(canvasId, filename) {
  const canvas = document.getElementById(canvasId);
  if (canvas) {
    const imageUri = canvas.toDataURL('image/png');
    const downloadLink = document.createElement('a');
    downloadLink.href = imageUri;
    downloadLink.download = filename || 'market-chart.png';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  }
}

/**
 * Copy Canonical Dataset Reference Link Utility
 */
function copyDatasetLink(customUrl) {
  const urlToCopy = customUrl || window.location.href;
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(urlToCopy).then(showCopyToast).catch(fallbackCopy);
  } else {
    fallbackCopy();
  }

  function fallbackCopy() {
    const tempInput = document.createElement('input');
    tempInput.value = urlToCopy;
    document.body.appendChild(tempInput);
    tempInput.select();
    try {
      document.execCommand('copy');
      showCopyToast();
    } catch (err) {
      alert('Reference link: ' + urlToCopy);
    }
    document.body.removeChild(tempInput);
  }

  function showCopyToast() {
    let toast = document.getElementById('copyFeedbackToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'copyFeedbackToast';
      toast.className = 'copy-feedback-toast';
      toast.innerHTML = '<i class="bi bi-check2-circle text-success fs-5"></i><span>Dataset reference link copied to clipboard!</span>';
      document.body.appendChild(toast);
    }
    toast.classList.add('show');
    setTimeout(function () {
      toast.classList.remove('show');
    }, 3000);
  }
}


