/* ═══════════════════════════════════════════════════════════════
   ARCY — Gemini Logic Layer
   Focus: Fast, Fluid, Minimalist Chat
   ═══════════════════════════════════════════════════════════════ */

'use strict';

const dom = {
  chatMessages:   document.getElementById('chat-messages'),
  chatInput:      document.getElementById('chat-input'),
  chatSendBtn:    document.getElementById('chat-send-btn'),
  greetingHero:   document.getElementById('greeting-hero'),
  chatWorkspace:  document.querySelector('.chat-workspace'),
  quickActions:   document.querySelectorAll('.action-btn'),
  // Sidebar elements
  sidebar:        document.getElementById('app-sidebar'),
  sidebarToggle:  document.getElementById('sidebar-toggle'),
  newChatBtn:     document.getElementById('new-chat-btn'),
  sessionsList:   document.getElementById('sessions-list'),
};

let hasStartedChat = false;
let thinkingMsgEl  = null;
let currentSessionId = 'session_' + Date.now();

// Wizard State Management
let wizardState = {
  active: false,
  type:   null, // 'timetable', 'payment', 'expense', 'account'
  step:   0,
  data:   {}
};

const WIZARD_CONFIGS = {
  timetable: {
    title: "Let's build your timetable! 📅",
    questions: [
      "⏰ **Wake up time?** (e.g., 7 AM)",
      "🏢 **Work/Study hours?** (e.g., 9 AM - 5 PM)",
      "🍽️ **Lunch break?** (e.g., 1 PM)",
      "🏋️ **Hobby or Gym?** (e.g., 6 PM or 'None')",
      "😴 **Bedtime?** (e.g., 10:30 PM)"
    ],
    keys: ['wakeup', 'work', 'lunch', 'hobby', 'bedtime'],
    generator: (data) => `
| Time Range | Activity |
| :--- | :--- |
| ${data.wakeup} | ☀️ Wake Up & Morning Routine |
| ${data.work} | 💻 Work / Study Session |
| ${data.lunch} | 🍱 Lunch & Recharge |
| ${data.hobby} | 🎨 Hobby / Exercise |
| ${data.bedtime} | 🌙 Wind down & Sleep |
`.trim()
  },
  payment: {
    title: "Payment Assistant 💸",
    questions: [
      "💰 **How much is the payment?** (e.g., 500)",
      "🏢 **What is it for?** (e.g., Rent, Internet)",
      "💳 **Payment technique?** (e.g., GPay, Card, Cash)"
    ],
    keys: ['amount', 'purpose', 'method'],
    generator: (data) => `
| Field | Details |
| :--- | :--- |
| **Amount** | ${data.amount} |
| **Purpose** | ${data.purpose} |
| **Method** | ${data.method} |
| **Status** | ✅ Payment Logged |
`.trim()
  },
  expense: {
    title: "Expense Tracker 📊",
    questions: [
      "🛒 **Expense category?** (e.g., Food, Travel)",
      "💵 **Amount spent?** (e.g., 120)",
      "📝 **Quick note?** (e.g., Lunch with team)"
    ],
    keys: ['category', 'amount', 'note'],
    generator: (data) => `
| Field | Details |
| :--- | :--- |
| **Category** | ${data.category} |
| **Amount** | ${data.amount} |
| **Note**| ${data.note} |
| **Timestamp** | 🕒 ${new Date().toLocaleTimeString()} |
`.trim()
  },
  account: {
    title: "Account Manager 👤",
    questions: [
      "👤 **Your preferred Name?** (e.g., Aryan)",
      "📧 **Update Email?** (or type 'Skip')",
      "🔔 **Notifications?** (On / Off)"
    ],
    keys: ['name', 'email', 'notify'],
    generator: (data) => `
| Setting | Selection |
| :--- | :--- |
| **Name** | ${data.name} |
| **Email** | ${data.email} |
| **Notifications**| ${data.notify} |
| **Sync** | ⚙️ Profile Localized |
`.trim()
  }
};

// ─────────────────────────────────────────────────────────────
// Message Rendering
// ─────────────────────────────────────────────────────────────

function addMessage(role, text, animate = true) {
  // Hide hero on first interaction
  if (!hasStartedChat && dom.greetingHero) {
    hasStartedChat = true;
    dom.greetingHero.style.display = 'none';
  }

  // Remove thinking indicator
  if (thinkingMsgEl) {
    thinkingMsgEl.remove();
    thinkingMsgEl = null;
  }

  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  if (!animate) msg.style.animation = 'none';
  
  if (role === 'user') {
    msg.innerHTML = `<div class="message-bubble">${escapeHtml(text)}</div>`;
  } else {
    const parsedMarkdown = marked.parse(text);
    msg.innerHTML = `<div class="message-bubble markdown-body">${parsedMarkdown}</div>`;
  }
  
  dom.chatMessages.appendChild(msg);
  scrollToBottom();
  return msg;
}

function showThinking() {
  if (thinkingMsgEl) return;

  thinkingMsgEl = document.createElement('div');
  thinkingMsgEl.className = 'message arcy thinking-msg';
  thinkingMsgEl.innerHTML = `
    <div class="message-bubble">
      <div class="thinking-bubble">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>
  `;
  dom.chatMessages.appendChild(thinkingMsgEl);
  scrollToBottom();
}

function scrollToBottom() {
  const scrollOptions = {
    top: dom.chatWorkspace.scrollHeight,
    behavior: 'smooth'
  };
  requestAnimationFrame(() => dom.chatWorkspace.scrollTo(scrollOptions));
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(text));
  return d.innerHTML;
}

// ─────────────────────────────────────────────────────────────
// Sidebar & Session Logic
// ─────────────────────────────────────────────────────────────

async function initSessions() {
  if (window.pywebview && window.pywebview.api) {
    const index = await window.pywebview.api.get_session_index();
    renderSessionList(index);
  }
}

function renderSessionList(index) {
  dom.sessionsList.innerHTML = '';
  const sessions = Object.values(index);
  
  if (sessions.length === 0) {
    dom.sessionsList.innerHTML = '<div style="padding: 32px; opacity: 0.3; font-size: 13px; text-align: center; font-style: italic;">No conversation history</div>';
    return;
  }

  sessions.forEach(s => {
    const item = document.createElement('div');
    item.className = `session-item ${s.id === currentSessionId ? 'active' : ''}`;
    
    item.innerHTML = `
      <span class="session-title">${s.title || "New Chat"}</span>
      <button class="delete-session-btn" title="Delete Chat">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    `;

    item.onclick = (e) => {
      if (e.target.closest('.delete-session-btn')) {
        e.stopPropagation();
        confirmDeleteSession(s.id);
        return;
      }
      loadSession(s.id);
    };

    dom.sessionsList.appendChild(item);
  });
}

async function confirmDeleteSession(id) {
  if (confirm("Sir, are you sure you want to permanently delete this conversation?")) {
    await window.pywebview.api.delete_session(id);
    if (id === currentSessionId) {
      startNewChat();
    } else {
      initSessions();
    }
  }
}

async function loadSession(id) {
  if (id === currentSessionId) return;
  const data = await window.pywebview.api.load_session(id);
  if (!data) return;

  currentSessionId = id;
  dom.chatMessages.innerHTML = '';
  hasStartedChat = true;
  dom.greetingHero.style.display = 'none';

  data.forEach(m => addMessage(m.role, m.content, false));
  initSessions(); // Refresh list to show active
}

async function startNewChat() {
  currentSessionId = 'session_' + Date.now();
  dom.chatMessages.innerHTML = '';
  hasStartedChat = false;
  dom.greetingHero.style.display = 'block';
  dom.greetingHero.style.opacity = '1';
  dom.greetingHero.style.transform = 'none';
  initSessions();
}

// ─────────────────────────────────────────────────────────────
// Input & Backend Communication
// ─────────────────────────────────────────────────────────────

async function sendTextMessage() {
  const text = dom.chatInput.value.trim();
  if (!text) return;
  dom.chatInput.value = '';
  dom.chatInput.style.height = 'auto';
  dom.chatSendBtn.classList.remove('active');

  addMessage('user', text);

  if (wizardState.active) {
    handleWizardStep(text);
    return;
  }

  showThinking();

  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.handle_user_message(text, currentSessionId);
      // Refresh session list to catch potential title update
      setTimeout(initSessions, 1500);
    }
  } catch (err) {
    console.error("Bridge Error:", err);
    addMessage('arcy', "Operational error: Connection lost.");
  }
}

// ─────────────────────────────────────────────────────────────
// Events & Auto-resize
// ─────────────────────────────────────────────────────────────

dom.chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendTextMessage();
  }
});

dom.chatInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
  
  if (this.value.trim().length > 0) {
    dom.chatSendBtn.classList.add('active');
  } else {
    dom.chatSendBtn.classList.remove('active');
  }
});

// ─────────────────────────────────────────────────────────────
// Quick Action Handlers
// ─────────────────────────────────────────────────────────────
dom.quickActions.forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.id === 'timetable-btn') return startWizard('timetable');
    if (btn.id === 'payment-btn')   return startWizard('payment');
    if (btn.id === 'expense-btn')   return startWizard('expense');
    if (btn.id === 'account-btn')   return startWizard('account');

    const query = btn.getAttribute('data-query');
    dom.chatInput.value = query;
    dom.chatInput.dispatchEvent(new Event('input'));
    sendTextMessage();
  });
});

// ─────────────────────────────────────────────────────────────
// Generalized Wizard Logic
// ─────────────────────────────────────────────────────────────

function startWizard(type) {
  const config = WIZARD_CONFIGS[type];
  if (!config) return;

  wizardState.active = true;
  wizardState.type = type;
  wizardState.step = 0;
  wizardState.data = {};
  
  addMessage('arcy', config.title + "\n\n" + config.questions[0]);
}

// ... (Rest of handleWizardStep and finishWizard same)

function handleWizardStep(text) {
  const config = WIZARD_CONFIGS[wizardState.type];
  const key = config.keys[wizardState.step];
  
  wizardState.data[key] = text;
  wizardState.step++;

  if (wizardState.step < config.questions.length) {
    setTimeout(() => {
      addMessage('arcy', config.questions[wizardState.step]);
    }, 400);
  } else {
    setTimeout(() => {
      finishWizard();
    }, 600);
  }
}

function finishWizard() {
  const config = WIZARD_CONFIGS[wizardState.type];
  const finalMessage = config.generator(wizardState.data);
  
  wizardState.active = false;
  addMessage('arcy', "All set! Here is your summary: ✨\n\n" + finalMessage);
}

// ─────────────────────────────────────────────────────────────
// Sidebar & Final Init
// ─────────────────────────────────────────────────────────────
dom.sidebarToggle.addEventListener('click', () => {
  dom.sidebar.classList.toggle('collapsed');
});
dom.newChatBtn.addEventListener('click', startNewChat);
dom.chatSendBtn.addEventListener('click', sendTextMessage);

window.addEventListener('load', () => {
  dom.chatInput.focus();
  initSessions();
});

// Bridge API
window.arctAPI = {
  showArcyReply(text) { addMessage('arcy', text); },
  setArcyState(state) { if (state === 'thinking') showThinking(); }
};
