// AI Hub Module for VietJourney
window.AIHub = {
  chatHistory: [],

  init: function() {
    if (this.initialized) return;
    this.initialized = true;
    this.bindEvents();
    this.fetchAIStatus();
    this.populateFeedbackTours();

    const targetSubTab = localStorage.getItem('vietjourney_ai_subtab');
    if (targetSubTab) {
      localStorage.removeItem('vietjourney_ai_subtab');
      this.switchSubTab(targetSubTab);
    }

    const pendingQuery = sessionStorage.getItem('vietjourney_pending_ai_query');
    if (pendingQuery) {
      sessionStorage.removeItem('vietjourney_pending_ai_query');
      setTimeout(() => this.handleConsultSend(pendingQuery), 250);
    }
  },

  switchSubTab: function(tabName) {
    if (tabName === 'desc') {
      const isAdmin = Boolean(window.App && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
      if (!isAdmin) {
        window.App?.showToast('Chức năng AI Sinh Mô Tả Tour chỉ dành cho Quản Trị Viên (Admin)!', 'error');
        return;
      }
    }
    if (tabName === 'feedback') {
      const isStaff = Boolean(window.App && window.App.currentUser && ['ADMIN', 'CONSULTANT'].includes(window.App.currentUser.role));
      if (!isStaff) {
        window.App?.showToast('Chức năng Phân Tích Phản Hồi dành cho Tư vấn viên và Quản trị viên!', 'error');
        return;
      }
    }
    const tabs = ['consult', 'desc', 'feedback'];
    tabs.forEach(t => {
      const view = document.getElementById('ai-subview-' + t);
      const btn = document.getElementById('ai-tab-' + t + '-btn');
      if (view) {
        if (t === tabName) view.classList.remove('hidden');
        else view.classList.add('hidden');
      }
      if (btn) {
        if (t === tabName) {
          btn.className = 'pb-3 text-sky-600 border-b-2 border-sky-600 flex items-center space-x-1.5 font-bold';
        } else {
          btn.className = 'pb-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 flex items-center space-x-1.5 font-bold';
        }
      }
    });
    if (tabName === 'feedback') {
      this.populateFeedbackTours();
    }
  },

  populateFeedbackTours: function() {
    const sel = document.getElementById('ai-feedback-tour-select');
    if (!sel) return;
    fetch('/api/v1/tours')
      .then(r => r.json())
      .then(tours => {
        let html = '<option value="">-- Tất cả các tour --</option>';
        if (Array.isArray(tours)) {
          tours.forEach(t => {
            html += `<option value="${t.id}">[${t.code}] ${t.title}</option>`;
          });
        }
        sel.innerHTML = html;
      })
      .catch(e => console.warn("Lỗi tải danh sách tour cho phân tích phản hồi:", e));
  },

  bindEvents: function() {
    const sendBtn = document.getElementById('ai-consult-send-btn');
    const input = document.getElementById('ai-consult-input');
    if (sendBtn) {
      sendBtn.onclick = (e) => {
        if (e && e.preventDefault) e.preventDefault();
        this.handleConsultSend();
      };
    }
    if (input) {
      input.onkeydown = (e) => {
        if (e.key === 'Enter') {
          if (e.preventDefault) e.preventDefault();
          this.handleConsultSend();
        }
      };
    }

    const genBtn = document.getElementById('ai-gen-desc-btn');
    if (genBtn) {
      genBtn.onclick = (e) => {
        if (e && e.preventDefault) e.preventDefault();
        this.handleGenerateDescription();
      };
    }

    const feedbackBtn = document.getElementById('ai-analyze-feedback-btn');
    if (feedbackBtn) {
      feedbackBtn.onclick = (e) => {
        if (e && e.preventDefault) e.preventDefault();
        this.handleAnalyzeFeedback();
      };
    }
  },

  handleConsultSend: async function(prefilledQuery = null) {
    const input = document.getElementById('ai-consult-input');
    const query = prefilledQuery || (input ? input.value.trim() : '');
    if (!query) return;

    if (input && !prefilledQuery) input.value = '';

    const chatContainer = document.getElementById('ai-chat-messages');
    if (!chatContainer) return;

    // AUTO-DETECT: Nếu ADMIN dán hoặc gõ mã API Key trực tiếp vào khung chat (hỗ trợ cả định dạng AIzaSy... và AQ.... từ Google AI Studio)
    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
    if (isAdmin && (query.startsWith("AIzaSy") || query.startsWith("AQ.")) && query.length >= 25) {
      this.appendUserMessage(chatContainer, "[Đã gửi mã Google Gemini API Key: " + query.substring(0, 8) + "...]");
      const loadingId = 'ai-loading-' + Date.now();
      this.appendLoadingMessage(chatContainer, loadingId);

      try {
        const headers = { 'Content-Type': 'application/json' };
        if (window.App && window.App.token) {
          headers['Authorization'] = `Bearer ${window.App.token}`;
        }
        const res = await fetch('/api/v1/ai/configure-key', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ api_key: query })
        });
        const data = await res.json();
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        if (data.success) {
          await this.fetchAIStatus();
          this.appendAIMessage(chatContainer, {
            advice_text: `Xác thực thành công! ${data.message}\n\nPhản hồi thử nghiệm từ Google Cloud: "${data.test_reply || 'OK'}"\n\nTừ bây giờ, hệ thống VietJourney đã chuyển sang sử dụng Google Gemini Cloud AI thật 100%! Bạn hãy thử nhập bất kỳ yêu cầu tư vấn tour nào nhé!`,
            recommended_tours: [],
            engine_used: `Google Gemini (${data.model_name || 'Cloud AI'})`
          });
        } else {
          this.appendAIMessage(chatContainer, {
            advice_text: `Kết nối Google Gemini thất bại: ${data.message}\n\nVui lòng kiểm tra lại mã API Key trên Google AI Studio.`,
            recommended_tours: [],
            engine_used: "Hệ thống"
          });
        }
      } catch (err) {
        console.error(err);
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        alert("Lỗi khi kết nối kiểm tra Gemini API Key.");
      }
      return;
    }

    // 1. Thêm tin nhắn của người dùng thông thường
    this.appendUserMessage(chatContainer, query);

    // 2. Thêm chỉ báo đang tải
    const loadingId = 'ai-loading-' + Date.now();
    this.appendLoadingMessage(chatContainer, loadingId);

    try {
      const response = await fetch('/api/v1/ai/consult', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      });

      const data = await response.json();
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      if (!response.ok) {
        this.appendAIMessage(chatContainer, {
          advice_text: `**Không thể kết nối Google Gemini Cloud AI:**\n\n${data.detail || "Đã xảy ra sự cố khi gọi Google Gemini API."}\n\nQuản trị viên vui lòng kiểm tra API Key tại trang **Trợ Lý AI Gemini**.`,
          recommended_tours: [],
          engine_used: "Google Gemini Cloud AI"
        });
        return;
      }

      this.appendAIMessage(chatContainer, data);
    } catch (err) {
      console.error(err);
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      this.appendAIMessage(chatContainer, {
        advice_text: "Xin lỗi, đã có sự cố kết nối tới AI Engine. Vui lòng thử lại sau giây lát.",
        recommended_tours: [],
        engine_used: "Hệ thống"
      });
    }
  },

  appendUserMessage: function(container, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex justify-end mb-4 animate-fade-in';
    msgDiv.innerHTML = `
      <div class="max-w-[80%] bg-sky-600 text-white rounded-2xl rounded-tr-none px-4 py-3 shadow-sm">
        <p class="text-sm leading-relaxed">${this.escapeHtml(text)}</p>
        <span class="text-[10px] text-sky-200 block text-right mt-1">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
    `;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
  },

  appendLoadingMessage: function(container, id) {
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex justify-start mb-4';
    div.innerHTML = `
      <div class="max-w-[80%] bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-2xl rounded-tl-none px-4 py-3 border border-slate-200 dark:border-slate-700 flex items-center space-x-2">
        <div class="w-2 h-2 rounded-full bg-sky-500 animate-bounce"></div>
        <div class="w-2 h-2 rounded-full bg-sky-500 animate-bounce anim-delay-200"></div>
        <div class="w-2 h-2 rounded-full bg-sky-500 animate-bounce anim-delay-400"></div>
        <span class="text-xs text-slate-500 dark:text-slate-400 ml-2">AI đang kiểm tra các tour còn chỗ trong CSDL...</span>
      </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  appendAIMessage: function(container, data) {
    const div = document.createElement('div');
    div.className = 'flex justify-start mb-4';

    let cardsHtml = '';
    if (data.recommended_tours && data.recommended_tours.length > 0) {
      cardsHtml = `
        <div class="mt-3 grid grid-cols-1 gap-2">
          ${data.recommended_tours.map(t => `
            <div class="bg-white dark:bg-slate-900 border border-sky-200 dark:border-sky-800 rounded-xl p-3 shadow-sm hover:border-sky-400 transition-all">
              <div class="flex justify-between items-start">
                <div>
                  <span class="inline-block bg-sky-100 dark:bg-sky-900/50 text-sky-700 dark:text-sky-300 text-[10px] font-bold px-2 py-0.5 rounded mr-1">${t.code}</span>
                  <span class="text-xs font-semibold text-slate-800 dark:text-slate-100">${t.title}</span>
                </div>
                <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">${t.price.toLocaleString('vi-VN')} đ</span>
              </div>
              <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">${t.destination} • ${t.duration} • Còn <span class="font-bold text-amber-600">${t.available_slots} chỗ</span></p>
              <p class="text-[11px] text-sky-700 dark:text-sky-300 mt-1">${t.match_reason}</p>
              <div class="mt-2 flex justify-end">
                <button data-action="${t.departure_id ? 'openRecommendedDeparture' : 'openBookingModalForTour'}" data-args="${t.departure_id ? `${t.tour_id},${t.departure_id}` : t.tour_id}" class="text-xs bg-sky-600 hover:bg-sky-700 text-white font-medium px-3 py-1 rounded-lg transition-colors shadow-sm">
                  Đặt chỗ tour này
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    div.innerHTML = `
      <div class="max-w-[85%] bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-2xl rounded-tl-none px-4 py-3 border border-slate-200 dark:border-slate-700 shadow-sm">
        <div class="flex items-center space-x-1.5 mb-1.5">
          <span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
          <span class="text-[10px] font-semibold text-slate-500 dark:text-slate-400">VietJourney AI (${data.engine_used})</span>
        </div>
        <div class="text-sm leading-relaxed whitespace-pre-line">${this.escapeHtml(data.advice_text)}</div>
        ${cardsHtml}
        <span class="text-[10px] text-slate-400 block text-right mt-2">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  handleGenerateDescription: async function() {
    if (!['ADMIN', 'CONSULTANT'].includes(window.App?.currentUser?.role)) { window.App?.showToast('Chức năng này dành cho nhân viên tư vấn và Admin.', 'error'); return; }
    let title = (document.getElementById('ai-gen-title')?.value || '').trim();
    let dest = (document.getElementById('ai-gen-dest')?.value || '').trim();
    const days = parseInt(document.getElementById('ai-gen-days')?.value) || 3;
    const nights = parseInt(document.getElementById('ai-gen-nights')?.value) || 2;
    const highlights = (document.getElementById('ai-gen-highlights')?.value || '').trim();

    if (!title && !dest) {
      alert("Vui lòng nhập Tên tour hoặc Điểm đến chính!");
      return;
    }
    if (!dest) dest = title;
    if (!title) title = `Du lịch ${dest}`;

    const resultBox = document.getElementById('ai-gen-result-box');
    const loadingEl = document.getElementById('ai-gen-loading');
    if (resultBox) resultBox.classList.add('hidden');
    if (loadingEl) loadingEl.classList.remove('hidden');

    try {
      const res = await fetch('/api/v1/ai/generate-description', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${window.App.token}` },
        body: JSON.stringify({
          tour_title: title,
          destination: dest,
          duration_days: days,
          duration_nights: nights,
          highlights: highlights
        })
      });
      if (!res.ok) throw new Error('Không tạo được nội dung');
      const data = await res.json();

      if (loadingEl) loadingEl.classList.add('hidden');
      if (resultBox) {
        resultBox.classList.remove('hidden');
        document.getElementById('ai-res-slogan').innerText = data.marketing_slogan;
        document.getElementById('ai-res-desc').innerText = data.description;
        document.getElementById('ai-res-itinerary').innerText = data.itinerary_summary;
        document.getElementById('ai-res-tips').innerText = data.packing_tips;
        document.getElementById('ai-res-engine').innerText = `Sinh bởi: ${data.engine_used}`;
      }
    } catch (e) {
      console.error(e);
      if (loadingEl) loadingEl.classList.add('hidden');
      alert("Có lỗi khi tạo nội dung tour. Vui lòng thử lại!");
    }
  },

  applyGeneratedToTourForm: function() {
    const title = document.getElementById('ai-gen-title').value;
    const dest = document.getElementById('ai-gen-dest').value;
    const days = document.getElementById('ai-gen-days').value;
    const nights = document.getElementById('ai-gen-nights').value;
    const desc = document.getElementById('ai-res-desc').innerText;
    const itinerary = document.getElementById('ai-res-itinerary').innerText;
    const highlights = document.getElementById('ai-gen-highlights').value;

    if (window.App.currentUser?.role !== 'ADMIN') { window.App.showToast('Chỉ Admin được tạo tour mới.', 'error'); return; }
    sessionStorage.setItem('tour-draft', JSON.stringify({title, destination:dest, days, nights, description:desc, itinerary, highlights}));
    window.location.assign('/tours');
  },

  handleAnalyzeFeedback: async function() {
    if (!['ADMIN', 'CONSULTANT'].includes(window.App?.currentUser?.role)) { window.App?.showToast('Chức năng này dành cho nhân viên tư vấn và Admin.', 'error'); return; }
    const tourSelect = document.getElementById('ai-feedback-tour-select');
    const tourId = tourSelect && tourSelect.value ? parseInt(tourSelect.value) : null;

    const resultBox = document.getElementById('ai-feedback-result-box');
    const loadingEl = document.getElementById('ai-feedback-loading');
    if (resultBox) resultBox.classList.add('hidden');
    if (loadingEl) loadingEl.classList.remove('hidden');

    try {
      const res = await fetch('/api/v1/ai/summarize-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${window.App.token}` },
        body: JSON.stringify({ tour_id: tourId })
      });
      if (!res.ok) throw new Error('Không phân tích được phản hồi');
      const data = await res.json();

      if (loadingEl) loadingEl.classList.add('hidden');
      if (resultBox) {
        resultBox.classList.remove('hidden');
        document.getElementById('ai-fb-total').innerText = `${data.total_feedbacks} đánh giá`;
        if (data.total_feedbacks === 0) {
          document.getElementById('ai-fb-rating').innerText = `Chưa có đánh giá`;
        } else {
          document.getElementById('ai-fb-rating').innerText = `${data.average_rating} / 5.0`;
        }
        
        const posHighlightsList = document.getElementById('ai-fb-pos-list');
        posHighlightsList.innerHTML = (data.positive_highlights || []).map(h => `<li class="text-xs text-emerald-800 dark:text-emerald-300 flex items-start leading-relaxed"><i class="fa-solid fa-check text-emerald-500 mr-2 shrink-0 mt-0.5"></i><span>${this.escapeHtml(h)}</span></li>`).join('');

        const impAreasList = document.getElementById('ai-fb-imp-list');
        impAreasList.innerHTML = (data.improvement_areas || []).map(a => `<li class="text-xs text-amber-800 dark:text-amber-300 flex items-start leading-relaxed"><i class="fa-solid fa-circle-exclamation text-amber-500 mr-2 shrink-0 mt-0.5"></i><span>${this.escapeHtml(a)}</span></li>`).join('');

        document.getElementById('ai-fb-guide-eval').innerText = data.guide_performance_summary;
        document.getElementById('ai-fb-exec-rec').innerText = data.executive_recommendation;
        document.getElementById('ai-fb-engine').innerText = `Phân tích bởi: ${data.engine_used}`;
      }
    } catch (e) {
      console.error(e);
      if (loadingEl) loadingEl.classList.add('hidden');
      alert("Lỗi khi phân tích phản hồi.");
    }
  },

  escapeHtml: function(text) {
    if (!text) return '';
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  },

  // ==================== AI STATUS & CONFIGURATION ====================
  fetchAIStatus: async function() {
    try {
      const headers = (window.App && window.App.token) ? { 'Authorization': `Bearer ${window.App.token}` } : {};
      const res = await fetch('/api/v1/ai/status', { headers });
      if (!res.ok) return;
      const data = await res.json();
      this.updateStatusUI(data);
    } catch (err) {
      console.error("fetchAIStatus error:", err);
    }
  },

  updateStatusUI: function(status) {
    const pill = document.getElementById('ai-engine-status-pill');
    const dot = document.getElementById('ai-engine-status-dot');
    const nameEl = document.getElementById('ai-engine-name');
    const descEl = document.getElementById('ai-engine-desc');
    const topbarBtn = document.getElementById('topbar-ai-status-btn');
    const topbarDot = document.getElementById('topbar-ai-dot');
    const topbarLabel = document.getElementById('topbar-ai-label');
    const directBadge = document.getElementById('ai-direct-badge');
    const directInput = document.getElementById('ai-direct-key-input');
    const adminCard = document.getElementById('ai-admin-config-card');
    const adminBtn = document.getElementById('ai-admin-config-btn');

    // BẢO MẬT: Chỉ hiển thị tính năng cấu hình Key khi là ADMIN
    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');

    if (adminCard) adminCard.style.display = isAdmin ? '' : 'none';
    if (adminBtn) adminBtn.style.display = isAdmin ? '' : 'none';

    if (status.is_gemini_active) {
      if (pill) pill.className = 'flex items-center space-x-2 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 px-3 py-1.5 rounded-xl text-xs';
      if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse';
      if (nameEl) {
        nameEl.className = 'font-bold text-emerald-700 dark:text-emerald-400 block';
        nameEl.innerHTML = `<i class="fa-solid fa-cloud text-emerald-500 mr-1"></i> ${status.active_engine}`;
      }
      if (descEl) {
        descEl.className = 'text-[10px] text-emerald-600 dark:text-emerald-500';
        descEl.innerText = (isAdmin && status.masked_key) ? `Key: ${status.masked_key} (${status.model_name}) • Sẵn sàng` : 'Trực tuyến 24/7 • Sẵn sàng tư vấn';
      }
      if (topbarBtn) {
        topbarBtn.className = 'flex items-center space-x-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 px-3 py-1.5 rounded-xl text-xs font-bold hover:bg-emerald-100 transition-all shadow-sm';
      }
      if (topbarDot) topbarDot.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
      if (topbarLabel) topbarLabel.innerText = 'AI: Gemini Cloud';
      if (directBadge && isAdmin) {
        directBadge.className = 'text-[10px] text-emerald-600 dark:text-emerald-400 font-bold';
        directBadge.innerHTML = `Đang kết nối Cloud AI: ${status.masked_key || 'Đã kích hoạt'} (${status.model_name})`;
      }
      if (directInput && !directInput.value && isAdmin) {
        directInput.placeholder = `Key đang hoạt động: ${status.masked_key || 'Đã kích hoạt'} (Nhập mã mới nếu muốn đổi)`;
      }
    } else {
      if (pill) pill.className = 'flex items-center space-x-2 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 px-3 py-1.5 rounded-xl text-xs';
      if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse';
      if (nameEl) {
        nameEl.className = 'font-bold text-amber-700 dark:text-amber-400 block';
        nameEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-500 mr-1"></i> ${status.active_engine}`;
      }
      if (descEl) {
        descEl.className = 'text-[10px] text-amber-600 dark:text-amber-500';
        descEl.innerText = isAdmin ? 'Chưa cấu hình API Key • Vui lòng nhập Key' : 'Chưa kích hoạt Google Gemini Cloud';
      }
      if (topbarBtn) {
        topbarBtn.className = 'flex items-center space-x-1.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-amber-700 dark:text-amber-300 px-3 py-1.5 rounded-xl text-xs font-bold hover:bg-amber-100 transition-all shadow-sm';
      }
      if (topbarDot) topbarDot.className = 'w-2 h-2 rounded-full bg-amber-500 animate-pulse';
      if (topbarLabel) topbarLabel.innerText = isAdmin ? 'AI: Cấu hình Key' : 'AI: Chưa kích hoạt';
      if (directBadge && isAdmin) {
        directBadge.className = 'text-[10px] text-amber-600 dark:text-amber-400 font-semibold';
        directBadge.innerText = 'Chưa có API Key • Vui lòng nhập Google Gemini API Key';
      }
    }
  },

  pasteKeyToInput: async function(targetId) {
    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
    if (!isAdmin) return;
    const el = document.getElementById(targetId);
    if (!el) return;
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          el.value = text.trim();
          el.focus();
          return;
        }
      }
    } catch (e) {
      console.warn("Clipboard access:", e);
    }
    el.focus();
    el.select();
  },

  openKeyModal: async function() {
    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
    if (!isAdmin) {
      alert("Quyền truy cập bị từ chối: Tính năng Cấu hình Gemini API Key chỉ dành riêng cho Quản trị viên (Admin)!");
      return;
    }

    const modal = document.getElementById('modal-gemini-config');
    if (!modal) return;
    modal.classList.remove('hidden');

    const titleEl = document.getElementById('modal-gemini-status-title');
    const descEl = document.getElementById('modal-gemini-status-desc');
    const alertBox = document.getElementById('modal-gemini-status-alert');
    const inputKey = document.getElementById('input-gemini-api-key');

    setTimeout(() => {
      if (inputKey) inputKey.focus();
    }, 100);

    try {
      const res = await fetch('/api/v1/ai/status');
      const data = await res.json();
      if (data.is_gemini_active) {
        alertBox.className = 'p-3.5 rounded-xl border bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 flex items-start space-x-3';
        titleEl.innerHTML = `<span class="text-emerald-700 dark:text-emerald-400 font-bold">Đang kết nối Google Gemini Cloud AI</span>`;
        descEl.innerText = `Key hiện tại: ${data.masked_key} | Model: ${data.model_name}`;
      } else {
        alertBox.className = 'p-3.5 rounded-xl border bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/60 flex items-start space-x-3';
        titleEl.innerHTML = `<span class="text-amber-700 dark:text-amber-400 font-bold">Chưa kích hoạt Google Gemini Cloud AI</span>`;
        descEl.innerText = 'Hệ thống hoạt động 100% bằng Google Gemini Cloud AI chính thức. Hãy nhập API Key từ Google AI Studio để kích hoạt!';
      }
    } catch (e) {
      console.error(e);
    }
  },

  closeKeyModal: function() {
    const modal = document.getElementById('modal-gemini-config');
    if (modal) modal.classList.add('hidden');
  },

  saveDirectKey: async function() {
    const inputKey = document.getElementById('ai-direct-key-input');
    const selectModel = document.getElementById('ai-direct-model-select');
    const saveBtn = document.getElementById('btn-save-direct-key');
    const statusMsg = document.getElementById('ai-direct-status-msg');

    const key = inputKey ? inputKey.value.trim() : '';
    const model = selectModel ? selectModel.value : 'gemini-3.1-flash-lite';

    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
    if (!isAdmin) {
      alert("Chỉ Quản trị viên (Admin) mới có quyền cấu hình API Key!");
      return;
    }

    if (!key) {
      alert("Vui lòng nhập Google Gemini API Key!");
      if (inputKey) inputKey.focus();
      return;
    }

    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Đang kết nối...`;
    }
    if (statusMsg) {
      statusMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-sky-500 mr-1"></i> Đang kiểm tra kết nối với Google Gemini Cloud API...`;
    }

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (window.App && window.App.token) {
        headers['Authorization'] = `Bearer ${window.App.token}`;
      }
      const res = await fetch('/api/v1/ai/configure-key', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ api_key: key, model_name: model })
      });

      const data = await res.json();

      if (data.success) {
        if (data.available_models && data.available_models.length) {
          this.populateModelSelects(data.available_models, data.model_name);
        } else if (data.model_name && selectModel) {
          selectModel.value = data.model_name;
        }
        if (statusMsg) {
          statusMsg.innerHTML = `<span class="text-emerald-600 dark:text-emerald-400 font-bold flex items-center"><i class="fa-solid fa-circle-check mr-1.5"></i> ${data.message} • Thử nghiệm: "${data.test_reply || 'OK'}"</span>`;
        }
        alert(`Thành công!\n\n${data.message}\nPhản hồi từ Google Gemini: "${data.test_reply || 'OK'}"\n\nTừ bây giờ hệ thống sẽ sử dụng Cloud AI thật 100%!`);
        if (inputKey) inputKey.value = '';
        await this.fetchAIStatus();
      } else {
        if (statusMsg) {
          statusMsg.innerHTML = `<span class="text-rose-600 dark:text-rose-400 font-bold flex items-center"><i class="fa-solid fa-triangle-exclamation mr-1.5"></i> ${data.message || data.detail}</span>`;
        }
        alert(`Lỗi kết nối Google Gemini:\n\n${data.message || data.detail || 'Không có quyền thực hiện'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Đã xảy ra lỗi khi gửi yêu cầu cấu hình API Key.");
    } finally {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up"></i> <span>Kích Hoạt</span>`;
      }
    }
  },

  populateModelSelects: function(models, selectedModel) {
    if (!models || !models.length) return;
    const selects = ['ai-direct-model-select', 'select-gemini-model'];
    selects.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      el.innerHTML = '';
      models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.text = m + (m.includes('flash') ? ' (Khuyên dùng - Nhanh)' : '');
        if (m === selectedModel) opt.selected = true;
        el.appendChild(opt);
      });
    });
  },

  saveGeminiKey: async function() {
    const isAdmin = Boolean(window.App && window.App.isLoggedIn() && window.App.currentUser && window.App.currentUser.role === 'ADMIN');
    if (!isAdmin) {
      alert("Chỉ Quản trị viên (Admin) mới có quyền cấu hình API Key!");
      return;
    }

    const inputKey = document.getElementById('input-gemini-api-key');
    const selectModel = document.getElementById('select-gemini-model');
    const saveBtn = document.getElementById('btn-save-gemini-key');

    const key = inputKey ? inputKey.value.trim() : '';
    const model = selectModel ? selectModel.value : 'gemini-3.1-flash-lite';

    if (!key) {
      alert("Vui lòng nhập Google Gemini API Key!");
      if (inputKey) inputKey.focus();
      return;
    }

    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Đang kiểm tra kết nối...`;
    }

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (window.App && window.App.token) {
        headers['Authorization'] = `Bearer ${window.App.token}`;
      }
      const res = await fetch('/api/v1/ai/configure-key', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ api_key: key, model_name: model })
      });

      const data = await res.json();

      if (data.success) {
        if (data.available_models && data.available_models.length) {
          this.populateModelSelects(data.available_models, data.model_name);
        }
        alert(`Thành công!\n\n${data.message}\nPhản hồi thử nghiệm: "${data.test_reply || 'OK'}"`);
        if (inputKey) inputKey.value = '';
        this.closeKeyModal();
        await this.fetchAIStatus();
      } else {
        alert(`Lỗi kết nối Google Gemini:\n\n${data.message || data.detail || 'Không có quyền thực hiện'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Đã xảy ra lỗi khi gửi yêu cầu cấu hình API Key.");
    } finally {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up"></i> <span>Kiểm Tra & Kích Hoạt</span>`;
      }
    }
  },

  resetToLocalEngine: function() {
    // Chế độ AI giả nội bộ đã bị loại bỏ hoàn toàn. Hệ thống chỉ dùng Google Gemini Cloud AI.
    return;
  }
};

// Tự động khởi tạo AIHub ngay khi tài liệu sẵn sàng
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.AIHub && typeof window.AIHub.init === 'function') {
      window.AIHub.init();
    }
  });
} else {
  if (window.AIHub && typeof window.AIHub.init === 'function') {
    window.AIHub.init();
  }
}
