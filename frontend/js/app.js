// VietJourney AI Frontend Core Application
window.App = {
  currentUser: null,
  token: null,
  currentTab: 'home',
  currentCategory: 'ALL',
  tours: [],
  departures: [],
  bookings: [],
  payments: [],
  guides: [],
  guideViewMode: 'table',
  guideFilterStatus: 'ALL',
  guideSearchKeyword: '',
  guideLanguageFilter: 'ALL',
  feedbacks: [],
  users: [],
  stats: {},

  // Search & Filter State across all employee features
  tourSearchKeyword: '',
  tourCategoryFilter: 'ALL',
  tourStatusFilter: 'ALL',
  tourPriceFilter: 'ALL',

  departureSearchKeyword: '',
  departureStatusFilter: 'ALL',
  departureGuideFilter: 'ALL',
  departureFromDate: '',
  departureToDate: '',

  bookingSearchKeyword: '',
  bookingStatusFilter: 'ALL',
  bookingPaymentFilter: 'ALL',

  queueSearchKeyword: '',

  paymentSearchKeyword: '',
  paymentTypeFilter: 'ALL',
  paymentMethodFilter: 'ALL',

  feedbackSearchKeyword: '',
  feedbackRatingFilter: 'ALL',
  feedbackSentimentFilter: 'ALL',

// ===================================================================
  // TRA CỨU ĐƠN TOUR & TIẾN ĐỘ THANH TOÁN (GUEST TRACKING & MAGIC LINK)
  // ===================================================================
toggleForgotBookingMode: function() {
    const box = document.getElementById('tracking-forgot-box');
    const label = document.getElementById('btn-toggle-forgot-label');
    if (!box) return;
    const isHidden = box.classList.contains('hidden');
    if (isHidden) {
      box.classList.remove('hidden');
      if (label) label.innerText = 'Đóng phần tìm lại mã qua Gmail';
      const input = document.getElementById('track-forgot-email');
      if (input) input.focus();
    } else {
      box.classList.add('hidden');
      if (label) label.innerText = 'Quên mã đặt tour? Gửi lại qua Gmail';
    }
  },

  submitResendTrackingEmail: async function() {
    const input = document.getElementById('track-forgot-email');
    const btn = document.getElementById('btn-submit-forgot-email');
    const msgBox = document.getElementById('track-forgot-msg');
    const email = input ? input.value.trim() : '';

    if (!email || !email.includes('@')) {
      alert('Vui lòng nhập địa chỉ Gmail/Email hợp lệ.');
      if (input) input.focus();
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Đang gửi...';
    }
    if (msgBox) msgBox.classList.add('hidden');

    try {
      const res = await fetch('/api/v1/bookings/resend-tracking-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      });
      const data = await res.json();

      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Gửi Về Gmail';
      }

      if (msgBox) {
        msgBox.classList.remove('hidden');
        msgBox.innerText = data.message || 'Đã gửi danh sách mã đặt tour về Gmail của bạn. Vui lòng mở hộp thư để kiểm tra.';
      }
      this.showToast('Đã gửi thông tin đơn tour về Gmail thành công!', 'success');
    } catch (err) {
      console.error(err);
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Gửi Về Gmail';
      }
      alert('Đã xảy ra lỗi khi kết nối máy chủ gửi mail. Vui lòng thử lại sau.');
    }
  },


  openGuestTrackingModal: function(code = '', contact = '') {
    const modal = document.getElementById('guest-tracking-modal');
    if (!modal) return;
    
    const searchForm = document.getElementById('tracking-search-form');
    const resultBox = document.getElementById('tracking-result-box');
    const loadingEl = document.getElementById('tracking-loading');
    const errorBox = document.getElementById('tracking-error');
    
    if (searchForm) searchForm.classList.remove('hidden');
    if (resultBox) resultBox.classList.add('hidden');
    if (loadingEl) loadingEl.classList.add('hidden');
    if (errorBox) errorBox.classList.add('hidden');
    
    const inputCode = document.getElementById('track-input-code');
    const inputContact = document.getElementById('track-input-contact');
    if (inputCode) inputCode.value = code || '';
    if (inputContact) inputContact.value = contact || '';
    
    modal.classList.remove('hidden');
    if (code && contact) {
      this.submitGuestTrackingSearch();
    }
  },

  submitGuestTrackingSearch: async function() {
    const inputCode = document.getElementById('track-input-code');
    const inputContact = document.getElementById('track-input-contact');
    const code = inputCode ? inputCode.value.trim().toUpperCase() : '';
    const contact = inputContact ? inputContact.value.trim() : '';

    const errorBox = document.getElementById('tracking-error');
    const loadingEl = document.getElementById('tracking-loading');
    const resultBox = document.getElementById('tracking-result-box');

    if (!code || !contact) {
      if (errorBox) {
        errorBox.classList.remove('hidden');
        errorBox.innerText = 'Vui lòng nhập cả Mã đặt chỗ và Số điện thoại hoặc Email đăng ký.';
      }
      return;
    }

    if (errorBox) errorBox.classList.add('hidden');
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (resultBox) resultBox.classList.add('hidden');

    try {
      const res = await fetch('/api/v1/bookings/track-guest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_code: code, contact: contact })
      });
      const data = await res.json();
      if (loadingEl) loadingEl.classList.add('hidden');

      if (!res.ok) {
        if (errorBox) {
          errorBox.classList.remove('hidden');
          errorBox.innerText = data.detail || 'Không tìm thấy đơn hàng tương ứng. Vui lòng kiểm tra lại thông tin.';
        }
        return;
      }

      this.renderGuestTrackingResult(data);
    } catch (e) {
      console.error(e);
      if (loadingEl) loadingEl.classList.add('hidden');
      if (errorBox) {
        errorBox.classList.remove('hidden');
        errorBox.innerText = 'Đã xảy ra lỗi khi kết nối máy chủ. Vui lòng thử lại sau.';
      }
    }
  },

  loadMagicTrack: async function(code, token) {
    const modal = document.getElementById('guest-tracking-modal');
    if (!modal) return;
    modal.classList.remove('hidden');

    const searchForm = document.getElementById('tracking-search-form');
    const resultBox = document.getElementById('tracking-result-box');
    const loadingEl = document.getElementById('tracking-loading');
    const errorBox = document.getElementById('tracking-error');

    if (searchForm) searchForm.classList.add('hidden'); // Ẩn form khi truy cập từ magic link
    if (resultBox) resultBox.classList.add('hidden');
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (errorBox) errorBox.classList.add('hidden');

    try {
      const res = await fetch(`/api/v1/bookings/magic-track?code=${encodeURIComponent(code)}&token=${encodeURIComponent(token)}`);
      const data = await res.json();
      if (loadingEl) loadingEl.classList.add('hidden');

      if (!res.ok) {
        if (errorBox) {
          errorBox.classList.remove('hidden');
          errorBox.innerText = data.detail || 'Liên kết tra cứu không hợp lệ hoặc đã hết hạn.';
        }
        if (searchForm) searchForm.classList.remove('hidden');
        return;
      }

      this.renderGuestTrackingResult(data);
    } catch (e) {
      console.error(e);
      if (loadingEl) loadingEl.classList.add('hidden');
      if (errorBox) {
        errorBox.classList.remove('hidden');
        errorBox.innerText = 'Không thể kết nối đến máy chủ. Vui lòng thử lại.';
      }
      if (searchForm) searchForm.classList.remove('hidden');
    }
  },

  renderGuestTrackingResult: function(data) {
    const resultBox = document.getElementById('tracking-result-box');
    if (!resultBox) return;
    resultBox.classList.remove('hidden');

    // Header info
    const codeEl = document.getElementById('track-res-code');
    if (codeEl) codeEl.innerText = data.booking_code;

    const titleEl = document.getElementById('track-res-tour-title');
    if (titleEl) titleEl.innerText = data.tour.title;

    const depDateEl = document.getElementById('track-res-dep-date');
    if (depDateEl) depDateEl.innerText = `${data.tour.departure_date} (Về: ${data.tour.return_date || 'Theo tour'})`;

    const numPeopleEl = document.getElementById('track-res-num-people');
    if (numPeopleEl) numPeopleEl.innerText = `${data.num_people} khách (${data.tour.duration_days} ngày)`;

    const custNameEl = document.getElementById('track-res-cust-name');
    if (custNameEl) custNameEl.innerText = `${data.customer.full_name} (${data.customer.phone})`;

    // Status badge styling
    const badgeStatus = document.getElementById('track-res-badge-status');
    if (badgeStatus) {
      let label = 'CHỜ XÁC NHẬN';
      let cls = 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300';
      if (data.status === 'PENDING') {
        label = 'CHỜ THANH TOÁN CỌC';
        cls = 'bg-sky-100 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300';
      } else if (data.status === 'DEPOSITED') {
        label = 'ĐÃ ĐẶT CỌC (GIỮ CHỖ)';
        cls = 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300';
      } else if (data.status === 'CONFIRMED') {
        label = 'ĐÃ THANH TOÁN ĐỦ';
        cls = 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300';
      } else if (data.status === 'COMPLETED') {
        label = 'HOÀN THÀNH CHUYẾN ĐI';
        cls = 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200';
      } else if (data.status === 'CANCELLED') {
        label = 'ĐÃ HỦY ĐẶT CHỖ';
        cls = 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300';
      }
      badgeStatus.className = `inline-block px-2.5 py-0.5 rounded-md text-[10px] font-extrabold ${cls}`;
      badgeStatus.innerText = label;
    }

    // Progress bar & Financials
    const total = data.total_amount || 0;
    const paid = data.paid_amount || 0;
    const remaining = data.remaining_amount || 0;
    const percent = total > 0 ? Math.min(100, Math.round((paid / total) * 100)) : 0;

    const percentEl = document.getElementById('track-res-percent');
    if (percentEl) percentEl.innerText = `${percent}%`;

    const barEl = document.getElementById('track-res-progress-bar');
    if (barEl) {
      barEl.style.width = `${percent}%`;
      barEl.className = percent >= 100 ? 'bg-emerald-500 h-2.5 rounded-full transition-all duration-500' : 'bg-sky-600 h-2.5 rounded-full transition-all duration-500';
    }

    const totalEl = document.getElementById('track-res-total');
    if (totalEl) totalEl.innerText = `${total.toLocaleString('vi-VN')} đ`;

    const paidEl = document.getElementById('track-res-paid');
    if (paidEl) paidEl.innerText = `${paid.toLocaleString('vi-VN')} đ`;

    const remEl = document.getElementById('track-res-remaining');
    if (remEl) remEl.innerText = `${remaining.toLocaleString('vi-VN')} đ`;

    // VietQR Box
    const qrBox = document.getElementById('track-vietqr-box');
    if (qrBox) {
      if (remaining > 0 && data.status !== 'CANCELLED') {
        qrBox.classList.remove('hidden');
        const qrImg = document.getElementById('track-vietqr-img');
        if (qrImg) qrImg.src = data.vietqr.qr_url;

        const qrBank = document.getElementById('track-qr-bank');
        if (qrBank) qrBank.innerText = data.vietqr.bank_name;

        const qrAcc = document.getElementById('track-qr-acc');
        if (qrAcc) qrAcc.innerText = data.vietqr.account_no;

        const qrName = document.getElementById('track-qr-name');
        if (qrName) qrName.innerText = data.vietqr.account_name;

        const qrAmount = document.getElementById('track-qr-amount');
        if (qrAmount) qrAmount.innerText = `${data.vietqr.amount.toLocaleString('vi-VN')} đ`;

        const qrContent = document.getElementById('track-qr-content');
        if (qrContent) qrContent.innerText = data.vietqr.content;
      } else {
        qrBox.classList.add('hidden');
      }
    }

    // Payments history
    const paymentsList = document.getElementById('track-payments-list');
    if (paymentsList) {
      if (!data.payments || data.payments.length === 0) {
        paymentsList.innerHTML = `<div class="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl text-center text-[11px] text-slate-400 italic">Chưa có khoản thanh toán nào được ghi nhận.</div>`;
      } else {
        paymentsList.innerHTML = data.payments.map(p => `
          <div class="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 text-[11px]">
            <div>
              <span class="font-bold text-slate-800 dark:text-slate-200 block">${p.payment_type === 'DEPOSIT' ? 'Thanh toán tiền cọc' : (p.payment_type === 'FULL' ? 'Thanh toán toàn bộ' : (p.payment_type === 'REFUND' ? 'Hoàn tiền' : 'Thanh toán'))}</span>
              <span class="text-[10px] text-slate-400 font-mono">Mã GD: ${p.transaction_code || '---'} • ${p.created_at}</span>
            </div>
            <div class="text-right">
              <span class="font-extrabold text-xs text-emerald-600 dark:text-emerald-400 block">+${p.amount.toLocaleString('vi-VN')} đ</span>
              <span class="text-[10px] text-slate-500">${p.payment_method || 'Chuyển khoản'}</span>
            </div>
          </div>
        `).join('');
      }
    }
  },

  copyTrackQrContent: function() {
    const el = document.getElementById('track-qr-content');
    if (!el) return;
    const text = el.innerText.trim();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      this.showToast(`Đã sao chép cú pháp: "${text}"`, 'success');
    }
  },

  checkMagicTrackUrl: function() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const trackCode = urlParams.get('track_code');
      const token = urlParams.get('token');
      if (trackCode && token) {
        this.loadMagicTrack(trackCode, token);
      }
    } catch (e) {
      console.error('Lỗi kiểm tra URL magic track:', e);
    }
  },


  init: async function() {
    try {
      this.initTheme();
      this.initAuth();
      await this.validateSession();
      this.updateUserUI();
    } catch (e) {
      console.warn("Lỗi khởi tạo giao diện cơ bản:", e);
    }

    if (window.AIHub && !window.AIHub.initialized && typeof window.AIHub.init === 'function') {
      try { window.AIHub.init(); } catch (e) { console.warn("Lỗi khởi tạo AIHub sớm:", e); }
    }

    try {
      await this.fetchInitialData();
    } catch (e) {
      console.warn("Lỗi tải dữ liệu ban đầu:", e);
    }

    try {
      this.setupEventListeners();
      this.initRouter();
      if (typeof this.ensureSearchToolbars === 'function') {
        this.ensureSearchToolbars();
      }
      this.updateUserUI();
      this.renderCurrentView();
      if (this.currentTab === 'guides' || document.getElementById('guides-table-body')) {
        this.renderGuidesTable();
      }
    } catch (e) {
      console.warn("Lỗi khởi tạo router/view:", e);
    }

    if (window.AIHub && !window.AIHub.initialized && typeof window.AIHub.init === 'function') {
      try { window.AIHub.init(); } catch (e) { console.warn("Lỗi khởi tạo AIHub:", e); }
    }
  },

  // ==================== THEME MANAGEMENT ====================
  initTheme: function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const icon = document.getElementById('theme-icon');
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
      if (icon) {
        icon.className = 'fa-solid fa-sun text-amber-400 text-base';
      }
    } else {
      document.documentElement.classList.remove('dark');
      if (icon) {
        icon.className = 'fa-solid fa-moon text-slate-600 text-base';
      }
    }
  },

  toggleTheme: function() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    const icon = document.getElementById('theme-icon');
    if (icon) {
      icon.className = isDark 
        ? 'fa-solid fa-sun text-amber-400 text-base' 
        : 'fa-solid fa-moon text-slate-600 text-base';
    }
    if (this.currentTab === 'analytics' || document.getElementById('analytics-revenue-canvas')) {
      this.renderAnalytics();
    }
  },

  // ==================== AUTHENTICATION & RBAC ====================
  initAuth: function() {
    const savedToken = localStorage.getItem('vietjourney_token');
    const savedUser = localStorage.getItem('vietjourney_user');
    if (savedToken && savedUser) {
      try {
        this.token = savedToken;
        this.currentUser = JSON.parse(savedUser);
      } catch (e) {
        this.token = null;
        this.currentUser = null;
      }
    }
  },

  isLoggedIn: function() {
    return this.currentUser !== null && this.token !== null;
  },

  openModal: function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
    }
    return modal;
  },

  closeModal: function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.querySelectorAll('[data-form-error]').forEach(el => el.remove());
      modal.classList.add('hidden');
      modal.style.removeProperty('display');
    }
    if (modalId === 'login-modal') {
      if (window.location.pathname.toLowerCase() === '/login') {
        const fallback = this.currentTab === 'home' ? '/home' : `/${this.currentTab}`;
        history.replaceState({ tab: this.currentTab }, '', fallback);
        this.updatePageTitle(this.currentTab);
      }
    }
  },

  openLoginModal: function(updateUrl = true) {
    const modal = this.openModal('login-modal');
    const input = document.getElementById('login-username');
    if (input) input.focus();
    if (updateUrl && window.location.pathname !== '/login') {
      history.pushState({ path: '/login' }, '', '/login');
      this.updatePageTitle('login');
    }
  },

  quickLoginDemo: function(username, password) {
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').value = password;
    this.submitLogin();
  },

  submitLogin: async function() {
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value;
    if (!u || !p) {
      alert("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!");
      return;
    }

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Đăng nhập thất bại: " + (err.detail || "Sai thông tin"));
        return;
      }

      const data = await res.json();
      this.token = data.access_token;
      this.currentUser = data.user;
      localStorage.setItem('vietjourney_token', this.token);
      localStorage.setItem('vietjourney_user', JSON.stringify(this.currentUser));

      this.closeModal('login-modal');
      this.showToast(`Xin chào, ${this.currentUser.full_name}! (${this.getRoleBadgeText(this.currentUser.role)})`, 'success');
      this.updateUserUI();
      await this.fetchInitialData();
      if (window.AIHub) window.AIHub.fetchAIStatus();

      // Điều hướng về trang phù hợp sau khi đăng nhập
      const target = (this.currentTab && this.currentTab !== 'login') ? this.currentTab : 'home';
      this.navigate(`/${target}`, true);
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối máy chủ đăng nhập.");
    }
  },

  logout: function() {
    this.token = null;
    this.currentUser = null;
    localStorage.removeItem('vietjourney_token');
    localStorage.removeItem('vietjourney_user');
    const menu = document.getElementById('user-dropdown-menu');
    if (menu) menu.classList.add('hidden');
    this.showToast("Đã đăng xuất khỏi hệ thống. Bạn đang ở chế độ Khách vãng lai.", "info");
    this.updateUserUI();
    if (window.AIHub) window.AIHub.fetchAIStatus();
    this.navigate('/home', true);
    this.fetchInitialData();
  },

  getRoleBadgeText: function(role) {
    switch (role) {
      case 'ADMIN': return 'Quản Trị Viên (Admin)';
      case 'CONSULTANT': return 'Nhân Viên Tư Vấn (Sales)';
      case 'ACCOUNTANT': return 'Kế Toán Viên (Accounting)';
      default: return 'Khách Vãng Lai';
    }
  },

  updateUserUI: function() {
    const isAuth = this.isLoggedIn();
    
    // Topbar Auth
    const topLoginBtn = document.getElementById('topbar-login-btn');
    const topDropdown = document.getElementById('topbar-user-dropdown');
    const topUserName = document.getElementById('topbar-user-name');
    const topUserRole = document.getElementById('topbar-user-role-badge');
    const topUserInitial = document.getElementById('topbar-user-initial');
    const dropdownFullName = document.getElementById('dropdown-full-name');
    const dropdownUsername = document.getElementById('dropdown-username');

    if (isAuth) {
      if (topLoginBtn) topLoginBtn.classList.add('hidden');
      if (topDropdown) topDropdown.classList.remove('hidden');
      if (topUserName) topUserName.innerText = this.currentUser.full_name.split(' ').pop();
      if (topUserRole) topUserRole.innerText = this.currentUser.role;
      if (topUserInitial) topUserInitial.innerText = this.currentUser.full_name.charAt(0);
      if (dropdownFullName) dropdownFullName.innerText = this.currentUser.full_name;
      if (dropdownUsername) dropdownUsername.innerText = `@${this.currentUser.username} • ${this.currentUser.role}`;
    } else {
      if (topLoginBtn) topLoginBtn.classList.remove('hidden');
      if (topDropdown) topDropdown.classList.add('hidden');
    }

    // Sidebar Info
    const sbStatus = document.getElementById('sidebar-auth-status');
    const sbRole = document.getElementById('sidebar-role-name');
    const sbStaffMenu = document.getElementById('sidebar-staff-menu');
    const sbAuthBtnContainer = document.getElementById('sidebar-auth-btn-container');
    const footerName = document.getElementById('footer-user-name');
    const footerRole = document.getElementById('footer-user-role');
    const footerLogout = document.getElementById('footer-logout-btn');

    if (isAuth) {
      if (sbStatus) sbStatus.innerText = "Đã đăng nhập";
      if (sbRole) sbRole.innerText = this.getRoleBadgeText(this.currentUser.role);
      if (sbStaffMenu) sbStaffMenu.classList.remove('hidden');
      if (sbAuthBtnContainer) sbAuthBtnContainer.classList.add('hidden');
      if (footerName) footerName.innerText = this.currentUser.full_name;
      if (footerRole) footerRole.innerText = this.currentUser.role;
      if (footerLogout) footerLogout.classList.remove('hidden');

      // Phân quyền hiển thị theo Role
      const role = this.currentUser.role;
      const isAdmin = (role === 'ADMIN');
      const isConsultant = (role === 'CONSULTANT');
      const isAccountant = (role === 'ACCOUNTANT');

      // Admin-only elements (Tạo/Sửa/Xóa Tour, Lịch khởi hành, HDV, Quản lý tài khoản)
      document.querySelectorAll('.admin-access, .admin-only').forEach(el => {
        el.style.display = isAdmin ? '' : 'none';
      });
      document.querySelectorAll('.consultant-access').forEach(el => {
        el.style.display = (isAdmin || isConsultant) ? '' : 'none';
      });
      document.querySelectorAll('.accountant-access').forEach(el => {
        el.style.display = (isAdmin || isAccountant) ? '' : 'none';
      });
      document.querySelectorAll('.staff-booking-access').forEach(el => {
        el.style.display = (isAdmin || isConsultant || isAccountant) ? '' : 'none';
      });

      // Thành phần thay thế khi không được xem doanh thu (dành cho Khách vãng lai & Tư vấn viên)
      const canViewRevenue = (isAdmin || isAccountant);
      document.querySelectorAll('.non-revenue-access').forEach(el => {
        el.style.display = canViewRevenue ? 'none' : '';
      });

      // Tự động làm mới bảng để ẩn các nút thao tác nghiệp vụ đối với tư vấn viên
      if (document.getElementById('tours-table-body')) this.renderToursTable();
      if (document.getElementById('departures-table-body')) this.renderDeparturesTable();
      if (document.getElementById('guides-table-body')) this.renderGuidesTable();
    } else {
      if (sbStatus) sbStatus.innerText = "Khách vãng lai";
      if (sbRole) sbRole.innerText = "Chưa đăng nhập";
      if (sbStaffMenu) sbStaffMenu.classList.add('hidden');
      if (sbAuthBtnContainer) sbAuthBtnContainer.classList.remove('hidden');
      if (footerName) footerName.innerText = "Khách Vãng Lai";
      if (footerRole) footerRole.innerText = "Khách xem tour";
      if (footerLogout) footerLogout.classList.add('hidden');

      // Ẩn tất cả nút & thành phần cấu hình Admin / Nhân viên đối với khách vãng lai
      document.querySelectorAll('.admin-access, .admin-only').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.consultant-access').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.accountant-access').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.staff-booking-access').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.non-revenue-access').forEach(el => el.style.display = '');

      if (document.getElementById('tours-table-body')) this.renderToursTable();
      if (document.getElementById('departures-table-body')) this.renderDeparturesTable();
      if (document.getElementById('guides-table-body')) this.renderGuidesTable();
    }
  },

  // ==================== DATA FETCHING ====================
  fetchInitialData: async function() {
    const headers = this.token ? { Authorization: `Bearer ${this.token}` } : {};
    const page = location.pathname.replace(/\.html$/, '').split('/').pop() || 'home';
    const jobs = [['tours', '/tours'], ['departures', '/departures'], ['stats', '/stats/dashboard']];
    if (['guides', 'departures', 'home', 'index'].includes(page)) jobs.push(['guides', '/guides']);
    if (['feedbacks', 'ai', 'index'].includes(page)) jobs.push(['feedbacks', '/feedbacks']);
    if (this.isLoggedIn()) {
      jobs.push(['bookings', '/bookings']);
      if (['payments', 'index'].includes(page)) jobs.push(['payments', '/payments']);
      if (this.currentUser.role === 'ADMIN' && ['users', 'index'].includes(page)) jobs.push(['users', '/users']);
    } else { this.bookings = []; this.payments = []; this.users = []; }
    let status = document.getElementById('data-load-status');
    if (!status) { status = document.createElement('div'); status.id = 'data-load-status'; document.querySelector('main')?.prepend(status); }
    status.hidden = false;
    status.setAttribute('role', 'status'); status.textContent = 'Đang tải dữ liệu…';
    const results = await Promise.allSettled(jobs.map(async ([key, url]) => {
      const response = await fetch('/api/v1' + url, { headers });
      if (!response.ok) throw new Error(`${key}: HTTP ${response.status}`);
      const data = await response.json();
      if (key !== 'stats' && !Array.isArray(data)) throw new Error('Dữ liệu không hợp lệ');
      this[key] = data;
    }));
    const failures = results.filter(result => result.status === 'rejected');
    status.hidden = failures.length === 0;
    status.textContent = '';
    if (failures.length) {
      status.className = 'p-3 bg-amber-50 text-amber-900 rounded-lg';
      status.textContent = 'Một phần dữ liệu chưa tải được. Dữ liệu đang hiển thị có thể chưa cập nhật. ';
      const retry = document.createElement('button'); retry.textContent = 'Thử lại'; retry.className = 'underline font-bold';
      retry.onclick = async () => { retry.disabled = true; await this.fetchInitialData(); this.renderCurrentView(); };
      status.append(retry);
    } else status.className = '';
    this.updateStatsCards(); this.populateTourSelects(); this.updateQueueBadge();
  },

  updateStatsCards: function() {
    const rating = document.querySelector('#card-guest-csat p');
    if (rating) rating.textContent = this.stats.average_rating == null ? 'Chưa có đánh giá' : `${this.stats.average_rating} / 5`;
    const canViewRevenue = this.isLoggedIn() && (this.currentUser.role === 'ADMIN' || this.currentUser.role === 'ACCOUNTANT');

    if (document.getElementById('stat-total-tours')) document.getElementById('stat-total-tours').innerText = this.stats.total_tours ?? this.tours.length;
    if (document.getElementById('stat-active-deps')) document.getElementById('stat-active-deps').innerText = this.stats.active_departures || 0;
    
    // Doanh thu chỉ hiển thị cho Admin và Kế toán (Khách vãng lai và Tư vấn viên không được xem)
    if (document.getElementById('stat-total-revenue')) {
      if (canViewRevenue) {
        document.getElementById('stat-total-revenue').innerText = (this.stats.total_revenue || 0).toLocaleString('vi-VN') + ' đ';
      } else {
        document.getElementById('stat-total-revenue').innerText = '0 đ';
      }
    }
    if (document.getElementById('topbar-stat-revenue')) {
      if (canViewRevenue) {
        document.getElementById('topbar-stat-revenue').innerText = (this.stats.total_revenue || 0).toLocaleString('vi-VN') + ' đ';
      } else {
        document.getElementById('topbar-stat-revenue').innerText = '0 đ';
      }
    }
    if (document.getElementById('stat-occupancy')) document.getElementById('stat-occupancy').innerText = (this.stats.average_occupancy_rate || 0) + '%';
  },

  updateQueueBadge: function() {
    const queueItems = this.bookings.filter(b => b.status === 'WAITING_CONFIRM');
    const count = queueItems.length;

    const badge = document.getElementById('sidebar-queue-badge');
    const chip = document.getElementById('queue-counter-chip');
    const summary = document.getElementById('queue-badge-summary');
    const notifDot = document.getElementById('topbar-notif-dot');

    if (badge) {
      badge.innerText = count;
      badge.classList.toggle('hidden', count === 0);
    }
    if (chip) chip.innerText = `${count} đơn`;
    if (summary) summary.innerText = `${count} yêu cầu đang chờ xử lý`;
    if (notifDot) notifDot.classList.toggle('hidden', count === 0);
  },

  populateTourSelects: function() {
    // Populate for Guest booking modal
    const guestDepSelect = document.getElementById('guest-dep-select');
    if (guestDepSelect) {
      let gHtml = '';
      const openDeps = this.departures.filter(d => d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA'));
      if (openDeps.length === 0) {
        gHtml = '<option value="">-- Tạm thời chưa có lịch mở --</option>';
      } else {
        gHtml = openDeps.map(d => `
          <option value="${d.id}">[${d.tour_code || d.tour_id}] ${d.tour_title || 'Tour'} (Khởi hành: ${d.departure_date} - Còn ${d.available_slots} chỗ)</option>
        `).join('');
      }
      guestDepSelect.innerHTML = gHtml;
    }

    const aiFeedbackSelect = document.getElementById('ai-feedback-tour-select');
    if (aiFeedbackSelect) {
      let html = '<option value="">-- Tất cả các tour --</option>';
      this.tours.forEach(t => {
        html += `<option value="${t.id}">[${t.code}] ${t.title}</option>`;
      });
      aiFeedbackSelect.innerHTML = html;
    }
  },

  // ==================== TABS & VIEW ROUTING ====================
  initRouter: function() {
    window.addEventListener('popstate', (e) => {
      this.handleRoute(window.location.pathname, false);
    });
    this.handleRoute(window.location.pathname, true);
  },

  handleRoute: function(pathname, isInitial = false) {
    let cleanPath = (pathname || '/').toLowerCase().trim();
    if (cleanPath.endsWith('/') && cleanPath.length > 1) {
      cleanPath = cleanPath.slice(0, -1);
    }
    if (cleanPath.endsWith('.html')) {
      cleanPath = cleanPath.slice(0, -5);
    }

    const pathParts = cleanPath.split('/');
    const lastSegment = pathParts[pathParts.length - 1] || 'home';

    if (cleanPath === '/login' || lastSegment === 'login') {
      if (!document.getElementById('view-home')) { window.location.assign('/login'); return; }
      this.switchTab('home', false);
      this.openLoginModal(false);
      this.updatePageTitle('login');
      return;
    }

    // Đóng login modal nếu đang mở khi chuyển sang trang khác
    const loginModal = document.getElementById('login-modal');
    if (loginModal && !loginModal.classList.contains('hidden')) {
      loginModal.classList.add('hidden');
    }

    const routeMap = {
      '': 'home',
      '/': 'home',
      '/home': 'home',
      '/index': 'home',
      '/ai': 'ai',
      '/queue': 'queue',
      '/tours': 'tours',
      '/departures': 'departures',
      '/bookings': 'bookings',
      '/payments': 'payments',
      '/guides': 'guides',
      '/feedbacks': 'feedbacks',
      '/analytics': 'analytics',
      '/users': 'users',
      '/sdlc': 'sdlc'
    };

    // Kiểm tra xem trang hiện tại chỉ có 1 view độc lập (standalone page)
    const singleViews = document.querySelectorAll('.tab-content-view');
    let pageTab = null;
    if (singleViews.length === 1 && singleViews[0].id && singleViews[0].id.startsWith('view-')) {
      pageTab = singleViews[0].id.replace('view-', '');
    }

    const targetTab = routeMap[cleanPath] || routeMap['/' + lastSegment] || pageTab || 'home';
    this.switchTab(targetTab, false);
    this.updatePageTitle(targetTab);

    if (isInitial && cleanPath !== `/${targetTab}` && cleanPath !== '/login' && !pathname.includes('.html')) {
      history.replaceState({ tab: targetTab }, '', `/${targetTab}`);
    }
  },

  navigate: function(path, replace = false) {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const pageView = document.querySelectorAll('.tab-content-view');
    const requestedTab = cleanPath.split('/').filter(Boolean).pop() || 'home';
    if (pageView.length === 1 && pageView[0].id !== `view-${requestedTab}` && requestedTab !== 'login') {
      if (replace) window.location.replace(cleanPath);
      else window.location.assign(cleanPath);
      return;
    }
    if (replace) {
      history.replaceState({ path: cleanPath }, '', cleanPath);
    } else {
      history.pushState({ path: cleanPath }, '', cleanPath);
    }
    this.handleRoute(cleanPath, false);
  },

  updatePageTitle: function(tabOrRoute) {
    const titleMap = {
      'home': 'Trang chủ | VietJourney AI',
      'login': 'Đăng nhập hệ thống | VietJourney AI',
      'ai': 'AI Hub & Trợ lý điều hành | VietJourney AI',
      'queue': 'Hàng đợi duyệt đơn | VietJourney AI',
      'tours': 'Quản lý Sản phẩm Tour | VietJourney AI',
      'departures': 'Lịch khởi hành & Ghế | VietJourney AI',
      'bookings': 'Quản lý Đặt tour | VietJourney AI',
      'payments': 'Thanh toán & Công nợ | VietJourney AI',
      'guides': 'Hướng dẫn viên & Điểm số | VietJourney AI',
      'feedbacks': 'Ý kiến & Khảo sát CSAT | VietJourney AI',
      'analytics': 'Báo cáo doanh thu & Vận hành | VietJourney AI',
      'users': 'Quản lý người dùng & Phân quyền | VietJourney AI',
      'sdlc': 'Hồ sơ Tài liệu & SDLC | VietJourney AI'
    };
    document.title = titleMap[tabOrRoute] || 'VietJourney AI - Nền tảng Du lịch Thông minh';
  },

  switchTab: function(tabName, updateUrl = true) {
    // Bảo vệ tab nội bộ nếu chưa đăng nhập
    if (tabName === 'users' && this.currentUser?.role !== 'ADMIN') { this.showToast('Bạn không có quyền quản lý tài khoản.', 'error'); this.navigate('/home', true); return; }
    const staffTabs = ['queue', 'tours', 'departures', 'bookings', 'payments', 'feedbacks', 'analytics', 'users'];
    if (staffTabs.includes(tabName) && !this.isLoggedIn()) {
      this.showToast("Vui lòng đăng nhập để truy cập khu vực quản lý nghiệp vụ!", "error");
      this.openLoginModal(true);
      return;
    }

    // Bảo vệ tab Doanh thu & Kế toán: Chỉ Admin và Kế toán được xem (Khách vãng lai & Tư vấn viên không được xem)
    if (['analytics', 'payments'].includes(tabName)) {
      const isFinRole = this.isLoggedIn() && (this.currentUser.role === 'ADMIN' || this.currentUser.role === 'ACCOUNTANT');
      if (!isFinRole) {
        this.showToast("Chỉ Quản lý (Admin) và Kế toán mới có quyền truy cập dữ liệu Doanh thu & Kế toán!", "error");
        if (window.location.pathname.includes('analytics') || window.location.pathname.includes('payments')) {
          this.navigate('/home', true);
        }
        return;
      }
    }

    this.currentTab = tabName;

    const targetView = document.getElementById(`view-${tabName}`);
    if (!targetView) {
      // Nếu view mục tiêu không có trên trang HTML hiện tại (do cấu trúc trang độc lập), điều hướng tới trang tương ứng
      const targetUrl = tabName === 'home' ? '/home' : `/${tabName}`;
      window.location.href = targetUrl;
      return;
    }

    // Ẩn tất cả views có trong trang hiện tại
    document.querySelectorAll('.tab-content-view').forEach(v => v.classList.add('hidden'));

    // Hiển thị view mục tiêu
    targetView.classList.remove('hidden');

    // Cập nhật style trên sidebar
    document.querySelectorAll('.sidebar-nav-item').forEach(item => {
      if (item.dataset.tab === tabName) {
        item.classList.add('bg-sky-600', 'text-white', 'shadow-sm');
        item.classList.remove('text-slate-600', 'dark:text-slate-300', 'hover:bg-slate-100', 'dark:hover:bg-slate-800');
      } else {
        item.classList.remove('bg-sky-600', 'text-white', 'shadow-sm');
        item.classList.add('text-slate-600', 'dark:text-slate-300', 'hover:bg-slate-100', 'dark:hover:bg-slate-800');
      }
    });

    if (updateUrl) {
      const newUrl = `/${tabName}`;
      if (window.location.pathname !== newUrl && !window.location.pathname.endsWith(`${tabName}.html`)) {
        history.pushState({ tab: tabName }, '', newUrl);
      }
      this.updatePageTitle(tabName);
    }

    this.renderCurrentView();
  },

  setCategoryFilter: function(cat) {
    this.currentCategory = cat;
    document.querySelectorAll('.category-tab-btn').forEach(btn => {
      if (btn.dataset.category === cat) {
        btn.classList.add('active', 'bg-sky-600', 'text-white');
        btn.classList.remove('bg-slate-200', 'dark:bg-slate-800');
      } else {
        btn.classList.remove('active', 'bg-sky-600', 'text-white');
        btn.classList.add('bg-slate-200', 'dark:bg-slate-800');
      }
    });
    this.renderTourCards();
  },

  renderCurrentView: function() {
    this.ensureSearchToolbars();

    switch (this.currentTab) {
      case 'home':
        this.renderTourCards();
        break;
      case 'queue':
        this.renderQueueTable();
        break;
      case 'users':
        this.renderUsersTable();
        break;
      case 'tours':
        this.renderToursTable();
        break;
      case 'departures':
        this.renderDeparturesTable();
        break;
      case 'bookings':
        this.renderBookingsTable();
        break;
      case 'payments':
        this.renderPaymentsTable();
        break;
      case 'guides':
        this.renderGuidesTable();
        break;
      case 'feedbacks':
        this.renderFeedbacksList();
        break;
      case 'analytics':
        this.renderAnalytics();
        break;
    }
  },

  ensureSearchToolbars: function() {
    // 1. Tours Toolbar
    const toursView = document.getElementById('view-tours');
    if (toursView && !document.getElementById('tours-search-toolbar')) {
      const targetTableBox = toursView.querySelector('table')?.closest('.bg-white, .rounded-2xl') || toursView.querySelector('table')?.parentElement?.parentElement;
      if (targetTableBox) {
        const tb = document.createElement('div');
        tb.id = 'tours-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="tour-search-keyword" data-action="onTourSearchChange" data-event="input" data-args="" placeholder="Tìm theo mã tour, tên tour, điểm đến, điểm nổi bật..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select id="tour-filter-category" data-action="onTourSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Tất cả danh mục</option>
                <option value="MIEN_BAC">Miền Bắc</option>
                <option value="MIEN_TRUNG">Miền Trung</option>
                <option value="MIEN_NAM">Miền Nam</option>
                <option value="BIEN_DAO">Biển Đảo</option>
                <option value="NUI_RUNG">Núi Rừng</option>
                <option value="NGHI_DUONG">Nghỉ Dưỡng</option>
              </select>
              <select id="tour-filter-price" data-action="onTourSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi mức giá</option>
                <option value="UNDER_3M">&lt; 3.000.000 đ</option>
                <option value="3M_7M">3.000.000 - 7.000.000 đ</option>
                <option value="OVER_7M">&gt; 7.000.000 đ</option>
              </select>
              <select id="tour-filter-status" data-action="onTourSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Tất cả trạng thái</option>
                <option value="ACTIVE">Đang mở bán</option>
                <option value="INACTIVE">Tạm dừng</option>
              </select>
              <button data-action="resetTourFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Đặt lại bộ lọc">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
              <span id="tours-count-display" class="px-2.5 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-300 font-bold text-[11px] whitespace-nowrap">
                Hiển thị 0 tour
              </span>
            </div>
          </div>
        `;
        targetTableBox.parentElement.insertBefore(tb, targetTableBox);
      }
    }

    // 2. Departures Toolbar
    const depsView = document.getElementById('view-departures');
    if (depsView && !document.getElementById('departures-search-toolbar')) {
      const targetTableBox = depsView.querySelector('table')?.closest('.bg-white, .rounded-2xl') || depsView.querySelector('table')?.parentElement?.parentElement;
      if (targetTableBox) {
        const tb = document.createElement('div');
        tb.id = 'departures-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="dep-search-keyword" data-action="onDepartureSearchChange" data-event="input" data-args="" placeholder="Tìm theo mã tour, tên tour, điểm đến, HDV, ghi chú..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select id="dep-filter-status" data-action="onDepartureSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Tất cả trạng thái</option>
                <option value="OPEN">Mở bán (Đang nhận khách)</option>
                <option value="RUNNING">Đang chạy tour (On Tour)</option>
                <option value="COMPLETED">Đã hoàn thành</option>
                <option value="CANCELLED">Đã hủy</option>
              </select>
              <select id="dep-filter-guide" data-action="onDepartureSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Tất cả hướng dẫn viên</option>
              </select>
              <button data-action="resetDepartureFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Đặt lại bộ lọc">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
              <span id="departures-count-display" class="px-2.5 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-300 font-bold text-[11px] whitespace-nowrap">
                Hiển thị 0 đợt
              </span>
            </div>
          </div>
        `;
        targetTableBox.parentElement.insertBefore(tb, targetTableBox);
        this.populateDepartureGuideOptions();
      }
    }

    // 3. Bookings Toolbar
    const bookingsView = document.getElementById('view-bookings');
    if (bookingsView && !document.getElementById('bookings-search-toolbar')) {
      const targetTableBox = bookingsView.querySelector('table')?.closest('.bg-white, .rounded-2xl') || bookingsView.querySelector('table')?.parentElement?.parentElement;
      if (targetTableBox) {
        const tb = document.createElement('div');
        tb.id = 'bookings-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="booking-search-keyword" data-action="onBookingSearchChange" data-event="input" data-args="" placeholder="Tìm theo mã đơn (BK-...), tên khách, số điện thoại, tên tour..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select id="booking-filter-status" data-action="onBookingSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Tất cả trạng thái</option>
                <option value="CONFIRMED">Xác nhận đủ</option>
                <option value="DEPOSITED">Đã cọc 30%</option>
                <option value="PENDING">Chờ thanh toán</option>
                <option value="CANCELLED">Đã hủy</option>
              </select>
              <select id="booking-filter-payment" data-action="onBookingSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi trạng thái thanh toán</option>
                <option value="UNPAID">Chưa thanh toán (0 đ)</option>
                <option value="PARTIAL">Đã cọc một phần</option>
                <option value="PAID">Đã thanh toán đủ 100%</option>
              </select>
              <button data-action="resetBookingFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Đặt lại bộ lọc">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
              <span id="bookings-count-display" class="px-2.5 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-300 font-bold text-[11px] whitespace-nowrap">
                Hiển thị 0 đơn
              </span>
            </div>
          </div>
        `;
        targetTableBox.parentElement.insertBefore(tb, targetTableBox);
      }
    }

    // 4. Queue Toolbar
    const queueView = document.getElementById('view-queue');
    if (queueView && !document.getElementById('queue-search-toolbar')) {
      const targetTableBox = queueView.querySelector('table')?.closest('.bg-white, .rounded-2xl') || queueView.querySelector('table')?.parentElement?.parentElement;
      if (targetTableBox) {
        const tb = document.createElement('div');
        tb.id = 'queue-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="queue-search-keyword" data-action="onQueueSearchChange" data-event="input" data-args="" placeholder="Tìm theo mã yêu cầu, họ tên khách, số điện thoại, tour đăng ký..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500" />
            </div>
            <div class="flex items-center space-x-2">
              <button data-action="resetQueueFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
            </div>
          </div>
        `;
        targetTableBox.parentElement.insertBefore(tb, targetTableBox);
      }
    }

    // 5. Payments Toolbar
    const paymentsView = document.getElementById('view-payments');
    if (paymentsView && !document.getElementById('payments-search-toolbar')) {
      const targetTableBox = paymentsView.querySelector('table')?.closest('.bg-white, .rounded-2xl') || paymentsView.querySelector('table')?.parentElement?.parentElement;
      if (targetTableBox) {
        const tb = document.createElement('div');
        tb.id = 'payments-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="payment-search-keyword" data-action="onPaymentSearchChange" data-event="input" data-args="" placeholder="Tìm theo mã giao dịch (TXN-...), mã booking, người lập, ghi chú..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select id="payment-filter-type" data-action="onPaymentSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi loại phiếu thu/chi</option>
                <option value="DEPOSIT">Đặt cọc</option>
                <option value="FINAL">Thanh toán đợt cuối</option>
                <option value="FULL">Toàn bộ</option>
                <option value="REFUND">Hoàn tiền hủy tour</option>
              </select>
              <select id="payment-filter-method" data-action="onPaymentSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi phương thức</option>
                <option value="BANK_TRANSFER">Chuyển khoản NH</option>
                <option value="CASH">Tiền mặt</option>
                <option value="CREDIT_CARD">Thẻ quốc tế</option>
                <option value="MOMO">Ví MoMo</option>
              </select>
              <button data-action="resetPaymentFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
              <span id="payments-count-display" class="px-2.5 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-300 font-bold text-[11px] whitespace-nowrap">
                Hiển thị 0 giao dịch
              </span>
            </div>
          </div>
        `;
        targetTableBox.parentElement.insertBefore(tb, targetTableBox);
      }
    }

    // 6. Feedbacks Toolbar
    const feedbacksView = document.getElementById('view-feedbacks');
    if (feedbacksView && !document.getElementById('feedbacks-search-toolbar')) {
      const streamList = document.getElementById('feedbacks-stream-list');
      if (streamList) {
        const tb = document.createElement('div');
        tb.id = 'feedbacks-search-toolbar';
        tb.className = 'bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm space-y-2.5 text-xs mb-3';
        tb.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2.5">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <i class="fa-solid fa-magnifying-glass text-xs"></i>
              </span>
              <input type="text" id="feedback-search-keyword" data-action="onFeedbackSearchChange" data-event="input" data-args="" placeholder="Tìm theo tên khách hàng, nội dung nhận xét, tên tour..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select id="feedback-filter-sentiment" data-action="onFeedbackSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi cảm xúc</option>
                <option value="POSITIVE">Tích cực (Hài lòng)</option>
                <option value="NEUTRAL">Trung tính</option>
                <option value="NEGATIVE">Tiêu cực (Góp ý)</option>
              </select>
              <select id="feedback-filter-rating" data-action="onFeedbackSearchChange" data-event="change" data-args="" class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-700 dark:text-slate-200 focus:outline-none">
                <option value="ALL">Mọi số sao</option>
                <option value="5">5 sao</option>
                <option value="4">4 sao</option>
                <option value="3">3 sao</option>
                <option value="2">2 sao</option>
                <option value="1">1 sao</option>
              </select>
              <button data-action="resetFeedbackFilters" data-event="click" data-args="" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <i class="fa-solid fa-rotate-left mr-1"></i> Đặt lại
              </button>
              <span id="feedbacks-count-display" class="px-2.5 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-300 font-bold text-[11px] whitespace-nowrap">
                Hiển thị 0 phản hồi
              </span>
            </div>
          </div>
        `;
        streamList.parentElement.insertBefore(tb, streamList);
      }
    }
  },

  // ==================== RENDERING LOGIC ====================
  renderTourCards: function() {
    const container = document.getElementById('tour-cards-grid');
    if (!container) return;

    let filtered = this.tours.filter(t => t.is_active);
    if (this.currentCategory !== 'ALL') {
      filtered = filtered.filter(t => t.category === this.currentCategory);
    }
    if (this.homeTourKeyword && this.homeTourKeyword.trim() !== '') {
      const kw = this.homeTourKeyword.trim().toLowerCase();
      filtered = filtered.filter(t => 
        (t.title && t.title.toLowerCase().includes(kw)) ||
        (t.code && t.code.toLowerCase().includes(kw)) ||
        (t.destination && t.destination.toLowerCase().includes(kw)) ||
        (t.highlights && t.highlights.toLowerCase().includes(kw)) ||
        (t.description && t.description.toLowerCase().includes(kw))
      );
    }

    const countBadge = document.getElementById('home-tour-count-badge');
    if (countBadge) {
      countBadge.innerText = `Hiển thị ${filtered.length} / ${this.tours.filter(t => t.is_active).length} tour`;
    }

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="col-span-full text-center py-12 text-slate-400">
          <p class="text-base">Không có tour nào trong danh mục này.</p>
        </div>
      `;
      return;
    }

    const isAuth = this.isLoggedIn();

    container.innerHTML = filtered.map(t => {
      const deps = this.departures.filter(d => d.tour_id === t.id && d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA'));
      const totalAvailable = deps.reduce((sum, d) => sum + d.available_slots, 0);
      const nearestDep = deps.length > 0 ? deps[0] : null;

      const badgeColor = t.category === 'BIEN_DAO' ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' :
                         t.category === 'TAY_BAC' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
                         t.category === 'MIEN_TAY' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                         'bg-purple-500/20 text-purple-400 border-purple-500/30';

      const slotBadgeColor = totalAvailable > 5 ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                             totalAvailable > 0 ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                             'bg-rose-500/10 text-rose-500 border-rose-500/20';

      return `
        <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col group">
          <div class="relative h-44 overflow-hidden">
            <img src="${t.image_url || 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=600&q=80'}" 
                 alt="${t.title}" 
                 class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
            <span class="absolute top-3 left-3 border text-[11px] font-bold px-2.5 py-1 rounded-lg backdrop-blur-md ${badgeColor}">
              ${t.destination} • ${t.duration_days}N${t.duration_nights}Đ
            </span>
            <span class="absolute top-3 right-3 text-[10px] font-mono bg-black/60 text-slate-200 px-2 py-0.5 rounded backdrop-blur-md">
              ${t.code}
            </span>
            <div class="absolute bottom-3 left-3 right-3 flex justify-between items-end text-white">
              <div>
                <span class="text-xs text-slate-300">Giá trọn gói từ</span>
                <p class="text-lg font-extrabold text-sky-400">${t.base_price.toLocaleString('vi-VN')} đ</p>
              </div>
              <span class="text-xs border px-2 py-0.5 rounded-lg ${slotBadgeColor} backdrop-blur-md">
                ${totalAvailable > 0 ? `Còn ${totalAvailable} chỗ` : 'Hết chỗ'}
              </span>
            </div>
          </div>
          
          <div class="p-4 flex-1 flex flex-col justify-between">
            <div>
              <h3 class="font-bold text-slate-900 dark:text-slate-100 text-sm leading-snug line-clamp-2 hover:text-sky-600 transition-colors">
                ${t.title}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2">
                ${t.description || t.highlights || 'Khám phá vẻ đẹp tuyệt mỹ, dịch vụ trọn gói tiêu chuẩn cao.'}
              </p>
              ${nearestDep ? `
                <div class="mt-3 text-[11px] text-slate-600 dark:text-slate-300 flex items-center bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 rounded-lg border border-slate-100 dark:border-slate-800">
                  <i class="fa-regular fa-calendar text-sky-500 mr-1.5"></i> Khởi hành gần nhất: <strong class="ml-1 text-slate-800 dark:text-slate-100">${nearestDep.departure_date}</strong>
                </div>
              ` : `
                <div class="mt-3 text-[11px] text-slate-400 italic">Chưa có lịch khởi hành mở</div>
              `}
            </div>
            
            <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
              <button data-action="openTourDetailsModal" data-event="click" data-args="${t.id}" class="text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-sky-600 px-3 py-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                Chi tiết & Lịch trình
              </button>
              
              <!-- Nút hành động: Nếu là khách thì Đăng ký tư vấn; nếu là nhân viên thì Đặt chỗ trực tiếp -->
              <button data-action="${isAuth ? "openBookingModalForTour" : "openGuestBookingModalForTour"}" data-event="click" data-args="${t.id}" 
                      ${totalAvailable === 0 ? 'disabled' : ''} 
                      class="text-xs font-bold px-4 py-2 rounded-xl transition-all shadow-sm ${
                        totalAvailable > 0 
                        ? (isAuth ? 'bg-sky-600 hover:bg-sky-700 text-white' : 'bg-emerald-600 hover:bg-emerald-700 text-white') 
                        : 'bg-slate-200 dark:bg-slate-800 text-slate-400 cursor-not-allowed'
                      }">
                ${totalAvailable > 0 ? (isAuth ? 'Đặt & Giữ Chỗ' : 'Đăng Ký Tư Vấn') : 'Đã Kín Chỗ'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  // RENDER HÀNG CHỜ TƯ VẤN (WAITING QUEUE)
  renderQueueTable: function() {
    const tbody = document.getElementById('queue-table-body');
    if (!tbody) return;

    let queueItems = this.bookings.filter(b => b.status === 'WAITING_CONFIRM');

    if (this.queueSearchKeyword) {
      const kw = this.queueSearchKeyword.toLowerCase().trim();
      queueItems = queueItems.filter(b =>
        (b.booking_code && b.booking_code.toLowerCase().includes(kw)) ||
        (b.customer_name && b.customer_name.toLowerCase().includes(kw)) ||
        (b.customer_phone && b.customer_phone.toLowerCase().includes(kw)) ||
        (b.tour_title && b.tour_title.toLowerCase().includes(kw)) ||
        (b.special_requests && b.special_requests.toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('queue-count-display');
    if (countEl) countEl.innerText = `${queueItems.length} yêu cầu chờ xử lý`;

    if (queueItems.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center py-10 text-slate-400 italic">
            Hiện không có yêu cầu nào phù hợp trong hàng chờ tư vấn.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = queueItems.map(b => `
      <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
        <td class="py-3 px-4 font-mono font-bold text-amber-600 dark:text-amber-400">${b.booking_code}</td>
        <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-100">
          ${b.customer_name || 'Khách'}
          <span class="block text-[10px] text-slate-500 font-normal">${b.customer_phone || ''}</span>
        </td>
        <td class="py-3 px-4 text-slate-700 dark:text-slate-300">
          ${b.tour_title || 'Tour'}
          <span class="block text-[10px] text-sky-600 dark:text-sky-400 font-medium">Ngày đi: ${b.departure_date || 'Chưa định'}</span>
        </td>
        <td class="py-3 px-4 text-center font-bold text-slate-800 dark:text-slate-100">${b.num_people}</td>
        <td class="py-3 px-4 font-bold text-emerald-600 dark:text-emerald-400">${b.total_amount.toLocaleString('vi-VN')} đ</td>
        <td class="py-3 px-4 text-[11px] text-slate-500 dark:text-slate-400 max-w-[180px] truncate" title="${b.special_requests || ''}">${b.special_requests || 'Không có'}</td>
        <td class="py-3 px-4 text-[10px] text-slate-400">${new Date(b.created_at).toLocaleDateString('vi-VN')}</td>
        <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
          <button data-action="openConfirmBookingModal" data-event="click" data-args="${b.id}" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-2.5 py-1 rounded-lg text-xs shadow-sm">
            <i class="fa-solid fa-check mr-1"></i> Xác Nhận Giữ Chỗ
          </button>
          <button data-action="promptRejectBooking" data-event="click" data-args="${b.id}" class="bg-rose-50 text-rose-600 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-400 font-semibold px-2 py-1 rounded-lg text-xs">
            Từ chối
          </button>
        </td>
      </tr>
    `).join('');
  },

  // RENDER QUẢN LÝ TÀI KHOẢN (ADMIN ONLY)
  renderUsersTable: function() {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;

    if (this.users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">Đang tải danh sách tài khoản...</td></tr>`;
      return;
    }

    tbody.innerHTML = this.users.map(u => {
      const roleBadge = u.role === 'ADMIN' ? '<span class="bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300 px-2 py-0.5 rounded font-bold text-[10px]">ADMIN</span>' :
                        u.role === 'CONSULTANT' ? '<span class="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300 px-2 py-0.5 rounded font-bold text-[10px]">TƯ VẤN (SALES)</span>' :
                        '<span class="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300 px-2 py-0.5 rounded font-bold text-[10px]">KẾ TOÁN</span>';

      return `
        <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
          <td class="py-3 px-4 font-mono text-slate-400">#${u.id}</td>
          <td class="py-3 px-4 font-mono font-bold text-slate-800 dark:text-slate-200">@${u.username}</td>
          <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-100">${u.full_name}</td>
          <td class="py-3 px-4">${roleBadge}</td>
          <td class="py-3 px-4 text-slate-500">${u.email || '-'}</td>
          <td class="py-3 px-4 text-slate-500">${u.phone || '-'}</td>
          <td class="py-3 px-4">
            <span class="text-[10px] font-bold ${u.is_active ? 'text-emerald-500' : 'text-rose-500'}">
              ${u.is_active ? '● Đang hoạt động' : '○ Đã khóa'}
            </span>
          </td>
          <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
            <button data-action="openEditUserModal" data-event="click" data-args="${u.id}" class="text-sky-600 hover:text-sky-700 font-bold text-xs">Sửa & Phân quyền</button>
            ${u.username !== 'admin' ? `
              <button data-action="deleteUser" data-event="click" data-args="${u.id}" class="text-rose-600 hover:text-rose-700 font-bold text-xs ml-2">Xóa</button>
            ` : ''}
          </td>
        </tr>
      `;
    }).join('');
  },

  renderToursTable: function() {
    const tbody = document.getElementById('tours-table-body');
    if (!tbody) return;

    const isAdmin = this.currentUser && this.currentUser.role === 'ADMIN';

    // Áp dụng bộ lọc đa trường
    let list = this.tours;
    if (this.tourCategoryFilter && this.tourCategoryFilter !== 'ALL') {
      list = list.filter(t => t.category === this.tourCategoryFilter);
    }
    if (this.tourStatusFilter && this.tourStatusFilter !== 'ALL') {
      const active = (this.tourStatusFilter === 'ACTIVE');
      list = list.filter(t => t.is_active === active);
    }
    if (this.tourPriceFilter && this.tourPriceFilter !== 'ALL') {
      if (this.tourPriceFilter === 'UNDER_3M') list = list.filter(t => t.base_price < 3000000);
      else if (this.tourPriceFilter === '3M_7M') list = list.filter(t => t.base_price >= 3000000 && t.base_price <= 7000000);
      else if (this.tourPriceFilter === 'OVER_7M') list = list.filter(t => t.base_price > 7000000);
    }
    if (this.tourSearchKeyword) {
      const kw = this.tourSearchKeyword.toLowerCase().trim();
      list = list.filter(t =>
        (t.code && t.code.toLowerCase().includes(kw)) ||
        (t.title && t.title.toLowerCase().includes(kw)) ||
        (t.destination && t.destination.toLowerCase().includes(kw)) ||
        (t.highlights && t.highlights.toLowerCase().includes(kw)) ||
        (t.description && t.description.toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('tours-count-display');
    if (countEl) countEl.innerText = `Hiển thị ${list.length} / ${this.tours.length} tour`;

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">Không tìm thấy tour nào phù hợp với bộ lọc tìm kiếm.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(t => `
      <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
        <td class="py-3 px-4 font-mono font-bold text-xs text-sky-600 dark:text-sky-400">${t.code}</td>
        <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-100 text-sm">${t.title}</td>
        <td class="py-3 px-4 text-xs text-slate-600 dark:text-slate-300">${t.destination}</td>
        <td class="py-3 px-4 text-xs font-bold text-slate-700 dark:text-slate-300">${t.duration_days}N${t.duration_nights}Đ</td>
        <td class="py-3 px-4 text-xs font-bold text-emerald-600 dark:text-emerald-400">${t.base_price.toLocaleString('vi-VN')} đ</td>
        <td class="py-3 px-4">
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${t.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300' : 'bg-slate-100 text-slate-500'}">
            ${t.is_active ? 'Đang mở' : 'Tạm dừng'}
          </span>
        </td>
        <td class="py-3 px-4 text-right space-x-2">
          ${isAdmin ? `
            <button data-action="openAddDepartureModal" data-event="click" data-args="${t.id}" class="text-xs bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 font-bold px-2 py-1 rounded-lg transition-colors" title="Mở đợt khởi hành và phân công HDV cho tour này">
              <i class="fa-solid fa-calendar-plus mr-1"></i>Mở lịch & HDV
            </button>
          ` : ''}
          <button data-action="openTourDetailsModal" data-event="click" data-args="${t.id}" class="text-xs text-sky-600 hover:text-sky-700 font-medium">Xem</button>
          ${isAdmin ? `
            <button data-action="deleteTour" data-event="click" data-args="${t.id}" class="text-xs text-rose-600 hover:text-rose-700 font-medium">Xóa</button>
          ` : ''}
        </td>
      </tr>
    `).join('');
  },

  renderDeparturesTable: function() {
    const tbody = document.getElementById('departures-table-body');
    if (!tbody) return;

    const isAdmin = this.currentUser && this.currentUser.role === 'ADMIN';

    // Áp dụng bộ lọc đa trường
    let list = this.departures;
    if (this.departureStatusFilter && this.departureStatusFilter !== 'ALL') {
      list = list.filter(d => d.status === this.departureStatusFilter);
    }
    if (this.departureGuideFilter && this.departureGuideFilter !== 'ALL') {
      list = list.filter(d => d.guide_id === parseInt(this.departureGuideFilter));
    }
    if (this.departureFromDate) {
      list = list.filter(d => d.departure_date >= this.departureFromDate);
    }
    if (this.departureToDate) {
      list = list.filter(d => d.departure_date <= this.departureToDate);
    }
    if (this.departureSearchKeyword) {
      const kw = this.departureSearchKeyword.toLowerCase().trim();
      list = list.filter(d =>
        (d.tour_code && d.tour_code.toLowerCase().includes(kw)) ||
        (d.tour_title && d.tour_title.toLowerCase().includes(kw)) ||
        (d.guide_name && d.guide_name.toLowerCase().includes(kw)) ||
        (d.notes && d.notes.toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('departures-count-display');
    if (countEl) countEl.innerText = `Hiển thị ${list.length} / ${this.departures.length} đợt khởi hành`;

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">Không tìm thấy đợt khởi hành nào phù hợp với bộ lọc tìm kiếm.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(d => {
      const booked = d.total_slots - d.available_slots;
      const percent = Math.round((booked / d.total_slots) * 100);

      const statusBadge = d.status === 'RUNNING' ?
        '<span class="bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 border border-amber-400 dark:border-amber-600 px-2 py-0.5 rounded text-[10px] font-bold flex items-center space-x-1.5 w-fit"><span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></span><span>Đang khởi hành</span></span>' :
        d.status === 'COMPLETED' ?
        '<span class="bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 px-2 py-0.5 rounded text-[10px] font-bold">Hoàn thành</span>' :
        d.status === 'CANCELLED' ?
        '<span class="bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300 px-2 py-0.5 rounded text-[10px] font-bold">Đã hủy</span>' :
        d.status === 'FULL' ?
        '<span class="bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300 px-2 py-0.5 rounded text-[10px] font-bold">Hết chỗ</span>' :
        '<span class="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300 px-2 py-0.5 rounded text-[10px] font-bold">Mở bán</span>';

      // Nút hành động: Khởi hành / Hoàn thành (Chỉ dành cho ADMIN)
      let actionButtons = '';
      if (isAdmin) {
        if (d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA') || d.status === 'FULL') {
          actionButtons += `
            <button data-action="startDeparture" data-event="click" data-args="${d.id}" class="text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-2.5 py-1 rounded-lg transition-all shadow-sm flex items-center space-x-1" title="Khởi động chuyến đi">
              <i class="fa-solid fa-plane-departure text-[11px]"></i>
              <span>Khởi hành</span>
            </button>
          `;
        } else if (d.status === 'RUNNING') {
          actionButtons += `
            <button data-action="completeDeparture" data-event="click" data-args="${d.id}" class="text-xs bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-2.5 py-1 rounded-lg transition-all shadow-sm flex items-center space-x-1" title="Kết thúc tour">
              <i class="fa-solid fa-flag-checkered text-[11px]"></i>
              <span>Kết thúc</span>
            </button>
          `;
        }
      }

      // Nút xem DS Khách & Liên hệ khẩn cấp
      actionButtons += `
        <button data-action="openDepartureCustomersModal" data-event="click" data-args="${d.id}" class="text-xs bg-amber-50 hover:bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 font-bold px-2 py-1 rounded-lg transition-colors flex items-center space-x-1" title="Xem danh sách khách hàng & liên hệ hủy chuyến khẩn cấp">
          <i class="fa-solid fa-users text-[11px]"></i>
          <span>Khách (${d.total_slots - d.available_slots})</span>
        </button>
      `;

      // Nút Đặt chỗ (Cả Admin và Tư vấn viên đều được đặt chỗ cho khách)
      if (d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA')) {
        actionButtons += `
          <button data-action="openBookingModalForDep" data-event="click" data-args="${d.id}" ${d.available_slots === 0 ? 'disabled' : ''} class="text-xs bg-sky-600 hover:bg-sky-700 text-white font-medium px-2 py-1 rounded-lg transition-colors disabled:bg-slate-300" title="Đặt chỗ trực tiếp">
            Đặt chỗ
          </button>
        `;
      }

      // Sửa & Xóa chỉ dành cho ADMIN
      if (isAdmin) {
        actionButtons += `
          <button data-action="openEditDepartureModal" data-event="click" data-args="${d.id}" class="text-xs text-slate-600 hover:text-sky-600 dark:text-slate-300 p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" title="Sửa thông tin / Đổi HDV">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button data-action="deleteDeparture" data-event="click" data-args="${d.id}" class="text-xs text-rose-500 hover:text-rose-700 p-1 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors" title="Xóa đợt khởi hành">
            <i class="fa-regular fa-trash-can"></i>
          </button>
        `;
      }

      if (!isAdmin && d.status !== 'OPEN') {
        actionButtons = '<span class="text-xs text-slate-400 italic">Chỉ xem</span>';
      }

      return `
        <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
          <td class="py-3 px-4 text-xs font-mono font-bold text-sky-600 dark:text-sky-400">${d.tour_code || ('#' + d.tour_id)}</td>
          <td class="py-3 px-4 font-semibold text-xs text-slate-800 dark:text-slate-100">
            <div>${d.tour_title || 'Tour du lịch'}</div>
            ${d.notes ? `<div class="text-[10px] text-slate-400 font-normal">${d.notes}</div>` : ''}
          </td>
          <td class="py-3 px-4 text-xs font-semibold text-emerald-600 dark:text-emerald-400">${d.departure_date}</td>
          <td class="py-3 px-4 text-xs font-medium text-slate-600 dark:text-slate-300">${d.return_date}</td>
          <td class="py-3 px-4">
            <div class="w-32">
              <div class="flex justify-between text-[11px] mb-1">
                <span class="font-bold text-slate-700 dark:text-slate-200">Còn ${d.available_slots}/${d.total_slots}</span>
                <span class="text-slate-400">${percent}%</span>
              </div>
              <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <progress class="w-full h-full" value="${percent}" max="100" aria-label="Tỷ lệ chỗ đã đặt"></progress>
              </div>
            </div>
          </td>
          <td class="py-3 px-4 text-xs">
            ${d.guide_name ? `
              <div class="flex items-center space-x-1.5">
                <span class="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 flex items-center justify-center text-[10px] font-bold">
                  <i class="fa-solid fa-user-tie"></i>
                </span>
                <span class="font-medium text-slate-800 dark:text-slate-200">${d.guide_name}</span>
              </div>
            ` : `<span class="text-slate-400 italic bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[11px]">Chưa phân công</span>`}
          </td>
          <td class="py-3 px-4">${statusBadge}</td>
          <td class="py-3 px-4 text-right">
            <div class="flex items-center justify-end space-x-1.5">
              ${actionButtons}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  renderBookingsTable: function() {
    const tbody = document.getElementById('bookings-table-body');
    if (!tbody) return;

    // Lọc ra các booking chính thức (đã xác nhận hoặc pending thanh toán, trừ WAITING_CONFIRM đã ở queue)
    let list = this.bookings.filter(b => b.status !== 'WAITING_CONFIRM');

    if (this.bookingStatusFilter && this.bookingStatusFilter !== 'ALL') {
      list = list.filter(b => b.status === this.bookingStatusFilter);
    }
    if (this.bookingPaymentFilter && this.bookingPaymentFilter !== 'ALL') {
      if (this.bookingPaymentFilter === 'UNPAID') list = list.filter(b => b.paid_amount === 0);
      else if (this.bookingPaymentFilter === 'PARTIAL') list = list.filter(b => b.paid_amount > 0 && b.paid_amount < b.total_amount);
      else if (this.bookingPaymentFilter === 'PAID') list = list.filter(b => b.paid_amount >= b.total_amount);
    }
    if (this.bookingSearchKeyword) {
      const kw = this.bookingSearchKeyword.toLowerCase().trim();
      list = list.filter(b =>
        (b.booking_code && b.booking_code.toLowerCase().includes(kw)) ||
        (b.customer_name && b.customer_name.toLowerCase().includes(kw)) ||
        (b.customer_phone && b.customer_phone.toLowerCase().includes(kw)) ||
        (b.tour_title && b.tour_title.toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('bookings-count-display');
    if (countEl) countEl.innerText = `Hiển thị ${list.length} / ${this.bookings.length} đơn`;

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">Không tìm thấy đơn đặt tour nào phù hợp với bộ lọc tìm kiếm.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(b => {
      const statusBadge = b.status === 'CONFIRMED' ? '<span class="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300 px-2 py-0.5 rounded text-[10px] font-bold">Xác nhận đủ</span>' :
                          b.status === 'DEPOSITED' ? '<span class="bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300 px-2 py-0.5 rounded text-[10px] font-bold">Đã cọc 30%</span>' :
                          b.status === 'PENDING' ? '<span class="bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300 px-2 py-0.5 rounded text-[10px] font-bold">Chờ thanh toán</span>' :
                          b.status === 'CANCELLED' ? '<span class="bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300 px-2 py-0.5 rounded text-[10px] font-bold">Đã hủy</span>' :
                          '<span class="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[10px] font-bold">' + b.status + '</span>';

      return `
        <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
          <td class="py-3 px-4 font-mono font-bold text-xs text-sky-600 dark:text-sky-400">${b.booking_code}</td>
          <td class="py-3 px-4 text-xs font-semibold text-slate-800 dark:text-slate-200">
            ${b.customer_name || 'Khách'}
            <span class="block text-[10px] text-slate-400 font-normal">${b.customer_phone || ''}</span>
          </td>
          <td class="py-3 px-4 text-xs text-slate-700 dark:text-slate-300">${b.tour_title || 'Tour'}</td>
          <td class="py-3 px-4 text-xs font-bold text-center">${b.num_people}</td>
          <td class="py-3 px-4 text-xs font-bold text-slate-800 dark:text-slate-200">${b.total_amount.toLocaleString('vi-VN')} đ</td>
          <td class="py-3 px-4 text-xs font-bold text-emerald-600 dark:text-emerald-400">${b.paid_amount.toLocaleString('vi-VN')} đ</td>
          <td class="py-3 px-4">${statusBadge}</td>
          <td class="py-3 px-4 text-right space-x-1.5 whitespace-nowrap">
            ${['ADMIN', 'ACCOUNTANT'].includes(this.currentUser?.role) && ['PENDING', 'DEPOSITED', 'CONFIRMED'].includes(b.status) && b.paid_amount < b.total_amount ? `
              <button data-action="openPaymentModal" data-event="click" data-args="${b.id}, ${b.total_amount - b.paid_amount}" class="text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-0.5 rounded font-medium">Thu tiền</button>
            ` : ''}
            ${['PENDING', 'DEPOSITED', 'CONFIRMED', 'WAITING_CONFIRM'].includes(b.status) && !['RUNNING', 'ON_TOUR', 'COMPLETED'].includes(this.departures.find(d => d.id === b.departure_id)?.status) ? `
              <button data-action="openCancelBookingModal" data-event="click" data-args="${b.id}" class="text-xs bg-rose-50 text-rose-600 hover:bg-rose-100 dark:bg-rose-900/20 dark:text-rose-400 px-2 py-0.5 rounded font-medium">Hủy</button>
            ` : ''}
            ${this.currentUser?.role === 'ADMIN' ? `
              <button data-action="deleteBooking" data-event="click" data-args="${b.id}" class="text-xs text-rose-600 hover:text-rose-800 font-bold px-1.5 py-0.5 rounded hover:bg-rose-50 dark:hover:bg-rose-950/30" title="Xóa vĩnh viễn đặt chỗ">Xóa</button>
            ` : ''}
          </td>
        </tr>
      `;
    }).join('');
  },

  renderPaymentsTable: function() {
    const tbody = document.getElementById('payments-table-body');
    if (!tbody) return;

    let list = this.payments;
    if (this.paymentTypeFilter && this.paymentTypeFilter !== 'ALL') {
      list = list.filter(p => p.payment_type === this.paymentTypeFilter);
    }
    if (this.paymentMethodFilter && this.paymentMethodFilter !== 'ALL') {
      list = list.filter(p => p.payment_method === this.paymentMethodFilter);
    }
    if (this.paymentSearchKeyword) {
      const kw = this.paymentSearchKeyword.toLowerCase().trim();
      list = list.filter(p =>
        (p.transaction_code && p.transaction_code.toLowerCase().includes(kw)) ||
        (p.note && p.note.toLowerCase().includes(kw)) ||
        (p.created_by && p.created_by.toLowerCase().includes(kw)) ||
        (('booking #' + p.booking_id).toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('payments-count-display');
    if (countEl) countEl.innerText = `Hiển thị ${list.length} / ${this.payments.length} giao dịch`;

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">Không tìm thấy giao dịch nào phù hợp với bộ lọc tìm kiếm.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(p => `
      <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
        <td class="py-3 px-4 font-mono text-xs text-slate-500">${p.transaction_code || ('TXN-' + p.id)}</td>
        <td class="py-3 px-4 font-mono text-xs text-sky-600">Booking #${p.booking_id}</td>
        <td class="py-3 px-4 text-xs">
          <span class="font-semibold ${p.payment_type === 'REFUND' ? 'text-rose-500' : 'text-emerald-600 dark:text-emerald-400'}">
            ${p.payment_type === 'DEPOSIT' ? 'Đặt cọc' : p.payment_type === 'FINAL' ? 'Thanh toán đợt cuối' : p.payment_type === 'REFUND' ? 'Hoàn tiền hủy tour' : 'Toàn bộ'}
          </span>
        </td>
        <td class="py-3 px-4 text-xs font-bold ${p.payment_type === 'REFUND' ? 'text-rose-600' : 'text-slate-800 dark:text-slate-200'}">
          ${p.payment_type === 'REFUND' ? '-' : '+'}${p.amount.toLocaleString('vi-VN')} đ
        </td>
        <td class="py-3 px-4 text-xs text-slate-600 dark:text-slate-400">${p.payment_method}</td>
        <td class="py-3 px-4 text-xs text-slate-500">${p.created_by}</td>
        <td class="py-3 px-4 text-xs text-slate-400">${new Date(p.created_at).toLocaleDateString('vi-VN')}</td>
      </tr>
    `).join('');
  },

  renderGuidesTable: function() {
    // Cập nhật các KPI stats
    const totalCount = this.guides.length;
    const availCount = this.guides.filter(g => g.status === 'AVAILABLE').length;
    const ontourCount = this.guides.filter(g => g.status === 'ON_TOUR').length;
    const avgRating = totalCount > 0 
      ? (this.guides.reduce((acc, g) => acc + (parseFloat(g.rating) || 5), 0) / totalCount).toFixed(1)
      : '5.0';

    const statTotalEl = document.getElementById('guide-stat-total');
    if (statTotalEl) statTotalEl.textContent = totalCount;
    const statAvailEl = document.getElementById('guide-stat-available');
    if (statAvailEl) statAvailEl.textContent = availCount;
    const statOntourEl = document.getElementById('guide-stat-ontour');
    if (statOntourEl) statOntourEl.textContent = ontourCount;
    const statRatingEl = document.getElementById('guide-stat-rating');
    if (statRatingEl) statRatingEl.textContent = `${avgRating} / 5.0`;

    // Lọc danh sách theo status & keyword
    let list = this.guides;
    if (this.guideFilterStatus && this.guideFilterStatus !== 'ALL') {
      list = list.filter(g => g.status === this.guideFilterStatus);
    }
    if (this.guideSearchKeyword) {
      const kw = this.guideSearchKeyword.toLowerCase().trim();
      list = list.filter(g => 
        (g.full_name && g.full_name.toLowerCase().includes(kw)) ||
        (g.phone && g.phone.toLowerCase().includes(kw)) ||
        (g.languages && g.languages.toLowerCase().includes(kw)) ||
        (g.notes && g.notes.toLowerCase().includes(kw))
      );
    }

    const tableBody = document.getElementById('guides-table-body');
    const cardsGrid = document.getElementById('guides-cards-grid');

    const statusBadge = (st) => {
      if (st === 'AVAILABLE') {
        return '<span class="inline-flex items-center space-x-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span><span>Sẵn sàng</span></span>';
      }
      if (st === 'ON_TOUR') {
        return '<span class="inline-flex items-center space-x-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-800"><span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span><span>Đang dẫn tour</span></span>';
      }
      return '<span class="inline-flex items-center space-x-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border border-slate-300 dark:border-slate-700"><span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span><span>Nghỉ phép</span></span>';
    };

    const isAdmin = this.currentUser && this.currentUser.role === 'ADMIN';

    // 1. Render Table View (dạng bảng quản trị trực quan đầy đủ nút Sửa, Xóa)
    if (tableBody) {
      if (list.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="8" class="py-12 text-center text-slate-400">
              <div class="flex flex-col items-center justify-center space-y-2">
                <i class="fa-solid fa-user-slash text-3xl text-slate-300 dark:text-slate-600 mb-1"></i>
                <span class="font-bold text-slate-700 dark:text-slate-300 text-sm">Không tìm thấy hướng dẫn viên nào</span>
                <span class="text-xs text-slate-400">Thử đổi bộ lọc hoặc thêm hướng dẫn viên mới</span>
                ${isAdmin ? `
                  <button data-action="openGuideModal" data-event="click" data-args="" class="mt-3 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-xs shadow-sm">
                    + Thêm Hướng Dẫn Viên Mới
                  </button>
                ` : ''}
              </div>
            </td>
          </tr>
        `;
      } else {
        tableBody.innerHTML = list.map(g => {
          const nameParts = (g.full_name || 'HDV').trim().split(' ');
          const initials = nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0) : (g.full_name || 'H').charAt(0);
          const safeName = (g.full_name || '').replace(/'/g, "\\'");
          const actionButtons = isAdmin ? `
            <div class="flex items-center justify-end space-x-1.5">
              <button data-action="openAssignTourForGuide" data-event="click" data-args="${g.id}" class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-300 font-bold text-xs transition-colors shadow-xs" title="Phân công HDV này dẫn một tour du lịch">
                <i class="fa-solid fa-calendar-plus text-[11px]"></i>
                <span>Giao tour</span>
              </button>
              <button data-action="openGuideModal" data-event="click" data-args="${g.id}" class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-sky-50 dark:bg-sky-950/50 hover:bg-sky-100 dark:hover:bg-sky-900/60 text-sky-600 dark:text-sky-300 font-bold text-xs transition-colors shadow-xs" title="Chỉnh sửa thông tin HDV">
                <i class="fa-solid fa-pen-to-square text-[11px]"></i>
                <span>Sửa</span>
              </button>
              <button data-action="deleteGuide" data-event="click" data-args="${g.id}" class="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/50 text-rose-600 dark:text-rose-400 font-bold text-xs transition-colors shadow-xs" title="Xóa hướng dẫn viên">
                <i class="fa-solid fa-trash-can text-[11px]"></i>
                <span>Xóa</span>
              </button>
            </div>
          ` : `<span class="text-xs text-slate-400 italic bg-slate-50 dark:bg-slate-800/60 px-2.5 py-1 rounded-lg">Chỉ xem</span>`;

          return `
            <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors">
              <td class="py-3 px-4">
                <div class="flex items-center space-x-3">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-cyan-400 text-white font-extrabold text-xs flex items-center justify-center shadow-sm shrink-0">
                    ${initials}
                  </div>
                  <div class="min-w-0">
                    <p class="font-bold text-slate-900 dark:text-slate-100 text-xs truncate" title="${g.full_name}">${g.full_name}</p>
                    <p class="text-[10px] text-slate-400">Mã: #${g.id}</p>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 font-medium text-xs text-slate-700 dark:text-slate-300 whitespace-nowrap">
                <a href="tel:${g.phone}" class="hover:text-sky-600 flex items-center space-x-1.5">
                  <i class="fa-solid fa-phone text-[10px] text-sky-500"></i>
                  <span>${g.phone}</span>
                </a>
              </td>
              <td class="py-3 px-4 text-xs text-slate-600 dark:text-slate-400 max-w-[160px] truncate" title="${g.email || ''}">
                ${g.email || '<span class="text-slate-400 italic">Chưa có</span>'}
              </td>
              <td class="py-3 px-4 text-xs text-slate-700 dark:text-slate-300">
                <span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-[11px] font-semibold text-slate-700 dark:text-slate-300">${g.languages || 'Tiếng Việt'}</span>
              </td>
              <td class="py-3 px-4 text-center font-bold text-sky-600 dark:text-sky-400 text-xs whitespace-nowrap">
                ${g.experience_years} năm
              </td>
              <td class="py-3 px-4 text-center font-bold text-amber-500 text-xs whitespace-nowrap">
                <span>${g.rating}</span> / 5.0
              </td>
              <td class="py-3 px-4 text-center whitespace-nowrap">
                ${statusBadge(g.status)}
              </td>
              <td class="py-3 px-4 text-right whitespace-nowrap">
                ${actionButtons}
              </td>
            </tr>
          `;
        }).join('');
      }
    }

    // 2. Render Cards View (dạng thẻ)
    if (cardsGrid) {
      if (list.length === 0) {
        cardsGrid.innerHTML = `
          <div class="col-span-full py-12 text-center bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-3xl p-8">
            <div class="w-12 h-12 rounded-2xl bg-sky-50 dark:bg-sky-950/40 text-sky-500 mx-auto flex items-center justify-center text-xl mb-3">
              <i class="fa-solid fa-user-slash"></i>
            </div>
            <p class="font-bold text-slate-700 dark:text-slate-200 text-sm">Không tìm thấy hướng dẫn viên nào</p>
            <p class="text-xs text-slate-400 mt-1">Thử đổi bộ lọc trạng thái hoặc từ khóa tìm kiếm</p>
            ${isAdmin ? `
              <button data-action="openGuideModal" data-event="click" data-args="" class="mt-4 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-xs shadow-sm">
                + Thêm Hướng Dẫn Viên Mới
              </button>
            ` : ''}
          </div>
        `;
      } else {
        cardsGrid.innerHTML = list.map(g => {
          const nameParts = (g.full_name || 'HDV').trim().split(' ');
          const initials = nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0) : (g.full_name || 'H').charAt(0);
          const safeName = (g.full_name || '').replace(/'/g, "\\'");
          const cardBottomActions = isAdmin ? `
            <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-1.5">
              <button data-action="openAssignTourForGuide" data-event="click" data-args="${g.id}" class="flex-1 inline-flex items-center justify-center space-x-1 py-1.5 px-2 rounded-xl bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-300 font-bold text-xs transition-colors shadow-xs" title="Giao tour cho HDV này">
                <i class="fa-solid fa-calendar-plus text-[11px]"></i>
                <span>Giao tour</span>
              </button>
              <button data-action="openGuideModal" data-event="click" data-args="${g.id}" class="inline-flex items-center justify-center space-x-1 py-1.5 px-2.5 rounded-xl bg-sky-50 dark:bg-sky-950/40 hover:bg-sky-100 dark:hover:bg-sky-900/50 text-sky-700 dark:text-sky-300 font-bold text-xs transition-colors">
                <i class="fa-solid fa-pen-to-square text-[11px]"></i>
                <span>Sửa</span>
              </button>
              <button data-action="deleteGuide" data-event="click" data-args="${g.id}" class="inline-flex items-center justify-center space-x-1 py-1.5 px-2 rounded-xl bg-rose-50 dark:bg-rose-950/30 hover:bg-rose-100 dark:hover:bg-rose-900/40 text-rose-600 dark:text-rose-400 font-bold text-xs transition-colors" title="Xóa hướng dẫn viên">
                <i class="fa-solid fa-trash-can text-[11px]"></i>
              </button>
            </div>
          ` : `
            <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-center">
              <span class="text-xs text-slate-400 italic">Chế độ xem hồ sơ HDV</span>
            </div>
          `;

          return `
            <div class="bg-white dark:bg-[#0c1322] border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
              <div>
                <div class="flex items-start justify-between mb-3.5">
                  <div class="flex items-center space-x-3">
                    <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-sky-500 to-cyan-400 flex items-center justify-center text-white font-extrabold text-base shadow-sm group-hover:scale-105 transition-transform">
                      ${initials}
                    </div>
                    <div class="overflow-hidden">
                      <h4 class="font-extrabold text-slate-900 dark:text-white text-sm truncate group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors" title="${g.full_name}">${g.full_name}</h4>
                      <a href="tel:${g.phone}" class="text-[11px] text-slate-500 hover:text-sky-600 flex items-center space-x-1 mt-0.5">
                        <i class="fa-solid fa-phone text-[10px] text-sky-500"></i>
                        <span>${g.phone}</span>
                      </a>
                    </div>
                  </div>
                  <div>${statusBadge(g.status)}</div>
                </div>

                <div class="space-y-1.5 py-2 border-y border-slate-100 dark:border-slate-800/80 text-xs">
                  ${g.email ? `
                    <div class="flex items-center justify-between text-slate-500">
                      <span>Email:</span>
                      <span class="font-medium text-slate-700 dark:text-slate-300 truncate max-w-[170px]" title="${g.email}">${g.email}</span>
                    </div>
                  ` : ''}
                  <div class="flex items-center justify-between text-slate-500">
                    <span>Ngoại ngữ:</span>
                    <span class="font-bold text-slate-700 dark:text-slate-200 truncate max-w-[170px]" title="${g.languages || 'Tiếng Việt'}">${g.languages || 'Tiếng Việt'}</span>
                  </div>
                  <div class="flex items-center justify-between text-slate-500">
                    <span>Kinh nghiệm:</span>
                    <span class="font-bold text-sky-600 dark:text-sky-400">${g.experience_years} năm</span>
                  </div>
                  <div class="flex items-center justify-between text-slate-500">
                    <span>Đánh giá khách:</span>
                    <span class="font-bold text-amber-500 flex items-center space-x-1">
                      <span>${g.rating}</span>
                      <i class="fa-solid fa-star text-[10px]"></i>
                    </span>
                  </div>
                </div>

                <div class="mt-2.5">
                  <p class="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 italic">
                    ${g.notes ? `"${g.notes}"` : 'Chưa có ghi chú tuyến tour.'}
                  </p>
                </div>
              </div>

              <!-- Bottom Action Buttons: Giao tour, Sửa & Xóa (Chỉ ADMIN) -->
              ${cardBottomActions}
            </div>
          `;
        }).join('');
      }
    }
  },

  // ==================== TOUR GUIDES MANAGEMENT ====================
  setGuideViewMode: function(mode) {
    this.guideViewMode = mode;
    const tableContainer = document.getElementById('guides-table-container');
    const cardsGrid = document.getElementById('guides-cards-grid');
    const btnTable = document.getElementById('guide-view-btn-table');
    const btnCards = document.getElementById('guide-view-btn-cards');

    if (mode === 'table') {
      if (tableContainer) tableContainer.classList.remove('hidden');
      if (cardsGrid) cardsGrid.classList.add('hidden');
      if (btnTable) {
        btnTable.className = 'px-2.5 py-1 rounded-lg text-xs font-bold bg-white dark:bg-slate-700 text-sky-600 dark:text-sky-300 shadow-sm transition-all flex items-center space-x-1';
      }
      if (btnCards) {
        btnCards.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-all flex items-center space-x-1';
      }
    } else {
      if (tableContainer) tableContainer.classList.add('hidden');
      if (cardsGrid) cardsGrid.classList.remove('hidden');
      if (btnCards) {
        btnCards.className = 'px-2.5 py-1 rounded-lg text-xs font-bold bg-white dark:bg-slate-700 text-sky-600 dark:text-sky-300 shadow-sm transition-all flex items-center space-x-1';
      }
      if (btnTable) {
        btnTable.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-all flex items-center space-x-1';
      }
    }
  },

  setGuideStatusFilter: function(status) {
    this.guideFilterStatus = status;
    document.querySelectorAll('.guide-filter-btn').forEach(btn => {
      if (btn.id === `guide-filter-${status}`) {
        btn.classList.add('bg-sky-600', 'text-white');
        btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      } else {
        btn.classList.remove('bg-sky-600', 'text-white');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      }
    });
    this.renderGuidesTable();
  },

  filterGuidesList: function() {
    const input = document.getElementById('guide-search-input');
    this.guideSearchKeyword = input ? input.value : '';
    this.renderGuidesTable();
  },

  onGuideSearchChange: function() {
    this.filterGuidesList();
  },

  resetGuideFilters: function() {
    this.guideSearchKeyword = '';
    this.guideFilterStatus = 'ALL';
    const input = document.getElementById('guide-search-input');
    if (input) input.value = '';
    document.querySelectorAll('.guide-filter-btn').forEach(btn => {
      if (btn.id === 'guide-filter-ALL') {
        btn.classList.add('bg-sky-600', 'text-white');
        btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      } else {
        btn.classList.remove('bg-sky-600', 'text-white');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      }
    });
    this.renderGuidesTable();
  },

  openGuideModal: function(guideId = null) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      this.showToast("Chỉ Quản trị viên (Admin) mới có quyền thêm hoặc sửa hướng dẫn viên!", "error");
      return;
    }

    const modal = document.getElementById('guide-modal');
    if (!modal) return;

    const titleEl = document.getElementById('guide-modal-title');
    const saveBtnText = document.getElementById('btn-save-guide-text');
    const idInput = document.getElementById('guide-form-id');
    const nameInput = document.getElementById('guide-form-fullname');
    const phoneInput = document.getElementById('guide-form-phone');
    const emailInput = document.getElementById('guide-form-email');
    const langInput = document.getElementById('guide-form-languages');
    const expInput = document.getElementById('guide-form-experience');
    const statusSelect = document.getElementById('guide-form-status');
    const ratingInput = document.getElementById('guide-form-rating');
    const notesInput = document.getElementById('guide-form-notes');

    if (guideId) {
      const g = this.guides.find(item => item.id === guideId);
      if (!g) {
        this.showToast("Không tìm thấy thông tin hướng dẫn viên!", "error");
        return;
      }
      if (titleEl) titleEl.textContent = `Chỉnh Sửa: ${g.full_name}`;
      if (saveBtnText) saveBtnText.textContent = "Cập Nhật Hướng Dẫn Viên";
      if (idInput) idInput.value = g.id;
      if (nameInput) nameInput.value = g.full_name || '';
      if (phoneInput) phoneInput.value = g.phone || '';
      if (emailInput) emailInput.value = g.email || '';
      if (langInput) langInput.value = g.languages || 'Tiếng Việt';
      if (expInput) expInput.value = g.experience_years !== undefined ? g.experience_years : 3;
      if (statusSelect) statusSelect.value = g.status || 'AVAILABLE';
      if (ratingInput) ratingInput.value = g.rating !== undefined ? g.rating : 4.8;
      if (notesInput) notesInput.value = g.notes || '';
    } else {
      if (titleEl) titleEl.textContent = "Thêm Hướng Dẫn Viên Mới";
      if (saveBtnText) saveBtnText.textContent = "Lưu Hướng Dẫn Viên";
      if (idInput) idInput.value = '';
      if (nameInput) nameInput.value = '';
      if (phoneInput) phoneInput.value = '';
      if (emailInput) emailInput.value = '';
      if (langInput) langInput.value = 'Tiếng Việt, Tiếng Anh';
      if (expInput) expInput.value = 3;
      if (statusSelect) statusSelect.value = 'AVAILABLE';
      if (ratingInput) ratingInput.value = 4.8;
      if (notesInput) notesInput.value = '';
    }

    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    if (nameInput) {
      setTimeout(() => {
        try { nameInput.focus(); } catch (e) {}
      }, 50);
    }
  },

  submitGuideForm: async function() {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền thêm hoặc sửa hướng dẫn viên!");
      return;
    }

    const idInput = document.getElementById('guide-form-id');
    const guideId = idInput ? idInput.value : '';
    const fullname = (document.getElementById('guide-form-fullname')?.value || '').trim();
    const phone = (document.getElementById('guide-form-phone')?.value || '').trim();
    const email = (document.getElementById('guide-form-email')?.value || '').trim();
    const languages = (document.getElementById('guide-form-languages')?.value || '').trim() || 'Tiếng Việt';
    const experience = parseInt(document.getElementById('guide-form-experience')?.value) || 0;
    const status = document.getElementById('guide-form-status')?.value || 'AVAILABLE';
    const rating = parseFloat(document.getElementById('guide-form-rating')?.value) || 4.8;
    const notes = (document.getElementById('guide-form-notes')?.value || '').trim();

    if (!fullname) {
      alert("Vui lòng nhập Họ và tên hướng dẫn viên!");
      return;
    }
    if (!phone) {
      alert("Vui lòng nhập Số điện thoại hướng dẫn viên!");
      return;
    }

    const payload = {
      full_name: fullname,
      phone: phone,
      email: email || null,
      languages: languages,
      experience_years: experience,
      status: status,
      rating: rating,
      notes: notes || null
    };

    const isEdit = Boolean(guideId);
    const url = isEdit ? `/api/v1/guides/${guideId}` : '/api/v1/guides';
    const method = isEdit ? 'PUT' : 'POST';

    const saveBtn = document.getElementById('btn-save-guide');
    if (saveBtn) saveBtn.disabled = true;

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }

      const res = await fetch(url, {
        method: method,
        headers: headers,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể lưu thông tin hướng dẫn viên"));
        if (saveBtn) saveBtn.disabled = false;
        return;
      }

      this.closeModal('guide-modal');
      this.showToast(isEdit ? "Đã cập nhật thông tin hướng dẫn viên thành công!" : "Đã thêm hướng dẫn viên mới thành công!", "success");
      await this.fetchGuides();
    } catch (err) {
      console.error(err);
      alert("Lỗi kết nối khi gửi dữ liệu hướng dẫn viên.");
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  },

  deleteGuide: async function(guideId, guideName) {
    guideName = this.guides.find(g => g.id === guideId)?.full_name || "HDV";
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền xóa hướng dẫn viên!");
      return;
    }

    const confirmed = confirm(`Bạn có chắc chắn muốn xóa hướng dẫn viên "${guideName}" khỏi hệ thống không?\n\nLưu ý: Nếu hướng dẫn viên đang được gán tour, hệ thống sẽ tự động gỡ phân công an toàn.`);
    if (!confirmed) return;

    try {
      const headers = {};
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }

      const res = await fetch(`/api/v1/guides/${guideId}`, {
        method: 'DELETE',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi khi xóa: " + (err.detail || "Không có quyền hoặc dữ liệu bị ràng buộc"));
        return;
      }

      this.showToast(`Đã xóa hướng dẫn viên "${guideName}" thành công!`, "success");
      await this.fetchGuides();
    } catch (err) {
      console.error(err);
      alert("Lỗi kết nối máy chủ khi xóa hướng dẫn viên.");
    }
  },

  fetchGuides: async function() {
    try {
      const res = await fetch('/api/v1/guides');
      if (res.ok) {
        this.guides = await res.json();
        this.renderGuidesTable();
      }
    } catch (e) {
      console.error("Lỗi tải danh sách guides:", e);
    }
  },

  renderFeedbacksList: function() {
    const container = document.getElementById('feedbacks-stream-list');
    if (!container) return;

    let list = this.feedbacks;
    if (this.feedbackSentimentFilter && this.feedbackSentimentFilter !== 'ALL') {
      list = list.filter(f => f.sentiment === this.feedbackSentimentFilter);
    }
    if (this.feedbackRatingFilter && this.feedbackRatingFilter !== 'ALL') {
      const targetRating = parseInt(this.feedbackRatingFilter);
      list = list.filter(f => f.rating === targetRating);
    }
    if (this.feedbackSearchKeyword) {
      const kw = this.feedbackSearchKeyword.toLowerCase().trim();
      list = list.filter(f =>
        (f.customer_name && f.customer_name.toLowerCase().includes(kw)) ||
        (f.tour_title && f.tour_title.toLowerCase().includes(kw)) ||
        (f.comments && f.comments.toLowerCase().includes(kw))
      );
    }

    const countEl = document.getElementById('feedbacks-count-display');
    if (countEl) countEl.innerText = `Hiển thị ${list.length} / ${this.feedbacks.length} phản hồi`;

    if (list.length === 0) {
      container.innerHTML = `<div class="p-8 text-center text-slate-400 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">Không tìm thấy phản hồi nào phù hợp với bộ lọc tìm kiếm.</div>`;
      return;
    }

    container.innerHTML = list.map(f => {
      const stars = '<i class="fa-solid fa-star text-amber-400 text-xs"></i>'.repeat(f.rating);
      return `
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm mb-3">
          <div class="flex justify-between items-start">
            <div>
              <span class="font-bold text-sm text-slate-800 dark:text-slate-100">${f.customer_name}</span>
              <span class="text-xs text-sky-600 dark:text-sky-400 font-medium ml-2">${f.tour_title || 'Tour du lịch'}</span>
            </div>
            <div class="text-xs text-amber-500">${stars} (${f.rating}/5)</div>
          </div>
          <p class="text-sm text-slate-700 dark:text-slate-300 mt-2 leading-relaxed">"${f.comments}"</p>
          <div class="mt-3 flex justify-between items-center text-[11px] text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
            <span>Đánh giá HDV: ${f.guide_rating}/5 sao</span>
            <span>${new Date(f.created_at).toLocaleDateString('vi-VN')}</span>
          </div>
        </div>
      `;
    }).join('');
  },

  // ==================== THÊM PHẢN HỒI TỪ GIAO DIỆN ====================
  openAddFeedbackModal: async function(preselectedTourId = null) {
    const modal = document.getElementById('add-feedback-modal');
    if (!modal) return;

    if (!Array.isArray(this.tours) || this.tours.length === 0) {
      try {
        const res = await fetch('/api/v1/tours');
        if (res.ok) this.tours = await res.json();
      } catch (e) {
        console.error("Lỗi tải danh sách tour cho feedback modal:", e);
      }
    }

    const select = document.getElementById('fb-form-tour-id');
    if (select) {
      let html = '<option value="">-- Chọn tour bạn muốn đánh giá --</option>';
      if (Array.isArray(this.tours)) {
        this.tours.forEach(t => {
          const selected = (preselectedTourId && t.id === parseInt(preselectedTourId)) ? 'selected' : '';
          html += `<option value="${t.id}" ${selected}>[${t.code}] ${t.title}</option>`;
        });
      }
      select.innerHTML = html;
    }

    const nameInput = document.getElementById('fb-form-name');
    if (nameInput) {
      nameInput.value = this.currentUser?.full_name || '';
    }

    const commentsInput = document.getElementById('fb-form-comments');
    if (commentsInput) commentsInput.value = '';

    modal.classList.remove('hidden');
  },

  submitFeedbackForm: async function() {
    const tourId = parseInt(document.getElementById('fb-form-tour-id')?.value);
    const name = document.getElementById('fb-form-name')?.value.trim();
    const rating = parseInt(document.getElementById('fb-form-rating')?.value) || 5;
    const guideRating = parseInt(document.getElementById('fb-form-guide-rating')?.value) || 5;
    const comments = document.getElementById('fb-form-comments')?.value.trim();

    if (!tourId) {
      this.showToast("Vui lòng chọn tour bạn đã trải nghiệm!", "warning");
      return;
    }
    if (!name) {
      this.showToast("Vui lòng nhập họ và tên của bạn!", "warning");
      return;
    }
    if (!comments || comments.length < 5) {
      this.showToast("Vui lòng viết nhận xét tối thiểu 5 ký tự!", "warning");
      return;
    }

    const submitBtn = document.getElementById('btn-submit-feedback');
    const oldText = submitBtn ? submitBtn.innerHTML : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Đang gửi...';
    }

    try {
      const res = await fetch('/api/v1/feedbacks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tour_id: tourId,
          customer_name: name,
          rating: rating,
          guide_rating: guideRating,
          comments: comments
        })
      });

      if (!res.ok) {
        const err = await res.json();
        this.showToast("Lỗi: " + (err.detail || "Không thể gửi đánh giá."), "error");
        return;
      }

      const newFb = await res.json();
      this.showToast("Cảm ơn bạn đã gửi đánh giá chuyến đi thành công!", "success");
      this.closeModal('add-feedback-modal');

      if (!Array.isArray(this.feedbacks)) this.feedbacks = [];
      this.feedbacks.unshift(newFb);
      this.renderFeedbacksList();

      if (window.AIHub && typeof window.AIHub.populateFeedbackTours === 'function') {
        window.AIHub.populateFeedbackTours();
      }
    } catch (e) {
      console.error(e);
      this.showToast("Lỗi kết nối khi gửi đánh giá!", "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = oldText;
      }
    }
  },

  // ==================== MULTI-FIELD SEARCH & FILTER HANDLERS ====================
  onTourSearchChange: function() {
    const kwInput = document.getElementById('tour-search-keyword');
    const catSelect = document.getElementById('tour-filter-category');
    const priceSelect = document.getElementById('tour-filter-price');
    const statusSelect = document.getElementById('tour-filter-status');

    this.tourSearchKeyword = kwInput ? kwInput.value : '';
    this.tourCategoryFilter = catSelect ? catSelect.value : 'ALL';
    this.tourPriceFilter = priceSelect ? priceSelect.value : 'ALL';
    this.tourStatusFilter = statusSelect ? statusSelect.value : 'ALL';

    this.renderToursTable();
  },

  resetTourFilters: function() {
    this.tourSearchKeyword = '';
    this.tourCategoryFilter = 'ALL';
    this.tourPriceFilter = 'ALL';
    this.tourStatusFilter = 'ALL';

    const kwInput = document.getElementById('tour-search-keyword');
    const catSelect = document.getElementById('tour-filter-category');
    const priceSelect = document.getElementById('tour-filter-price');
    const statusSelect = document.getElementById('tour-filter-status');

    if (kwInput) kwInput.value = '';
    if (catSelect) catSelect.value = 'ALL';
    if (priceSelect) priceSelect.value = 'ALL';
    if (statusSelect) statusSelect.value = 'ALL';

    this.renderToursTable();
  },

  onDepartureSearchChange: function() {
    const kwInput = document.getElementById('dep-search-keyword');
    const statusSelect = document.getElementById('dep-filter-status');
    const guideSelect = document.getElementById('dep-filter-guide');

    this.departureSearchKeyword = kwInput ? kwInput.value : '';
    this.departureStatusFilter = statusSelect ? statusSelect.value : 'ALL';
    this.departureGuideFilter = guideSelect ? guideSelect.value : 'ALL';

    this.renderDeparturesTable();
  },

  resetDepartureFilters: function() {
    this.departureSearchKeyword = '';
    this.departureStatusFilter = 'ALL';
    this.departureGuideFilter = 'ALL';

    const kwInput = document.getElementById('dep-search-keyword');
    const statusSelect = document.getElementById('dep-filter-status');
    const guideSelect = document.getElementById('dep-filter-guide');

    if (kwInput) kwInput.value = '';
    if (statusSelect) statusSelect.value = 'ALL';
    if (guideSelect) guideSelect.value = 'ALL';

    this.renderDeparturesTable();
  },

  onBookingSearchChange: function() {
    const kwInput = document.getElementById('booking-search-keyword');
    const statusSelect = document.getElementById('booking-filter-status');
    const paySelect = document.getElementById('booking-filter-payment');

    this.bookingSearchKeyword = kwInput ? kwInput.value : '';
    this.bookingStatusFilter = statusSelect ? statusSelect.value : 'ALL';
    this.bookingPaymentFilter = paySelect ? paySelect.value : 'ALL';

    this.renderBookingsTable();
  },

  resetBookingFilters: function() {
    this.bookingSearchKeyword = '';
    this.bookingStatusFilter = 'ALL';
    this.bookingPaymentFilter = 'ALL';

    const kwInput = document.getElementById('booking-search-keyword');
    const statusSelect = document.getElementById('booking-filter-status');
    const paySelect = document.getElementById('booking-filter-payment');

    if (kwInput) kwInput.value = '';
    if (statusSelect) statusSelect.value = 'ALL';
    if (paySelect) paySelect.value = 'ALL';

    this.renderBookingsTable();
  },

  onQueueSearchChange: function() {
    const kwInput = document.getElementById('queue-search-keyword');
    this.queueSearchKeyword = kwInput ? kwInput.value : '';
    this.renderQueueTable();
  },

  resetQueueFilters: function() {
    this.queueSearchKeyword = '';
    const kwInput = document.getElementById('queue-search-keyword');
    if (kwInput) kwInput.value = '';
    this.renderQueueTable();
  },

  onPaymentSearchChange: function() {
    const kwInput = document.getElementById('payment-search-keyword');
    const typeSelect = document.getElementById('payment-filter-type');
    const methodSelect = document.getElementById('payment-filter-method');

    this.paymentSearchKeyword = kwInput ? kwInput.value : '';
    this.paymentTypeFilter = typeSelect ? typeSelect.value : 'ALL';
    this.paymentMethodFilter = methodSelect ? methodSelect.value : 'ALL';

    this.renderPaymentsTable();
  },

  resetPaymentFilters: function() {
    this.paymentSearchKeyword = '';
    this.paymentTypeFilter = 'ALL';
    this.paymentMethodFilter = 'ALL';

    const kwInput = document.getElementById('payment-search-keyword');
    const typeSelect = document.getElementById('payment-filter-type');
    const methodSelect = document.getElementById('payment-filter-method');

    if (kwInput) kwInput.value = '';
    if (typeSelect) typeSelect.value = 'ALL';
    if (methodSelect) methodSelect.value = 'ALL';

    this.renderPaymentsTable();
  },

  onFeedbackSearchChange: function() {
    const kwInput = document.getElementById('feedback-search-keyword');
    const sentSelect = document.getElementById('feedback-filter-sentiment');
    const ratingSelect = document.getElementById('feedback-filter-rating');

    this.feedbackSearchKeyword = kwInput ? kwInput.value : '';
    this.feedbackSentimentFilter = sentSelect ? sentSelect.value : 'ALL';
    this.feedbackRatingFilter = ratingSelect ? ratingSelect.value : 'ALL';

    this.renderFeedbacksList();
  },

  resetFeedbackFilters: function() {
    this.feedbackSearchKeyword = '';
    this.feedbackSentimentFilter = 'ALL';
    this.feedbackRatingFilter = 'ALL';

    const kwInput = document.getElementById('feedback-search-keyword');
    const sentSelect = document.getElementById('feedback-filter-sentiment');
    const ratingSelect = document.getElementById('feedback-filter-rating');

    if (kwInput) kwInput.value = '';
    if (sentSelect) sentSelect.value = 'ALL';
    if (ratingSelect) ratingSelect.value = 'ALL';

    this.renderFeedbacksList();
  },

  renderAnalytics: function() {
    if (window.ChartService) {
      window.ChartService.initRevenueChart('analytics-revenue-canvas', this.stats.top_tours);
      window.ChartService.initOccupancyChart('analytics-occupancy-canvas', this.stats.average_occupancy_rate);
    }
  },

  // ==================== GUEST BOOKING MODAL & ACTIONS ====================
  openGuestBookingModal: function() {
    this.populateTourSelects();
    const modal = document.getElementById('guest-booking-modal');
    if (modal) modal.classList.remove('hidden');
  },

  openGuestBookingModalForTour: function(tourId) {
    this.openGuestBookingModal();
    setTimeout(() => {
      const depSelect = document.getElementById('guest-dep-select');
      if (depSelect) {
        const matchingDep = this.departures.find(d => d.tour_id === tourId && d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA') && d.available_slots > 0);
        depSelect.value = matchingDep ? matchingDep.id : '';
      }
    }, 50);
  },

  submitGuestBooking: async function() {
    const depId = parseInt(document.getElementById('guest-dep-select').value);
    const name = document.getElementById('guest-cust-name').value.trim();
    const phone = document.getElementById('guest-cust-phone').value.trim();
    const email = document.getElementById('guest-cust-email').value.trim();
    const numPeople = Number(document.getElementById('guest-num-people').value);
    if (!Number.isInteger(numPeople) || numPeople < 1) { this.showToast("Số khách phải là số nguyên dương.", "error"); return; }
    const notes = document.getElementById('guest-special-requests').value.trim();

    if (!depId || !name || !phone) {
      alert("Vui lòng điền đầy đủ Họ tên, Số điện thoại và chọn tour khởi hành!");
      return;
    }

    try {
      const res = await fetch('/api/v1/bookings/guest-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          departure_id: depId,
          customer_name: name,
          customer_phone: phone,
          customer_email: email,
          num_people: numPeople,
          special_requests: notes
        })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi gửi yêu cầu: " + (err.detail || "Thất bại"));
        return;
      }

      const booking = await res.json();
      this.closeModal('guest-booking-modal');
      window.UI.showConfirmation(booking.booking_code);
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối khi gửi thông tin.");
    }
  },

  // ==================== CONSULTANT QUEUE APPROVAL ====================
  openConfirmBookingModal: function(bookingId, custName) {
    custName = this.bookings.find(b => b.id === bookingId)?.customer_name || "Khách";
    const modal = document.getElementById('confirm-booking-modal');
    if (!modal) return;
    document.getElementById('confirm-booking-id').value = bookingId;
    document.getElementById('confirm-booking-cust-name').innerText = custName;
    document.getElementById('confirm-booking-note').value = '';
    modal.classList.remove('hidden');
  },

  submitConfirmBooking: async function() {
    const bookingId = document.getElementById('confirm-booking-id').value;
    const note = document.getElementById('confirm-booking-note').value.trim();

    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      };
      const res = await fetch(`/api/v1/bookings/${bookingId}/confirm`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ note: note })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Không thể duyệt: " + (err.detail || "Thất bại"));
        return;
      }

      this.closeModal('confirm-booking-modal');
      this.showToast("Đã xác nhận giữ chỗ và trừ số chỗ ngồi thành công!", "success");
      await this.fetchInitialData();
      this.renderQueueTable();
      this.updateQueueBadge();
    } catch (e) {
      console.error(e);
    }
  },

  promptRejectBooking: async function(bookingId) {
    const reason = prompt("Nhập lý do từ chối yêu cầu đặt tour này:");
    if (!reason) return;

    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/bookings/${bookingId}/reject?reason=${encodeURIComponent(reason)}`, {
        method: 'POST',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể từ chối"));
        return;
      }

      this.showToast("Đã từ chối đơn yêu cầu.", "info");
      await this.fetchInitialData();
      this.renderQueueTable();
      this.updateQueueBadge();
    } catch (e) {
      console.error(e);
    }
  },

  // ==================== ADMIN USER MANAGEMENT ====================
  openAddUserModal: function() {
    document.getElementById('user-modal-title').innerText = "Thêm Tài Khoản Mới";
    document.getElementById('user-form-id').value = '';
    document.getElementById('user-form-username-box').style.display = '';
    document.getElementById('user-form-username').value = '';
    document.getElementById('user-form-fullname').value = '';
    document.getElementById('user-form-role').value = 'CONSULTANT';
    document.getElementById('user-form-phone').value = '';
    document.getElementById('user-form-email').value = '';
    document.getElementById('user-form-password').value = '';
    const modal = document.getElementById('user-modal');
    if (modal) modal.classList.remove('hidden');
  },

  openEditUserModal: function(userId) {
    const user = this.users.find(u => u.id === userId);
    if (!user) return;

    document.getElementById('user-modal-title').innerText = `Chỉnh Sửa Tài Khoản @${user.username}`;
    document.getElementById('user-form-id').value = user.id;
    document.getElementById('user-form-username-box').style.display = 'none';
    document.getElementById('user-form-fullname').value = user.full_name;
    document.getElementById('user-form-role').value = user.role;
    document.getElementById('user-form-phone').value = user.phone || '';
    document.getElementById('user-form-email').value = user.email || '';
    document.getElementById('user-form-password').value = '';
    const modal = document.getElementById('user-modal');
    if (modal) modal.classList.remove('hidden');
  },

  submitUserForm: async function() {
    const userId = document.getElementById('user-form-id').value;
    const fullname = document.getElementById('user-form-fullname').value.trim();
    const role = document.getElementById('user-form-role').value;
    const phone = document.getElementById('user-form-phone').value.trim();
    const email = document.getElementById('user-form-email').value.trim();
    const password = document.getElementById('user-form-password').value.trim();

    if (!fullname) {
      alert("Vui lòng nhập họ và tên!");
      return;
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`
    };

    try {
      if (!userId) {
        // Thêm mới
        const username = document.getElementById('user-form-username').value.trim();
        if (!username || !password) {
          alert("Vui lòng nhập tên đăng nhập và mật khẩu!");
          return;
        }
        const res = await fetch('/api/v1/users', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({
            username: username,
            password: password,
            full_name: fullname,
            role: role,
            phone: phone,
            email: email
          })
        });
        if (!res.ok) {
          const err = await res.json();
          alert("Lỗi tạo tài khoản: " + (err.detail || "Thất bại"));
          return;
        }
        this.showToast("Tạo tài khoản người dùng thành công!", "success");
      } else {
        // Cập nhật
        const updatePayload = {
          full_name: fullname,
          role: role,
          phone: phone,
          email: email
        };
        if (password) updatePayload.password = password;

        const res = await fetch(`/api/v1/users/${userId}`, {
          method: 'PUT',
          headers: headers,
          body: JSON.stringify(updatePayload)
        });
        if (!res.ok) {
          const err = await res.json();
          alert("Lỗi cập nhật: " + (err.detail || "Thất bại"));
          return;
        }
        this.showToast("Cập nhật thông tin và phân quyền thành công!", "success");
      }

      this.closeModal('user-modal');
      await this.fetchInitialData();
      this.renderUsersTable();
    } catch (e) {
      console.error(e);
      alert("Sự cố kết nối máy chủ.");
    }
  },

  deleteUser: async function(userId) {
    if (!confirm("Bạn có chắc chắn muốn xóa tài khoản này khỏi hệ thống?")) return;

    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/users/${userId}`, {
        method: 'DELETE',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể xóa"));
        return;
      }

      this.showToast("Đã xóa tài khoản.", "info");
      await this.fetchInitialData();
      this.renderUsersTable();
    } catch (e) {
      console.error(e);
    }
  },

  // ==================== OTHER ACTIONS & MODALS ====================
  openRecommendedDeparture: function(tourId, departureId) {
    if (this.isLoggedIn()) { this.openBookingModalForDep(departureId); return; }
    this.openGuestBookingModal();
    const select = document.getElementById('guest-dep-select');
    if (select) select.value = departureId;
  },

  openBookingModalForTour: function(tourId) {
    if (!this.isLoggedIn()) { this.openGuestBookingModalForTour(tourId); return; }
    const tour = this.tours.find(t => t.id === tourId);
    if (!tour) return;

    const modal = document.getElementById('booking-modal');
    if (!modal) return;

    const openDeps = this.departures.filter(d => d.tour_id === tourId && d.status === 'OPEN' && d.available_slots > 0 && d.departure_date >= new Date().toLocaleDateString('en-CA') && d.available_slots > 0);
    const depSelect = document.getElementById('modal-booking-dep-select');
    if (depSelect) {
      if (openDeps.length === 0) {
        depSelect.innerHTML = '<option value="">-- Tour này hiện tạm hết chỗ --</option>';
      } else {
        depSelect.innerHTML = openDeps.map(d => `
          <option value="${d.id}">Ngày khởi hành: ${d.departure_date} (Còn ${d.available_slots} chỗ) - ${(d.price_override ?? tour.base_price).toLocaleString('vi-VN')} đ</option>
        `).join('');
      }
    }

    document.getElementById('modal-booking-tour-name').innerText = `[${tour.code}] ${tour.title}`;
    document.getElementById('modal-booking-unit-price').value = tour.base_price;
    document.getElementById('modal-booking-num-people').value = 1;
    if (depSelect) {
      depSelect.onchange = () => this.calculateBookingTotal();
    }
    this.calculateBookingTotal();

    modal.classList.remove('hidden');
  },

  openBookingModalForDep: function(depId) {
    const dep = this.departures.find(d => d.id === depId);
    if (!dep) return;
    this.openBookingModalForTour(dep.tour_id);
    setTimeout(() => {
      const depSelect = document.getElementById('modal-booking-dep-select');
      if (depSelect) { depSelect.value = depId; this.calculateBookingTotal(); }
    }, 50);
  },

  calculateBookingTotal: function() {
    const selectedId = Number(document.getElementById('modal-booking-dep-select').value);
    const departure = this.departures.find(d => d.id === selectedId);
    const tour = departure && this.tours.find(t => t.id === departure.tour_id);
    const unitPrice = departure ? (departure.price_override ?? tour?.base_price ?? 0) : 0;
    document.getElementById('modal-booking-unit-price').value = unitPrice;
    const numPeople = Number(document.getElementById('modal-booking-num-people').value);
    if (!Number.isInteger(numPeople) || numPeople < 1) { this.showToast("Số khách phải là số nguyên dương.", "error"); return; }
    const total = unitPrice * numPeople;
    const deposit = Math.floor((total * 3 + 5) / 10);

    document.getElementById('modal-booking-total-display').innerText = total.toLocaleString('vi-VN') + ' đ';
    document.getElementById('modal-booking-deposit-display').innerText = deposit.toLocaleString('vi-VN') + ' đ (30%)';
    document.getElementById('modal-booking-initial-pay').value = this.currentUser?.role === 'ADMIN' ? deposit : 0;
    document.getElementById('modal-booking-initial-pay').disabled = this.currentUser?.role !== 'ADMIN';
  },

  submitBooking: async function() {
    const depId = parseInt(document.getElementById('modal-booking-dep-select').value);
    const name = document.getElementById('modal-booking-cust-name').value.trim();
    const phone = document.getElementById('modal-booking-cust-phone').value.trim();
    const email = document.getElementById('modal-booking-cust-email').value.trim();
    const numPeople = Number(document.getElementById('modal-booking-num-people').value);
    if (!Number.isInteger(numPeople) || numPeople < 1) { this.showToast("Số khách phải là số nguyên dương.", "error"); return; }
    const initialPay = parseFloat(document.getElementById('modal-booking-initial-pay').value) || 0;
    const method = document.getElementById('modal-booking-pay-method').value;

    if (!depId || !name || !phone) {
      alert("Vui lòng điền đủ thông tin!");
      return;
    }

    try {
      const res = await fetch('/api/v1/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
        body: JSON.stringify({
          departure_id: depId,
          customer_name: name,
          customer_phone: phone,
          customer_email: email,
          num_people: numPeople,
          initial_payment: initialPay,
          payment_method: method
        })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi đặt chỗ: " + (err.detail || "Thất bại"));
        return;
      }

      const booking = await res.json();
      this.closeModal('booking-modal');
      this.showToast(`Đặt chỗ thành công! Mã: ${booking.booking_code}`, 'success');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
    }
  },

  openCancelBookingModal: function(bookingId) {
    const booking = this.bookings.find(b => b.id === bookingId);
    if (!booking) return;

    const modal = document.getElementById('cancel-booking-modal');
    if (!modal) return;

    document.getElementById('cancel-modal-booking-code').innerText = booking.booking_code;
    document.getElementById('cancel-modal-booking-id').value = booking.id;
    document.getElementById('cancel-modal-paid-amount').innerText = booking.paid_amount.toLocaleString('vi-VN') + ' đ';

    modal.classList.remove('hidden');
  },

  submitCancelBooking: async function() {
    const bookingId = document.getElementById('cancel-modal-booking-id').value;
    const reason = document.getElementById('cancel-modal-reason').value.trim();

    if (!reason) {
      alert("Vui lòng nhập lý do hủy!");
      return;
    }

    try {
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      };
      const res = await fetch(`/api/v1/bookings/${bookingId}/cancel`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ reason: reason })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể hủy"));
        return;
      }

      const updated = await res.json();
      this.closeModal('cancel-booking-modal');
      this.showToast(`Hủy tour thành công! Tiền hoàn: ${updated.refund_amount.toLocaleString('vi-VN')} đ`, 'info');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
    }
  },

  homeTourKeyword: '',

  onHomeTourSearchChange: function() {
    const input = document.getElementById('home-tour-search-keyword');
    const clearBtn = document.getElementById('home-tour-clear-search');
    this.homeTourKeyword = input ? input.value : '';
    if (clearBtn) {
      clearBtn.classList.toggle('hidden', !this.homeTourKeyword);
    }
    this.renderTourCards();
  },

  clearHomeTourSearch: function() {
    const input = document.getElementById('home-tour-search-keyword');
    const clearBtn = document.getElementById('home-tour-clear-search');
    if (input) input.value = '';
    if (clearBtn) clearBtn.classList.add('hidden');
    this.homeTourKeyword = '';
    this.renderTourCards();
  },

  openDirectPaymentModal: function() {
    if (!['ADMIN', 'ACCOUNTANT'].includes(this.currentUser?.role)) {
      this.showToast('Chỉ Quản trị viên hoặc Kế toán mới được thu tiền.', 'error');
      return;
    }
    const unpaidBookings = this.bookings.filter(b => 
      ['PENDING', 'DEPOSITED', 'CONFIRMED'].includes(b.status) && 
      (b.total_amount - b.paid_amount) > 0
    );

    if (unpaidBookings.length === 0) {
      this.showToast('Hiện không có đơn đặt chỗ nào còn công nợ cần thu tiền.', 'info');
      return;
    }

    const selectEl = document.getElementById('direct-payment-booking-select');
    if (selectEl) {
      selectEl.innerHTML = unpaidBookings.map(b => {
        const remaining = b.total_amount - b.paid_amount;
        return `<option value="${b.id}">[${b.booking_code}] ${b.customer_name} (${b.customer_phone}) - Còn thiếu: ${remaining.toLocaleString('vi-VN')} đ</option>`;
      }).join('');
      this.onDirectPaymentBookingChange();
    }
    this.openModal('direct-payment-modal');
  },

  onDirectPaymentBookingChange: function() {
    const selectEl = document.getElementById('direct-payment-booking-select');
    const infoEl = document.getElementById('direct-payment-info');
    if (!selectEl || !infoEl) return;
    const bookingId = parseInt(selectEl.value);
    const booking = this.bookings.find(b => b.id === bookingId);
    if (!booking) {
      infoEl.innerHTML = '';
      return;
    }
    const remaining = booking.total_amount - booking.paid_amount;
    const dep = this.departures.find(d => d.id === booking.departure_id);
    const tour = this.tours.find(t => t.id === dep?.tour_id);

    infoEl.innerHTML = `
      <div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl space-y-1 text-xs">
        <div class="flex justify-between"><span class="text-slate-500">Tour:</span><strong class="text-slate-800 dark:text-slate-200">${tour?.title || 'Tour du lịch'}</strong></div>
        <div class="flex justify-between"><span class="text-slate-500">Khách hàng:</span><span class="font-semibold">${booking.customer_name} (${booking.customer_phone})</span></div>
        <div class="flex justify-between"><span class="text-slate-500">Số khách:</span><span>${booking.num_people} khách</span></div>
        <div class="flex justify-between"><span class="text-slate-500">Đã thanh toán:</span><span class="text-emerald-600 font-bold">${booking.paid_amount.toLocaleString('vi-VN')} đ</span></div>
        <div class="flex justify-between border-t border-slate-200 dark:border-slate-700 pt-1"><span class="text-slate-500 font-bold">Số tiền còn thiếu:</span><strong class="text-rose-600 text-sm">${remaining.toLocaleString('vi-VN')} đ</strong></div>
      </div>
    `;
  },

  submitDirectPaymentChoice: function() {
    const selectEl = document.getElementById('direct-payment-booking-select');
    if (!selectEl || !selectEl.value) return;
    const bookingId = parseInt(selectEl.value);
    const booking = this.bookings.find(b => b.id === bookingId);
    if (!booking) return;
    this.closeModal('direct-payment-modal');
    this.openPaymentModal(booking.id, booking.total_amount - booking.paid_amount);
  },
  openPaymentModal: function(bookingId, remainingAmount) {
    if (!['ADMIN', 'ACCOUNTANT'].includes(this.currentUser?.role)) { this.showToast('Chỉ Admin hoặc kế toán được thu tiền.', 'error'); return; }
    const modal = document.getElementById('add-payment-modal');
    if (!modal) return;

    document.getElementById('payment-modal-booking-id').value = bookingId;
    document.getElementById('payment-modal-amount').value = remainingAmount;
    document.getElementById('payment-modal-remaining-display').innerText = remainingAmount.toLocaleString('vi-VN') + ' đ';

    modal.classList.remove('hidden');
  },

  submitPayment: async function() {
    const bookingId = parseInt(document.getElementById('payment-modal-booking-id').value);
    const amount = parseFloat(document.getElementById('payment-modal-amount').value);
    const method = document.getElementById('payment-modal-method').value;
    const type = document.getElementById('payment-modal-type').value;

    if (!amount || amount <= 0) {
      alert("Vui lòng nhập số tiền hợp lệ!");
      return;
    }

    try {
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      };
      const res = await fetch('/api/v1/payments', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          booking_id: bookingId,
          amount: amount,
          payment_type: type,
          payment_method: method,
          note: "Ghi nhận thanh toán kế toán"
        })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi thanh toán: " + (err.detail || "Thất bại"));
        return;
      }

      this.closeModal('add-payment-modal');
      this.showToast("Ghi nhận thanh toán thành công!", "success");
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
    }
  },

  openTourDetailsModal: function(tourId) {
    const tour = this.tours.find(t => t.id === tourId);
    if (!tour) return;

    const modal = document.getElementById('tour-details-modal');
    if (!modal) return;

    document.getElementById('tour-detail-title').innerText = tour.title;
    document.getElementById('tour-detail-code').innerText = tour.code;
    document.getElementById('tour-detail-dest').innerText = `${tour.destination} • ${tour.duration_days}N${tour.duration_nights}Đ`;
    document.getElementById('tour-detail-price').innerText = tour.base_price.toLocaleString('vi-VN') + ' đ';
    document.getElementById('tour-detail-desc').innerText = tour.description || 'Chưa có mô tả.';
    document.getElementById('tour-detail-itinerary').innerText = tour.itinerary_summary || 'Chưa có lịch trình tóm tắt.';
    document.getElementById('tour-detail-highlights').innerText = tour.highlights || 'Không có ghi chú.';
    document.getElementById('tour-detail-img').src = tour.image_url || 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80';

    modal.classList.remove('hidden');
  },

  openAddTourModal: function(isDraft = false) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      this.showToast("Chỉ Quản trị viên (Admin) mới có quyền tạo hoặc chỉnh sửa tour!", "error");
      return;
    }
    const modal = document.getElementById('add-tour-modal');
    if (modal) {
      if (!isDraft) {
        ['tour-form-code', 'tour-form-title', 'tour-form-destination', 'tour-form-price', 'tour-form-description', 'tour-form-itinerary', 'tour-form-highlights', 'tour-form-img'].forEach(id => {
          const el = document.getElementById(id);
          if (el) el.value = '';
        });
      }
      modal.classList.remove('hidden');
      const depDateInput = document.getElementById('tour-form-dep-date');
      const chk = document.getElementById('tour-form-create-dep');
      if (chk) chk.checked = true;
      this.toggleInitialDepartureFields();
      if (depDateInput && !depDateInput.value) {
        const d = new Date();
        d.setDate(d.getDate() + 3);
        depDateInput.value = d.toISOString().split('T')[0];
        this.calcTourReturnDate();
      }
    }
  },

  toggleInitialDepartureFields: function() {
    const chk = document.getElementById('tour-form-create-dep');
    const fields = document.getElementById('tour-form-dep-fields');
    if (!chk || !fields) return;
    fields.style.display = chk.checked ? 'grid' : 'none';
  },

  calcTourReturnDate: function() {
    const depDateInput = document.getElementById('tour-form-dep-date');
    const returnDateInput = document.getElementById('tour-form-return-date');
    const daysInput = document.getElementById('tour-form-days');
    if (!depDateInput || !returnDateInput || !depDateInput.value) return;

    const days = parseInt(daysInput ? daysInput.value : 3) || 3;
    const depDate = new Date(depDateInput.value);
    const retDate = new Date(depDate);
    retDate.setDate(retDate.getDate() + Math.max(0, days - 1));
    returnDateInput.value = retDate.toISOString().split('T')[0];
  },

  generateTourContentWithAI: async function() {
    const title = document.getElementById('tour-form-title') ? document.getElementById('tour-form-title').value.trim() : '';
    const destination = document.getElementById('tour-form-destination') ? document.getElementById('tour-form-destination').value.trim() : '';
    const days = parseInt(document.getElementById('tour-form-days')?.value) || 3;
    const nights = parseInt(document.getElementById('tour-form-nights')?.value) || 2;
    const highlights = document.getElementById('tour-form-highlights')?.value.trim();

    if (!title && !destination) {
      alert("Vui lòng nhập Tên tour hoặc Điểm đến trước để AI có cơ sở sinh nội dung!");
      return;
    }

    const btn = document.getElementById('btn-modal-ai-gen');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Đang soạn thảo...';
    }

    try {
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      };
      const res = await fetch('/api/v1/ai/generate-description', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          tour_title: title || `Du lịch ${destination}`,
          destination: destination || title,
          duration_days: days,
          duration_nights: nights,
          highlights: highlights || null,
          target_audience: "Gia đình, bạn bè hoặc khách du lịch"
        })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi AI: " + (err.detail || "Không thể sinh nội dung"));
        return;
      }

      const data = await res.json();
      if (document.getElementById('tour-form-description') && data.description) {
        document.getElementById('tour-form-description').value = data.description;
      }
      if (document.getElementById('tour-form-itinerary') && data.itinerary_summary) {
        document.getElementById('tour-form-itinerary').value = data.itinerary_summary;
      }
      if (document.getElementById('tour-form-highlights') && data.marketing_slogan && !highlights) {
        document.getElementById('tour-form-highlights').value = data.marketing_slogan;
      }
      this.showToast("AI Gemini đã tự động điền mô tả & lịch trình tour!", "success");
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối tới Trợ lý AI!");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  },

  submitNewTour: async function() {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền tạo hoặc chỉnh sửa tour!");
      return;
    }

    const code = document.getElementById('tour-form-code').value.trim();
    const title = document.getElementById('tour-form-title').value.trim();
    const destination = document.getElementById('tour-form-destination').value.trim();
    const category = document.getElementById('tour-form-category').value;
    const days = parseInt(document.getElementById('tour-form-days').value) || 3;
    const nights = parseInt(document.getElementById('tour-form-nights').value) || 2;
    const price = parseFloat(document.getElementById('tour-form-price').value) || 0;
    const desc = document.getElementById('tour-form-description').value.trim();
    const itinerary = document.getElementById('tour-form-itinerary').value.trim();
    const highlights = document.getElementById('tour-form-highlights').value.trim();
    const img = document.getElementById('tour-form-img').value.trim();

    if (!code || !title || !destination || price <= 0) {
      alert("Vui lòng điền đủ thông tin tour!");
      return;
    }

    const createDep = document.getElementById('tour-form-create-dep') ? document.getElementById('tour-form-create-dep').checked : false;
    let depDate = '';
    let returnDate = '';
    let totalSlots = 25;

    if (createDep) {
      depDate = document.getElementById('tour-form-dep-date')?.value;
      returnDate = document.getElementById('tour-form-return-date')?.value;
      totalSlots = parseInt(document.getElementById('tour-form-total-slots')?.value) || 25;
      if (!depDate || !returnDate || totalSlots <= 0) {
        alert("Vui lòng điền ngày khởi hành, ngày về và tổng số chỗ hợp lệ cho đợt khởi hành đầu tiên!");
        return;
      }
    }

    try {
      const headers = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      };
      const res = await fetch('/api/v1/tours', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          code: code,
          title: title,
          destination: destination,
          category: category,
          duration_days: days,
          duration_nights: nights,
          base_price: price,
          description: desc,
          itinerary_summary: itinerary,
          highlights: highlights,
          image_url: img || 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80'
        })
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể tạo tour"));
        return;
      }

      const createdTour = await res.json();

      // Nếu có chọn mở đợt khởi hành đầu tiên kèm tổng số chỗ
      if (createDep && createdTour && createdTour.id) {
        try {
          const depRes = await fetch('/api/v1/departures', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
              tour_id: createdTour.id,
              departure_date: depDate,
              return_date: returnDate,
              total_slots: totalSlots,
              available_slots: totalSlots,
              status: 'OPEN',
              notes: 'Đợt khởi hành đầu tiên tạo cùng tour'
            })
          });
          if (!depRes.ok) {
            const depErr = await depRes.json();
            console.warn("Lỗi tạo đợt khởi hành:", depErr);
            this.showToast("Đã tạo tour, nhưng chưa tạo được lịch đi: " + (depErr.detail || ""), "warning");
          } else {
            this.showToast(`Tạo tour [${createdTour.code}] & mở đợt khởi hành (${totalSlots} chỗ) thành công!`, "success");
          }
        } catch (depErr) {
          console.error("Lỗi gọi API departure:", depErr);
          this.showToast("Đã tạo tour nhưng gặp sự cố khi tạo lịch đi.", "warning");
        }
      } else {
        this.showToast("Tạo tour mới thành công!", "success");
      }

      this.closeModal('add-tour-modal');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
      alert("Đã xảy ra lỗi hệ thống khi lưu tour!");
    }
  },


  deleteBooking: async function(bookingId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Chỉ Quản trị viên mới có quyền xóa vĩnh viễn đặt chỗ!");
      return;
    }
    const booking = this.bookings.find(b => b.id === bookingId);
    const code = booking ? booking.booking_code : bookingId;
    if (!confirm(`Bạn có chắc chắn muốn XÓA VĨNH VIỄN đặt chỗ [${code}]?\n\nHệ thống sẽ xóa phiếu thu liên quan và hoàn trả số ghế (nếu có). Hành động này không thể hoàn tác.`)) {
      return;
    }
    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/bookings/${bookingId}`, { method: 'DELETE', headers });
      if (res.ok) {
        this.showToast(`Đã xóa vĩnh viễn đặt chỗ [${code}]!`, "success");
        await this.fetchInitialData();
        this.renderCurrentView();
      } else {
        const err = await res.json();
        alert("Lỗi xóa đặt chỗ: " + (err.detail || "Thất bại"));
      }
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối khi xóa đặt chỗ!");
    }
  },

  currentDepCustomerPhones: [],
  currentViewingDepId: null,

  openDepartureCustomersModal: async function(depId) {
    if (!this.isLoggedIn()) {
      alert("Vui lòng đăng nhập để xem danh sách khách hàng!");
      return;
    }
    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/departures/${depId}/customers`, { headers });
      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi tải danh sách khách: " + (err.detail || "Thất bại"));
        return;
      }
      const data = await res.json();
      this.currentViewingDepId = depId;
      this.currentDepCustomerPhones = data.customers.map(c => c.customer_phone).filter(p => p && p !== 'N/A');

      document.getElementById('dep-cust-modal-title').innerText = `Danh Sách Khách Hàng - [${data.tour_code}] ${data.tour_title}`;
      document.getElementById('dep-cust-modal-subtitle').innerText = `Khởi hành: ${data.departure_date} → ${data.return_date} • Trạng thái: ${data.status}`;
      document.getElementById('dep-cust-count-badge').innerText = `Tổng: ${data.booked_count} đơn (${data.total_slots - data.available_slots} / ${data.total_slots} chỗ)`;

      const cancelBtn = document.getElementById('btn-emergency-cancel-dep');
      if (cancelBtn) {
        cancelBtn.style.display = (this.currentUser?.role === 'ADMIN' && data.status !== 'CANCELLED') ? '' : 'none';
        cancelBtn.onclick = () => this.submitEmergencyDepartureCancel(depId, data.tour_title, data.departure_date);
      }

      const tbody = document.getElementById('dep-customers-table-body');
      if (tbody) {
        if (data.customers.length === 0) {
          tbody.innerHTML = '<tr><td colspan="8" class="text-center py-6 text-slate-400">Chưa có khách hàng nào đặt chỗ cho đợt khởi hành này.</td></tr>';
        } else {
          tbody.innerHTML = data.customers.map(c => `
            <tr class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <td class="py-2.5 px-3 font-mono font-bold text-sky-600 dark:text-sky-400">${c.booking_code}</td>
              <td class="py-2.5 px-3 font-semibold text-slate-800 dark:text-slate-200">${c.customer_name}</td>
              <td class="py-2.5 px-3 font-mono text-slate-700 dark:text-slate-300">
                <a href="tel:${c.customer_phone}" class="hover:underline text-sky-600 flex items-center space-x-1">
                  <i class="fa-solid fa-phone text-[10px]"></i>
                  <span>${c.customer_phone}</span>
                </a>
              </td>
              <td class="py-2.5 px-3 font-bold text-center">${c.num_people}</td>
              <td class="py-2.5 px-3">${c.total_amount.toLocaleString('vi-VN')} đ</td>
              <td class="py-2.5 px-3 font-bold text-emerald-600">${c.paid_amount.toLocaleString('vi-VN')} đ</td>
              <td class="py-2.5 px-3">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${c.status === 'CANCELLED' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}">${c.status}</span>
              </td>
              <td class="py-2.5 px-3 text-right">
                <a href="tel:${c.customer_phone}" class="px-2 py-1 bg-sky-50 text-sky-600 hover:bg-sky-100 dark:bg-sky-950/40 rounded-lg text-xs font-semibold mr-1" title="Gọi điện">
                  <i class="fa-solid fa-phone"></i>
                </a>
                <button onclick="navigator.clipboard.writeText('${c.customer_phone}'); window.App.showToast('Đã sao chép SĐT: ${c.customer_phone}', 'info');" class="px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 hover:bg-slate-200 rounded-lg text-xs" title="Sao chép SĐT">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </td>
            </tr>
          `).join('');
        }
      }

      this.openModal('departure-customers-modal');
    } catch (e) {
      console.error(e);
      alert("Lỗi tải thông tin khách hàng!");
    }
  },

  copyAllCustomerPhones: function() {
    if (!this.currentDepCustomerPhones || this.currentDepCustomerPhones.length === 0) {
      this.showToast("Không có số điện thoại nào để sao chép.", "warning");
      return;
    }
    const text = this.currentDepCustomerPhones.join(', ');
    navigator.clipboard.writeText(text);
    this.showToast(`Đã sao chép ${this.currentDepCustomerPhones.length} SĐT khách hàng vào bộ nhớ tạm!`, "success");
  },

  submitEmergencyDepartureCancel: async function(depId, tourTitle, depDate) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Chỉ Quản trị viên mới có quyền hủy chuyến khẩn cấp!");
      return;
    }
    const reason = prompt(`XÁC NHẬN HỦY CHUYẾN KHẨN CẤP:\nTour: ${tourTitle}\nNgày khởi hành: ${depDate}\n\nVui lòng nhập lý do hủy (VD: Bão số 7 cấm tàu, thời tiết xấu, sự cố đột xuất...):`);
    if (!reason || !reason.trim()) {
      alert("Bạn phải nhập lý do hủy chuyến khẩn cấp!");
      return;
    }

    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/departures/${depId}/cancel-emergency?reason=${encodeURIComponent(reason.trim())}`, {
        method: 'POST',
        headers
      });
      if (res.ok) {
        const result = await res.json();
        alert(result.message);
        this.closeModal('departure-customers-modal');
        await this.fetchInitialData();
        this.renderCurrentView();
      } else {
        const err = await res.json();
        alert("Lỗi hủy chuyến khẩn cấp: " + (err.detail || "Thất bại"));
      }
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối khi gửi lệnh hủy chuyến!");
    }
  },

  deleteTour: async function(tourId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền xóa tour!");
      return;
    }
    const tour = this.tours.find(t => t.id === tourId);
    const tourName = tour ? `[${tour.code}] ${tour.title}` : `Tour #${tourId}`;
    if (!confirm(`Bạn có chắc chắn muốn xóa ${tourName}?`)) return;
    try {
      const headers = { 'Authorization': `Bearer ${this.token}` };
      const res = await fetch(`/api/v1/tours/${tourId}`, { method: 'DELETE', headers });
      if (res.ok) {
        this.showToast("Đã xóa tour thành công!", "info");
        await this.fetchInitialData();
        this.renderCurrentView();
      } else {
        const err = await res.json();
        if (err.detail && (err.detail.includes("đặt chỗ") || err.detail.includes("Force Delete") || err.detail.includes("cưỡng chế"))) {
          if (confirm(err.detail + "\n\nBạn có chắc muốn XÓA CƯỠNG CHẾ (Force Delete) toàn bộ tour này cùng tất cả các lịch khởi hành và đặt chỗ liên quan? (Hãy đảm bảo đã liên hệ hoàn tiền cho khách hàng trước khi xóa)")) {
            const forceRes = await fetch(`/api/v1/tours/${tourId}?force=true`, { method: 'DELETE', headers });
            if (forceRes.ok) {
              this.showToast("Đã xóa cưỡng chế tour và dữ liệu liên quan thành công!", "success");
              await this.fetchInitialData();
              this.renderCurrentView();
            } else {
              const forceErr = await forceRes.json();
              alert("Lỗi xóa cưỡng chế: " + (forceErr.detail || "Thất bại"));
            }
          }
        } else {
          alert("Lỗi xóa tour: " + (err.detail || "Thất bại"));
        }
      }
    } catch (e) {
      console.error(e);
      alert("Lỗi kết nối khi xóa tour!");
    }
  },

  // ==================== QUẢN LÝ ĐỢT KHỞI HÀNH & HDV ====================
  openAddDepartureModal: function(preselectedTourId, preselectedGuideId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      this.showToast("Chỉ Quản trị viên (Admin) mới có quyền tạo lịch khởi hành!", "error");
      return;
    }

    const modal = document.getElementById('departure-modal');
    if (!modal) return;

    document.getElementById('dep-modal-title').innerText = 'Mở Đợt Khởi Hành Mới';
    document.getElementById('dep-form-id').value = '';

    // Điền danh sách tour vào select
    const tourSelect = document.getElementById('dep-form-tour-id');
    if (tourSelect) {
      tourSelect.disabled = false;
      tourSelect.innerHTML = this.tours.map(t => `
        <option value="${t.id}" ${preselectedTourId && Number(preselectedTourId) === Number(t.id) ? 'selected' : ''}>[${t.code}] ${t.title}</option>
      `).join('');
    }

    // Thiết lập ngày khởi hành mặc định (ngày mai -> +3 ngày)
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const returnDay = new Date(tomorrow);
    returnDay.setDate(tomorrow.getDate() + 3);

    const depDateInput = document.getElementById('dep-form-dep-date');
    const returnDateInput = document.getElementById('dep-form-return-date');
    if (depDateInput) depDateInput.value = tomorrow.toISOString().split('T')[0];
    if (returnDateInput) returnDateInput.value = returnDay.toISOString().split('T')[0];

    document.getElementById('dep-form-total-slots').value = 20;
    document.getElementById('dep-form-price').value = '';
    document.getElementById('dep-form-status').value = 'OPEN';
    document.querySelectorAll('#dep-form-status option').forEach(option => { option.disabled = option.value !== 'OPEN'; });
    document.getElementById('dep-form-notes').value = '';

    // Điền danh sách HDV
    this.populateDepartureGuideOptions(preselectedGuideId || '');

    const alertBox = document.getElementById('dep-guide-conflict-alert');
    if (alertBox) {
      alertBox.className = 'hidden';
      alertBox.innerHTML = '';
    }

    this.openModal('departure-modal');
    this.checkGuideConflictLive();
  },

  openAssignTourForGuide: function(guideId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      this.showToast("Chỉ Quản trị viên (Admin) mới có quyền phân công tour cho hướng dẫn viên!", "error");
      return;
    }

    const guide = this.guides.find(g => g.id === guideId);
    this.openAddDepartureModal(null, guideId);
    if (guide) {
      const modalTitle = document.getElementById('dep-modal-title');
      if (modalTitle) {
        modalTitle.innerText = `Phân Công Tour Cho HDV: ${guide.full_name}`;
      }
    }
  },

  openEditDepartureModal: function(depId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      this.showToast("Chỉ Quản trị viên (Admin) mới có quyền chỉnh sửa lịch khởi hành!", "error");
      return;
    }

    const dep = this.departures.find(d => d.id === depId);
    if (!dep) return;

    const modal = document.getElementById('departure-modal');
    if (!modal) return;

    document.getElementById('dep-modal-title').innerText = `Chỉnh Sửa Đợt Khởi Hành #${dep.id} (${dep.tour_code || ''})`;
    document.getElementById('dep-form-id').value = dep.id;

    // Điền tour
    const tourSelect = document.getElementById('dep-form-tour-id');
    if (tourSelect) {
      tourSelect.disabled = true;
      tourSelect.innerHTML = this.tours.map(t => `
        <option value="${t.id}" ${dep.tour_id === t.id ? 'selected' : ''}>[${t.code}] ${t.title}</option>
      `).join('');
    }

    document.getElementById('dep-form-dep-date').value = dep.departure_date;
    document.getElementById('dep-form-return-date').value = dep.return_date;
    document.getElementById('dep-form-total-slots').value = dep.total_slots;
    document.getElementById('dep-form-price').value = dep.price_override ?? '';
    document.getElementById('dep-form-status').value = dep.status;
    document.querySelectorAll('#dep-form-status option').forEach(option => { option.disabled = option.value !== dep.status && !(['OPEN', 'FULL'].includes(dep.status) && option.value === 'CANCELLED'); });
    document.getElementById('dep-form-notes').value = dep.notes || '';

    // Điền danh sách HDV với giá trị đã chọn
    this.populateDepartureGuideOptions(dep.guide_id || '');

    this.openModal('departure-modal');
    this.checkGuideConflictLive();
  },

  populateDepartureGuideOptions: function(selectedGuideId) {
    const guideSelect = document.getElementById('dep-form-guide-id');
    const filterGuideSelect = document.getElementById('dep-filter-guide');

    let options = '<option value="">-- Chưa phân công HDV --</option>';
    let filterOptions = '<option value="ALL">Tất cả hướng dẫn viên</option>';

    if (this.guides && this.guides.length > 0) {
      options += this.guides.map(g => {
        const isSelected = selectedGuideId && String(selectedGuideId) === String(g.id);
        const statusLabel = g.status === 'AVAILABLE' ? 'Sẵn sàng' :
                            g.status === 'ON_TOUR' ? 'Đang đi tour' :
                            g.status === 'OFF' ? 'Nghỉ phép' : g.status;
        const name = g.full_name || g.name || `HDV #${g.id}`;
        const code = g.code || `HDV-${String(g.id).padStart(2, '0')}`;
        return `<option value="${g.id}" ${isSelected ? 'selected' : ''}>${name} (${code}) [${statusLabel}]</option>`;
      }).join('');

      filterOptions += this.guides.map(g => {
        const name = g.full_name || g.name || `HDV #${g.id}`;
        return `<option value="${g.id}">${name}</option>`;
      }).join('');
    }
    if (guideSelect) guideSelect.innerHTML = options;
    if (filterGuideSelect && filterGuideSelect.options.length <= 1) filterGuideSelect.innerHTML = filterOptions;
  },

  checkGuideConflictLive: async function() {
    const guideId = document.getElementById('dep-form-guide-id')?.value;
    const depDate = document.getElementById('dep-form-dep-date')?.value;
    const returnDate = document.getElementById('dep-form-return-date')?.value;
    const depId = document.getElementById('dep-form-id')?.value;
    const alertBox = document.getElementById('dep-guide-conflict-alert');
    const submitBtn = document.getElementById('btn-submit-departure');

    if (!alertBox) return;

    if (!guideId || !depDate || !returnDate) {
      alertBox.className = 'hidden';
      alertBox.innerHTML = '';
      if (submitBtn) submitBtn.disabled = false;
      return;
    }

    if (returnDate < depDate) {
      alertBox.className = 'p-3 rounded-xl border bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-300 block';
      alertBox.innerHTML = '<i class="fa-solid fa-circle-exclamation mr-1.5"></i> <strong>Lỗi thời gian:</strong> Ngày về không được trước ngày khởi hành.';
      if (submitBtn) submitBtn.disabled = true;
      return;
    }

    try {
      let url = `/api/v1/departures/check-conflict?guide_id=${guideId}&departure_date=${depDate}&return_date=${returnDate}`;
      if (depId) url += `&exclude_dep_id=${depId}`;

      const res = await fetch(url);
      const data = await res.json();

      if (data.has_conflict) {
        alertBox.className = 'p-3 rounded-xl border bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-300 block leading-relaxed';
        alertBox.innerHTML = `
          <div class="font-bold flex items-center space-x-1.5 text-rose-800 dark:text-rose-200">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>CẢNH BÁO TRÙNG LỊCH HDV!</span>
          </div>
          <div class="mt-1">${data.message || 'Hướng dẫn viên đã có lịch trình khác trong khoảng ngày này.'}</div>
          <div class="text-[10px] text-rose-600 dark:text-rose-400 mt-0.5 font-semibold">Vui lòng chọn hướng dẫn viên khác hoặc điều chỉnh ngày khởi hành/ngày về.</div>
        `;
        if (submitBtn) submitBtn.disabled = true;
      } else {
        alertBox.className = 'p-2.5 rounded-xl border bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 block';
        alertBox.innerHTML = `
          <div class="flex items-center space-x-1.5 font-medium">
            <i class="fa-solid fa-circle-check text-emerald-600"></i>
            <span>Lịch trình hợp lệ: Hướng dẫn viên sẵn sàng và không bị trùng lịch nào trong thời gian này.</span>
          </div>
        `;
        if (submitBtn) submitBtn.disabled = false;
      }
    } catch (e) {
      console.error("Conflict check error:", e);
    }
  },

  submitDepartureForm: async function() {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền thêm hoặc sửa lịch khởi hành!");
      return;
    }

    const depId = document.getElementById('dep-form-id').value;
    const tourId = parseInt(document.getElementById('dep-form-tour-id').value);
    const depDate = document.getElementById('dep-form-dep-date').value;
    const returnDate = document.getElementById('dep-form-return-date').value;
    const totalSlots = parseInt(document.getElementById('dep-form-total-slots').value) || 20;
    const price = document.getElementById('dep-form-price').value ? parseFloat(document.getElementById('dep-form-price').value) : null;
    const guideIdVal = document.getElementById('dep-form-guide-id').value;
    const guideId = guideIdVal ? parseInt(guideIdVal) : null;
    const status = document.getElementById('dep-form-status').value || 'OPEN';
    const notes = document.getElementById('dep-form-notes').value.trim();

    if (!tourId || !depDate || !returnDate) {
      alert("Vui lòng chọn tour và nhập đầy đủ ngày khởi hành, ngày về!");
      return;
    }

    if (returnDate < depDate) {
      alert("Ngày về không được trước ngày khởi hành!");
      return;
    }

    const payload = {
      tour_id: tourId,
      departure_date: depDate,
      return_date: returnDate,
      total_slots: totalSlots,
      price_override: price,
      guide_id: guideId,
      status: status,
      notes: notes
    };
    if (depId) delete payload.tour_id;

    try {
      const headers = {
        'Content-Type': 'application/json',
        ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
      };

      const url = depId ? `/api/v1/departures/${depId}` : '/api/v1/departures';
      const method = depId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method: method,
        headers: headers,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        alert("Lỗi: " + (err.detail || "Không thể lưu đợt khởi hành"));
        return;
      }

      this.closeModal('departure-modal');
      this.showToast(depId ? "Cập nhật đợt khởi hành thành công!" : "Mở đợt khởi hành mới thành công!", "success");
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
      alert("Đã xảy ra lỗi: " + e.message);
    }
  },

  startDeparture: async function(depId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền khởi hành chuyến đi!");
      return;
    }

    const dep = this.departures.find(d => d.id === depId);
    const tourName = dep ? dep.tour_title : `Mã #${depId}`;
    const guideMsg = dep && dep.guide_name ? ` cùng Hướng dẫn viên ${dep.guide_name}` : ' (Chưa có HDV phụ trách)';

    if (!confirm(`Bạn có chắc chắn muốn KHỞI HÀNH chuyến đi:\n"${tourName}"${guideMsg}?\n\nTrạng thái sẽ chuyển sang "Đang khởi hành" (RUNNING) và Hướng dẫn viên sẽ cập nhật trạng thái "On Tour".`)) {
      return;
    }

    try {
      const headers = this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
      const res = await fetch(`/api/v1/departures/${depId}/start`, {
        method: 'POST',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert('Lỗi khởi hành: ' + (err.detail || 'Không thể khởi hành đợt này'));
        return;
      }

      this.showToast('Khởi hành chuyến đi thành công! HDV đã chuyển sang "On Tour".', 'success');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
      alert('Đã xảy ra lỗi: ' + e.message);
    }
  },

  completeDeparture: async function(depId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền kết thúc chuyến đi!");
      return;
    }

    const dep = this.departures.find(d => d.id === depId);
    const tourName = dep ? dep.tour_title : `Mã #${depId}`;

    if (!confirm(`Xác nhận KẾT THÚC chuyến đi:\n"${tourName}"?\n\nTrạng thái sẽ chuyển sang "Hoàn thành" (COMPLETED) và HDV sẽ tự động trở về trạng thái "Sẵn sàng" (AVAILABLE).`)) {
      return;
    }

    try {
      const headers = this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
      const res = await fetch(`/api/v1/departures/${depId}/complete`, {
        method: 'POST',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert('Lỗi: ' + (err.detail || 'Không thể hoàn thành chuyến đi'));
        return;
      }

      this.showToast('Kết thúc chuyến đi thành công! HDV đã trở về trạng thái Sẵn sàng.', 'success');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
      alert('Đã xảy ra lỗi: ' + e.message);
    }
  },

  deleteDeparture: async function(depId) {
    if (!this.currentUser || this.currentUser.role !== 'ADMIN') {
      alert("Từ chối truy cập: Bạn không có quyền xóa đợt khởi hành!");
      return;
    }

    if (!confirm('Bạn có chắc chắn muốn xóa đợt khởi hành này? Chú ý: Đợt có khách đặt chỗ sẽ không thể xóa.')) return;
    try {
      const headers = this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
      const res = await fetch(`/api/v1/departures/${depId}`, {
        method: 'DELETE',
        headers: headers
      });

      if (!res.ok) {
        const err = await res.json();
        alert('Không thể xóa: ' + (err.detail || 'Lỗi hệ thống'));
        return;
      }

      this.showToast('Đã xóa đợt khởi hành thành công', 'info');
      await this.fetchInitialData();
      this.renderCurrentView();
    } catch (e) {
      console.error(e);
    }
  },

  goToAISubTab: function(subTab) {
    if (this.currentTab === 'ai' && window.AIHub) {
      window.AIHub.switchSubTab(subTab);
    } else {
      localStorage.setItem('vietjourney_ai_subtab', subTab);
      this.navigate('/ai');
    }
  },

  sendFloatingAIMessage: function() {
    const input = document.getElementById('quick-ai-input');
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;
    input.value = '';
    this.toggleFloatingAI();
    if (this.currentTab === 'ai' && window.AIHub) {
      window.AIHub.handleConsultSend(val);
    } else {
      sessionStorage.setItem('vietjourney_pending_ai_query', val);
      this.navigate('/ai');
    }
  },

  toggleFloatingAI: function() {
    const drawer = document.getElementById('floating-ai-drawer');
    if (!drawer) return;
    drawer.classList.toggle('hidden');
  },

  showToast: function(message, type = 'info') {
    const toast = document.createElement('div');
    const bg = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-sky-600';
    toast.className = `fixed bottom-6 left-1/2 -translate-x-1/2 ${bg} text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg z-50 animate-fade-in flex items-center space-x-2`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3500);
  },

  setupEventListeners: function() {
    document.querySelectorAll('.category-tab-btn').forEach(btn => {
      btn.onclick = () => this.setCategoryFilter(btn.dataset.category);
    });

    document.querySelectorAll('.sidebar-nav-item').forEach(btn => {
      btn.onclick = (e) => {
        const sb = document.getElementById('main-sidebar');
        if (sb && innerWidth < 768) {
          sb.classList.remove('sidebar-open');
        }
        // Cho phép trình duyệt mở tab mới khi người dùng nhấn Ctrl+Click, Cmd+Click, Shift+Click hoặc click chuột giữa
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) {
          return true; // Không chặn sự kiện mặc định của thẻ <a>
        }
        e.preventDefault();
        this.switchTab(btn.dataset.tab);
      };
    });

    const bookingDeparture = document.getElementById('modal-booking-dep-select');
    if (bookingDeparture) bookingDeparture.onchange = () => this.calculateBookingTotal();
    const sidebarBtn = document.getElementById('sidebar-toggle-btn');
    const sidebar = document.getElementById('main-sidebar');
    if (sidebarBtn && sidebar) sidebarBtn.onclick = () => {
      if (innerWidth >= 768) { sidebar.classList.toggle('sidebar-collapsed'); return; }
      sidebar.classList.toggle('sidebar-open');
      sidebarBtn.setAttribute('aria-expanded', String(sidebar.classList.contains('sidebar-open')));
    };
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        document.querySelectorAll('[id$="-modal"]:not(.hidden)').forEach(el => this.closeModal(el.id));
        sidebar?.classList.remove('sidebar-open');
      }
    });
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) themeBtn.onclick = () => this.toggleTheme();

    const floatBtn = document.getElementById('floating-ai-btn');
    if (floatBtn) floatBtn.onclick = () => this.toggleFloatingAI();

    this.checkMagicTrackUrl();
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.App.init();
});
