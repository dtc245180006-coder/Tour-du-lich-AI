/* Shared safety, network and accessibility behavior. Loaded before app scripts. */
(() => {
  'use strict';
  const nativeHTML = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
  Object.defineProperty(Element.prototype, 'innerHTML', {
    get: nativeHTML.get,
    set(value) {
      if (!window.DOMPurify) throw new Error('HTML sanitizer unavailable');
      const str = String(value);
      let sanitized;
      const isTablePart = /^\s*<(?:tr|td|th|tbody|thead|tfoot)/i.test(str) || ['TBODY', 'THEAD', 'TFOOT', 'TR', 'TABLE'].includes(this.tagName);
      if (isTablePart) {
        const wrapped = `<table><tbody>${str}</tbody></table>`;
        const cleaned = DOMPurify.sanitize(wrapped, {
          USE_PROFILES: { html: true }, FORBID_TAGS: ['style', 'form', 'iframe'],
          FORBID_ATTR: ['srcdoc', 'style'],
        });
        const match = cleaned.match(/<tbody>([\s\S]*)<\/tbody>/i);
        sanitized = match ? match[1] : cleaned;
      } else {
        sanitized = DOMPurify.sanitize(str, {
          USE_PROFILES: { html: true }, FORBID_TAGS: ['style', 'form', 'iframe'],
          FORBID_ATTR: ['srcdoc', 'style'],
        });
      }
      nativeHTML.set.call(this, sanitized);
    },
  });

  const nativeFetch = window.fetch.bind(window);
  const writeKeys = new Map();
  window.fetch = async (input, options = {}) => {
    const headers = new Headers(options.headers);
    const isBooking = options.method === 'POST' && /^\/api\/v1\/bookings(?:\/guest-request)?$/.test(String(input));
    const isPayment = options.method === 'POST' && String(input) === '/api/v1/payments';
    const fingerprint = String(input) + (options.body || '');
    if (isBooking || isPayment) {
      if (!writeKeys.has(fingerprint)) writeKeys.set(fingerprint, crypto.randomUUID());
      headers.set('Idempotency-Key', writeKeys.get(fingerprint));
      if (isPayment) {
        const payload = JSON.parse(options.body);
        payload.transaction_code ||= writeKeys.get(fingerprint);
        options = { ...options, body: JSON.stringify(payload) };
      }
    }
    let response;
    try {
      response = await nativeFetch(input, { ...options, headers, signal: options.signal || AbortSignal.timeout(30000) });
    } catch (error) {
      window.App?.showToast('Không kết nối được máy chủ. Kiểm tra mạng và thử lại.', 'error');
      throw error;
    }
    if ((isBooking || isPayment) && response.ok) writeKeys.delete(fingerprint);
    const readJSON = response.json.bind(response);
    response.json = async () => {
      const data = await readJSON();
      if (!response.ok && Array.isArray(data.detail)) data.detail = data.detail.map(item => `${item.loc?.slice(1).join('.') || ''}: ${item.msg}`).join('; ');
      return data;
    };
    const url = String(input);
    if (response.status === 401 && !url.includes('/auth/login')) {
      localStorage.removeItem('vietjourney_token');
      localStorage.removeItem('vietjourney_user');
      if (window.App) {
        App.token = null; App.currentUser = null; App.updateUserUI();
        App.showToast('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'error');
      }
    }
    return response;
  };

  for (const type of ['click', 'change', 'input']) document.addEventListener(type, event => {
    const button = event.target.closest('[data-action]');
    if (!button || (button.dataset.event || 'click') !== type || button.disabled) return;
    const action = button.dataset.action;
    // Generated actions take numeric IDs only. Never evaluate JavaScript from HTML.
    const raw = button.dataset.args || '';
    if (!/^\s*(?:-?\d+(?:\.\d+)?\s*(?:,\s*-?\d+(?:\.\d+)?\s*)*)?$/.test(raw)) return;
    const args = raw.trim() ? raw.split(',').map(Number) : [];
    if (Object.hasOwn(window.App || {}, action) && typeof App[action] === 'function') App[action](...args);
  });

  let returnFocus;
  document.addEventListener('error', event => {
    if (event.target instanceof HTMLImageElement && !event.target.src.endsWith('/static/assets/tour-placeholder.svg')) {
      event.target.src = '/static/assets/tour-placeholder.svg';
    }
  }, true);
  const observer = new MutationObserver(() => {
    document.querySelectorAll('[id$="-modal"]').forEach(modal => {
      const shown = !modal.classList.contains('hidden') && modal.style.display !== 'none';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-hidden', String(!shown));
      const heading = modal.querySelector('h2,h3');
      if (heading) { heading.id ||= `${modal.id}-title`; modal.setAttribute('aria-labelledby', heading.id); }
      if (shown && !modal.dataset.focused) {
        returnFocus = document.activeElement;
        modal.dataset.focused = 'true';
        modal.querySelector('input,select,textarea,button')?.focus();
      } else if (!shown && modal.dataset.focused) {
        delete modal.dataset.focused; returnFocus?.focus();
      }
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const modal = [...document.querySelectorAll('[role="dialog"]')].find(el => el.getAttribute('aria-hidden') === 'false');
    if (!modal) return;
    const focusable = [...modal.querySelectorAll('button,input,select,textarea,a[href],[tabindex="0"]')].filter(el => !el.disabled && el.getClientRects().length);
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
  });

  window.UI = {
    showConfirmation(code) {
      let panel = document.getElementById('booking-confirmation');
      if (!panel) { panel = document.createElement('section'); panel.id = 'booking-confirmation'; document.querySelector('main')?.prepend(panel); }
      panel.className = 'p-4 mb-4 bg-emerald-50 text-emerald-900 rounded-xl border border-emerald-300';
      panel.setAttribute('role', 'status');
      panel.textContent = `Đã nhận yêu cầu ${code}. Chỗ chưa được giữ cho đến khi nhân viên xác nhận. Hãy lưu mã yêu cầu để liên hệ.`;
      const copy = document.createElement('button'); copy.textContent = 'Sao chép mã'; copy.className = 'ml-3 underline font-bold';
      copy.onclick = async () => { try { await navigator.clipboard.writeText(code); copy.textContent = 'Đã sao chép'; } catch { copy.textContent = code; } };
      panel.append(copy); panel.scrollIntoView({ block: 'center' });
    },
  };

  document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/v1/app-config').then(r => r.json()).then(config => {
      if (!config.demo_mode) document.querySelectorAll('button[onclick*="quickLogin"]').forEach(button => button.remove());
    }).catch(() => {});
    document.querySelectorAll('label:not([for])').forEach(label => {
      const control = label.parentElement.querySelector('input,select,textarea');
      if (control?.id) label.htmlFor = control.id;
    });
    document.querySelectorAll('label[for]').forEach(label => {
      const control = document.getElementById(label.htmlFor);
      if (control && label.textContent.includes('*')) control.required = true;
    });
    document.querySelectorAll('input[id*="phone"]').forEach(input => { input.type = 'tel'; input.pattern = '[+()0-9 .-]{8,20}'; input.autocomplete = 'tel'; });
    document.querySelectorAll('input[type="number"]').forEach(input => { input.step ||= '1'; });
    document.querySelectorAll('button').forEach(button => {
      if (!button.textContent.trim() && !button.hasAttribute('aria-label')) {
        let label = button.title;
        if (!label) {
          if (button.querySelector('.fa-xmark')) label = 'Đóng';
          else if (button.querySelector('.fa-bars')) label = 'Thu gọn hoặc mở rộng thanh điều hướng';
          else if (button.querySelector('.fa-bell')) label = 'Thông báo hệ thống';
          else if (button.querySelector('.fa-robot')) label = 'Mở Trợ lý AI tư vấn';
          else if (button.querySelector('.fa-moon, .fa-sun')) label = 'Chuyển chế độ giao diện sáng/tối';
          else if (button.querySelector('.fa-magnifying-glass')) label = 'Tìm kiếm';
          else if (button.querySelector('.fa-trash')) label = 'Xóa';
          else if (button.querySelector('.fa-plus')) label = 'Thêm mới';
          else label = 'Thao tác';
        }
        button.setAttribute('aria-label', label);
      }
    });
    observer.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class', 'style'] });
    if (!window.App) return;
    const init = App.init;
    App.init = async function() {
      await init.call(this);
      if (location.pathname === '/tours' && this.currentUser?.role === 'ADMIN') {
        const raw = sessionStorage.getItem('tour-draft');
        if (raw) {
          try {
            const draft = JSON.parse(raw);
            this.openAddTourModal(true);
            Object.entries(draft).forEach(([key, value]) => {
              const input = document.getElementById(`tour-form-${key}`);
              if (input) input.value = value;
            });
          } finally { sessionStorage.removeItem('tour-draft'); }
        }
      }
    };
    App.validateSession = async function() {
      if (!this.token) return;
      try {
        const result = await fetch('/api/v1/auth/me', { headers: { Authorization: `Bearer ${this.token}` } });
        if (!result.ok) throw new Error('Phiên không hợp lệ');
        this.currentUser = await result.json();
        localStorage.setItem('vietjourney_user', JSON.stringify(this.currentUser));
      } catch {
        this.token = null; this.currentUser = null;
        localStorage.removeItem('vietjourney_token'); localStorage.removeItem('vietjourney_user');
      }
    };
    // Avoid duplicate writes while an action is running, including keyboard submits.
    Object.keys(App).filter(name => /^(submit|delete|startDeparture|completeDeparture|promptReject)/.test(name)).forEach(name => {
      const original = App[name]; if (typeof original !== 'function') return;
      let busy = false;
      App[name] = async function(...args) {
        if (busy) return;
        if (/^submit/.test(name)) {
          const visible = [...document.querySelectorAll('[id$="-modal"]')].find(el => !el.classList.contains('hidden') && el.style.display !== 'none');
          const invalid = visible && [...visible.querySelectorAll('input,select,textarea')].find(el => !el.disabled && !el.checkValidity());
          if (invalid) { invalid.reportValidity(); return; }
        }
        busy = true;
        const buttons = [...document.querySelectorAll('button')].filter(el => (el.getAttribute('onclick') || '').includes(name) || el.dataset.action === name);
        buttons.forEach(el => { el.dataset.previousDisabled = String(el.disabled); el.disabled = true; el.setAttribute('aria-busy', 'true'); });
        try { return await original.apply(this, args); }
        finally { busy = false; buttons.forEach(el => { el.disabled = el.dataset.previousDisabled === 'true'; el.removeAttribute('aria-busy'); }); }
      };
    });
    window.alert = message => {
      App.showToast(String(message), 'error');
      const modal = [...document.querySelectorAll('[id$="-modal"]')].find(el => !el.classList.contains('hidden') && el.style.display !== 'none');
      if (modal) {
        let error = modal.querySelector('[data-form-error]');
        if (!error) { error = document.createElement('p'); error.dataset.formError = 'true'; error.className = 'text-rose-700 bg-rose-50 p-3 rounded-lg'; error.setAttribute('role', 'alert'); modal.firstElementChild.prepend(error); }
        error.textContent = String(message);
      }
    };
  });
})();
