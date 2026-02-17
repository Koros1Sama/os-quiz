#!/usr/bin/env python3
"""Generate OS Quiz HTML from questions.json"""
import json, os, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Topic classification by question ID
TOPIC_MAP = {
    "أساسيات نظام التشغيل": [1,26,31,32,33,34,41,42,43,44,45,46,47,48,49,50,51,54,56,58,59,60,100,111,115,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,152,153,154,155,156,157,158,159,160,173,174,175,176,177,178],
    "إدارة العمليات": [3,5,11,20,21,22,23,37,40,52,55,61,62,65,94,109,110,112],
    "جدولة المعالج": [2,29,35,47,53,83,88,89,90,105,106,169],
    "إدارة الذاكرة": [12,13,14,15,25,36,66,67,68,69,70,91,92,93,97,107,108,113,116,117,118,119,120,121],
    "أنظمة الملفات": [6,7,8,9,10,16,17,71,72,73,74,75,122,124,150],
    "الجمود (Deadlock)": [4,76,77,78,79,80,99],
    "الخيوط (Threads)": [18,24,27,28,101,102,114,161,162,163,164,165,166,167,168,170,171,172,179,180],
    "التزامن (Synchronization)": [19,30,95,96,98,151],
    "الإدخال/الإخراج والأجهزة": [49,57,81,82,84,85,126,136,138,152,178],
    "الأمن والحماية": [86,87,103,104,123,127,146,159],
    "استدعاءات النظام": [38,39],
}

def get_topic(qid):
    for topic, ids in TOPIC_MAP.items():
        if qid in ids:
            return topic
    return "أساسيات نظام التشغيل"

def load_questions():
    with open(os.path.join(SCRIPT_DIR, 'questions.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def generate():
    questions = load_questions()
    
    # Build JS data
    js_questions = []
    for q in questions:
        topic = get_topic(q['id'])
        opts_js = []
        for o in q['options']:
            opts_js.append({
                't': o['text'],
                'c': o['correct']
            })
        js_questions.append({
            'id': q['id'],
            'q': q['text'],
            'topic': topic,
            'opts': opts_js
        })
    
    questions_json = json.dumps(js_questions, ensure_ascii=False)
    
    html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>بنك أسئلة نظم التشغيل - 180 سؤال</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
--bg:#0f0f1a;--bg2:#1a1a2e;--bg3:#25253d;--card:#1e1e35;--card-hover:#252545;
--text:#e8e8f0;--text2:#a0a0c0;--text3:#707090;
--accent:#7c5cfc;--accent2:#a78bfa;--accent-glow:rgba(124,92,252,0.3);
--correct:#10b981;--correct-bg:rgba(16,185,129,0.15);--correct-border:rgba(16,185,129,0.4);
--wrong:#ef4444;--wrong-bg:rgba(239,68,68,0.15);--wrong-border:rgba(239,68,68,0.4);
--bookmark-red:#ef4444;--bookmark-yellow:#f59e0b;--bookmark-green:#10b981;--bookmark-blue:#3b82f6;
--radius:12px;--radius-sm:8px;--shadow:0 4px 24px rgba(0,0,0,0.3);
--font-ar:'Tajawal',sans-serif;--font-en:'Inter',sans-serif;
}}
[data-theme="light"]{{
--bg:#f0f0f8;--bg2:#e8e8f2;--bg3:#dddde8;--card:#ffffff;--card-hover:#f5f5ff;
--text:#1a1a2e;--text2:#4a4a6a;--text3:#8a8aa0;
--shadow:0 4px 24px rgba(0,0,0,0.08);
}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--font-ar);background:var(--bg);color:var(--text);line-height:1.7;transition:all .3s}}
.en{{font-family:var(--font-en);direction:ltr;text-align:left}}

/* HEADER */
.header{{position:sticky;top:0;z-index:100;background:var(--bg2);border-bottom:1px solid var(--bg3);padding:12px 20px;backdrop-filter:blur(12px)}}
.header-top{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}
.header h1{{font-size:1.2rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header-btns{{display:flex;gap:6px;flex-wrap:wrap}}
.btn{{padding:6px 14px;border:1px solid var(--bg3);border-radius:var(--radius-sm);background:var(--bg3);color:var(--text);cursor:pointer;font-family:var(--font-ar);font-size:.82rem;transition:all .2s;white-space:nowrap}}
.btn:hover{{background:var(--accent);border-color:var(--accent);color:#fff}}
.btn.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
.btn-danger{{border-color:var(--wrong);color:var(--wrong)}}
.btn-danger:hover{{background:var(--wrong);color:#fff}}

/* PROGRESS */
.progress-wrap{{margin-top:10px}}
.progress-bar{{height:8px;background:var(--bg3);border-radius:99px;overflow:hidden}}
.progress-fill{{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px;transition:width .4s ease;width:0%}}
.progress-text{{font-size:.8rem;color:var(--text2);margin-top:4px;display:flex;justify-content:space-between}}

/* FILTER BAR */
.filter-bar{{position:sticky;top:72px;z-index:90;background:var(--bg);padding:10px 20px;display:flex;gap:6px;flex-wrap:wrap;border-bottom:1px solid var(--bg3)}}
.filter-bar .btn{{font-size:.78rem;padding:5px 12px}}
.bookmark-dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-inline-end:4px;vertical-align:middle}}

/* SIDEBAR NAV */
.sidebar{{position:fixed;left:0;top:0;bottom:0;width:60px;background:var(--bg2);border-right:1px solid var(--bg3);z-index:80;overflow-y:auto;padding:80px 6px 20px;transition:width .3s;scrollbar-width:thin}}
.sidebar::-webkit-scrollbar{{width:4px}}
.sidebar::-webkit-scrollbar-thumb{{background:var(--bg3);border-radius:9px}}
.sidebar.expanded{{width:220px}}
.nav-btn{{width:100%;aspect-ratio:1;border:none;border-radius:var(--radius-sm);font-size:.7rem;font-weight:700;cursor:pointer;margin-bottom:3px;position:relative;transition:all .2s;display:flex;align-items:center;justify-content:center;background:var(--bg3);color:var(--text2)}}
.nav-btn:hover{{transform:scale(1.1);z-index:2}}
.nav-btn.answered-correct{{background:var(--correct-bg);color:var(--correct);border:1px solid var(--correct-border)}}
.nav-btn.answered-wrong{{background:var(--wrong-bg);color:var(--wrong);border:1px solid var(--wrong-border)}}
.nav-btn .bm-indicator{{position:absolute;top:2px;right:2px;width:8px;height:8px;border-radius:50%;border:1px solid var(--bg2)}}
.nav-btn .bm-indicator-2{{position:absolute;top:2px;left:2px}}

/* MAIN */
.main{{margin-right:0;margin-left:68px;padding:20px;max-width:900px}}
@media(min-width:1200px){{.main{{margin:0 auto;padding-left:80px}}}}

/* QUESTION CARD */
.q-card{{background:var(--card);border:1px solid var(--bg3);border-radius:var(--radius);padding:20px;margin-bottom:16px;transition:all .3s;position:relative}}
.q-card:hover{{border-color:var(--accent-glow)}}
.q-card.filtered-out{{display:none}}
.q-header{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:14px}}
.q-number{{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;min-width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.85rem;flex-shrink:0}}
.q-text{{flex:1;font-size:1rem;font-weight:600;line-height:1.8}}
.q-text .en{{display:block;font-size:.95rem;margin-bottom:4px}}
.q-text .ar{{display:block;font-size:.85rem;color:var(--text2)}}
.q-actions{{display:flex;gap:4px;flex-shrink:0}}
.q-actions .btn{{padding:4px 8px;font-size:.75rem}}

/* BOOKMARK MENU */
.bm-menu{{position:absolute;top:50px;left:10px;background:var(--bg2);border:1px solid var(--bg3);border-radius:var(--radius-sm);padding:6px;z-index:10;display:none;box-shadow:var(--shadow)}}
.bm-menu.show{{display:flex;flex-direction:column;gap:4px}}
.bm-color-btn{{width:28px;height:28px;border-radius:50%;border:2px solid transparent;cursor:pointer;transition:all .2s}}
.bm-color-btn:hover,.bm-color-btn.active{{border-color:#fff;transform:scale(1.15)}}

/* OPTIONS */
.opts{{display:flex;flex-direction:column;gap:8px}}
.opt-btn{{padding:12px 16px;border:2px solid var(--bg3);border-radius:var(--radius-sm);background:var(--bg);cursor:pointer;text-align:right;font-family:var(--font-ar);font-size:.9rem;transition:all .2s;position:relative;display:flex;align-items:center;gap:10px}}
.opt-btn .en{{font-family:var(--font-en);direction:ltr;flex:1}}
.opt-btn:hover:not(.disabled){{border-color:var(--accent);background:var(--accent-glow)}}
.opt-btn.selected{{border-color:var(--accent);background:rgba(124,92,252,0.1)}}
.opt-btn.correct{{border-color:var(--correct-border)!important;background:var(--correct-bg)!important}}
.opt-btn.wrong{{border-color:var(--wrong-border)!important;background:var(--wrong-bg)!important}}
.opt-btn.disabled{{cursor:default;opacity:.85}}
.opt-btn .opt-letter{{min-width:28px;height:28px;border-radius:50%;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem;flex-shrink:0;transition:all .2s}}
.opt-btn.correct .opt-letter{{background:var(--correct);color:#fff}}
.opt-btn.wrong .opt-letter{{background:var(--wrong);color:#fff}}
.opt-icon{{margin-inline-start:auto;font-size:1.1rem}}

/* EXPLANATION */
.explanation{{display:none;margin-top:12px;padding:14px;background:var(--bg);border:1px solid var(--bg3);border-radius:var(--radius-sm);font-size:.85rem;line-height:1.9}}
.explanation.show{{display:block;animation:fadeIn .3s ease}}
.explanation h4{{color:var(--accent2);margin-bottom:8px;font-size:.9rem}}
.exp-opt{{margin-bottom:8px;padding:8px 10px;border-radius:6px}}
.exp-opt.exp-correct{{background:var(--correct-bg);border-right:3px solid var(--correct)}}
.exp-opt.exp-wrong{{background:var(--wrong-bg);border-right:3px solid var(--wrong)}}
.exp-opt b{{display:block;margin-bottom:2px}}

/* TOOLTIP */
[data-tooltip]{{position:relative}}
[data-tooltip]:hover::after{{content:attr(data-tooltip);position:absolute;bottom:105%;right:0;background:var(--bg2);color:var(--text);padding:6px 10px;border-radius:6px;font-size:.78rem;white-space:pre-wrap;max-width:320px;z-index:99;box-shadow:var(--shadow);border:1px solid var(--bg3);pointer-events:none;animation:fadeIn .2s}}

/* RESULT */
.result-box{{background:var(--card);border:2px solid var(--accent);border-radius:var(--radius);padding:24px;margin:20px 0;display:none}}
.result-box.show{{display:block;animation:fadeIn .4s}}
.result-score{{font-size:2.5rem;font-weight:800;text-align:center;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.result-details{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-top:16px}}
.result-stat{{text-align:center;padding:12px;border-radius:var(--radius-sm);background:var(--bg)}}
.result-stat .num{{font-size:1.5rem;font-weight:800}}
.result-stat .label{{font-size:.8rem;color:var(--text2)}}

/* BOOKMARK LABEL MODAL */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:200;align-items:center;justify-content:center}}
.modal-overlay.show{{display:flex}}
.modal{{background:var(--bg2);border:1px solid var(--bg3);border-radius:var(--radius);padding:24px;max-width:400px;width:90%}}
.modal h3{{margin-bottom:12px}}
.modal input{{width:100%;padding:10px;border:1px solid var(--bg3);border-radius:var(--radius-sm);background:var(--bg);color:var(--text);font-family:var(--font-ar);font-size:1rem;margin-bottom:8px}}
.modal .btn{{margin-top:8px}}

/* TOPIC FILTER */
.topic-panel{{display:none;padding:10px 20px;background:var(--bg2);border-bottom:1px solid var(--bg3)}}
.topic-panel.show{{display:flex;flex-wrap:wrap;gap:6px}}
.topic-btn{{font-size:.78rem}}

@keyframes fadeIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}

/* MOBILE */
@media(max-width:768px){{
  .sidebar{{width:100%;height:auto;position:fixed;bottom:0;top:auto;left:0;right:0;padding:8px;display:flex;flex-wrap:wrap;gap:3px;justify-content:center;border-right:none;border-top:2px solid var(--bg3);max-height:40vh;overflow-y:auto}}
  .nav-btn{{width:32px;height:32px;aspect-ratio:1;font-size:.65rem}}
  .main{{margin-left:0;padding:12px;padding-bottom:200px}}
  .header{{position:sticky;top:0}}
  .filter-bar{{top:auto;position:relative}}
  .q-card{{padding:14px}}
}}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <h1>📝 بنك أسئلة نظم التشغيل - 180 سؤال</h1>
    <div class="header-btns">
      <button class="btn" onclick="toggleTheme()" id="themeBtn">🌙 الوضع</button>
      <button class="btn" onclick="shuffleQuestions()">🔀 خلط</button>
      <button class="btn" onclick="saveProgress()">💾 حفظ</button>
      <button class="btn" onclick="loadProgress()">📂 استعادة</button>
      <button class="btn" onclick="showResults()">📊 النتائج</button>
      <button class="btn" onclick="toggleTopics()">📁 المواضيع</button>
      <button class="btn btn-danger" onclick="resetAll()">🗑️ مسح الكل</button>
    </div>
  </div>
  <div class="progress-wrap">
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="progress-text"><span id="progressText">0 / 180</span><span id="progressPct">0%</span></div>
  </div>
</div>

<div class="topic-panel" id="topicPanel"></div>

<div class="filter-bar" id="filterBar">
  <button class="btn active" data-filter="all" onclick="setFilter('all',this)">الكل (180)</button>
  <button class="btn" data-filter="unanswered" onclick="setFilter('unanswered',this)">❓ لم يُجب</button>
  <button class="btn" data-filter="correct" onclick="setFilter('correct',this)">✅ صحيح</button>
  <button class="btn" data-filter="wrong" onclick="setFilter('wrong',this)">❌ خطأ</button>
  <span style="border-left:1px solid var(--bg3);margin:0 4px"></span>
  <button class="btn" data-filter="bm-red" onclick="setFilter('bm-red',this)"><span class="bookmark-dot" style="background:var(--bookmark-red)"></span><span class="bm-label-red">أحمر</span></button>
  <button class="btn" data-filter="bm-yellow" onclick="setFilter('bm-yellow',this)"><span class="bookmark-dot" style="background:var(--bookmark-yellow)"></span><span class="bm-label-yellow">أصفر</span></button>
  <button class="btn" data-filter="bm-green" onclick="setFilter('bm-green',this)"><span class="bookmark-dot" style="background:var(--bookmark-green)"></span><span class="bm-label-green">أخضر</span></button>
  <button class="btn" data-filter="bm-blue" onclick="setFilter('bm-blue',this)"><span class="bookmark-dot" style="background:var(--bookmark-blue)"></span><span class="bm-label-blue">أزرق</span></button>
  <span style="border-left:1px solid var(--bg3);margin:0 4px"></span>
  <button class="btn btn-danger" onclick="undoBookmarkGroup()">↩️ تراجع علامة</button>
</div>

<div class="sidebar" id="sidebar"></div>

<div class="main" id="main">
  <div id="questionsContainer"></div>
  <div class="result-box" id="resultBox">
    <h2 style="text-align:center;margin-bottom:8px">📊 النتائج</h2>
    <div class="result-score" id="resultScore">0%</div>
    <div class="result-details" id="resultDetails"></div>
    <div id="wrongList" style="margin-top:16px"></div>
  </div>
</div>

<div class="modal-overlay" id="bmModal">
  <div class="modal">
    <h3>✏️ تسمية العلامة</h3>
    <input id="bmLabelInput" placeholder="اسم العلامة...">
    <div style="display:flex;gap:8px">
      <button class="btn" onclick="saveBmLabel()">حفظ</button>
      <button class="btn" onclick="closeBmModal()">إلغاء</button>
    </div>
  </div>
</div>

<div class="modal-overlay" id="undoBmModal">
  <div class="modal">
    <h3>↩️ تراجع عن علامة</h3>
    <p style="margin-bottom:12px;color:var(--text2)">اختر لون العلامة لإزالتها من جميع الأسئلة:</p>
    <div style="display:flex;gap:8px;justify-content:center">
      <button class="bm-color-btn" style="background:var(--bookmark-red)" onclick="removeAllBookmarks('red')"></button>
      <button class="bm-color-btn" style="background:var(--bookmark-yellow)" onclick="removeAllBookmarks('yellow')"></button>
      <button class="bm-color-btn" style="background:var(--bookmark-green)" onclick="removeAllBookmarks('green')"></button>
      <button class="bm-color-btn" style="background:var(--bookmark-blue)" onclick="removeAllBookmarks('blue')"></button>
    </div>
    <button class="btn" style="margin-top:12px;width:100%" onclick="closeUndoBmModal()">إلغاء</button>
  </div>
</div>

<script>
const QUESTIONS = {questions_json};
''' + '''
// ============ EXPLANATIONS (Arabic) ============
const EXPLANATIONS = {};
function getExplanations(q) {
  if (EXPLANATIONS[q.id]) return EXPLANATIONS[q.id];
  return null;
}

// ============ STATE ============
let state = {
  answers: {},       // qid -> selected index
  bookmarks: {},     // qid -> Set of colors
  bmLabels: {red:'أحمر',yellow:'أصفر',green:'أخضر',blue:'أزرق'},
  filter: 'all',
  theme: 'dark',
  questionOrder: QUESTIONS.map(q => q.id),
  topicFilter: null
};

const letters = ['A','B','C','D'];
const colors = ['red','yellow','green','blue'];
const colorVars = {red:'--bookmark-red',yellow:'--bookmark-yellow',green:'--bookmark-green',blue:'--bookmark-blue'};

// ============ RENDER ============
function renderAll() {
  renderQuestions();
  renderSidebar();
  renderTopics();
  updateProgress();
  updateFilterCounts();
  updateBmLabels();
}

function renderQuestions() {
  const container = document.getElementById('questionsContainer');
  container.innerHTML = '';
  const order = state.questionOrder;
  
  for (const qid of order) {
    const q = QUESTIONS.find(x => x.id === qid);
    if (!q) continue;
    
    const card = document.createElement('div');
    card.className = 'q-card';
    card.id = 'q-' + q.id;
    card.dataset.qid = q.id;
    
    const answered = state.answers[q.id] !== undefined;
    const selectedIdx = state.answers[q.id];
    const correctIdx = q.opts.findIndex(o => o.c);
    const isCorrect = answered && selectedIdx === correctIdx;
    
    // Bookmark indicators
    const bms = state.bookmarks[q.id] || new Set();
    let bmHTML = '';
    for (const c of bms) {
      bmHTML += `<span class="bookmark-dot" style="background:var(${colorVars[c]})"></span>`;
    }
    
    // Bookmark menu
    let bmMenuHTML = '<div class="bm-menu" id="bm-menu-'+q.id+'">';
    for (const c of colors) {
      const isActive = bms.has(c);
      bmMenuHTML += `<button class="bm-color-btn ${isActive?'active':''}" style="background:var(${colorVars[c]})" onclick="toggleBookmark(${q.id},'${c}')"></button>`;
    }
    bmMenuHTML += `<button class="btn" style="font-size:.7rem;margin-top:4px" onclick="renameBmPrompt(event)">✏️ تسمية</button>`;
    bmMenuHTML += '</div>';
    
    let optsHTML = '<div class="opts">';
    q.opts.forEach((opt, idx) => {
      let cls = 'opt-btn';
      let icon = '';
      if (answered) {
        cls += ' disabled';
        if (idx === correctIdx) { cls += ' correct'; icon = '✅'; }
        if (idx === selectedIdx && !isCorrect) { cls += ' wrong'; icon = '❌'; }
      }
      const letter = letters[idx] || (idx+1);
      optsHTML += `<button class="${cls}" onclick="selectAnswer(${q.id},${idx})" ${answered?'disabled':''}>
        <span class="opt-letter">${letter}</span>
        <span class="en">${escapeHtml(opt.t)}</span>
        ${icon ? '<span class="opt-icon">'+icon+'</span>' : ''}
      </button>`;
    });
    optsHTML += '</div>';
    
    // Explanation
    let expHTML = '';
    if (answered) {
      const exp = getExplanations(q);
      if (exp) {
        expHTML = '<div class="explanation show"><h4>📖 الشرح:</h4>';
        exp.forEach((e, idx) => {
          const isC = q.opts[idx] && q.opts[idx].c;
          expHTML += `<div class="exp-opt ${isC?'exp-correct':'exp-wrong'}">
            <b>${letters[idx] || idx+1}) ${escapeHtml(q.opts[idx]?.t || '')}</b>
            ${e}
          </div>`;
        });
        expHTML += '</div>';
      }
    }
    
    card.innerHTML = `
      <div class="q-header">
        <span class="q-number">${q.id}</span>
        <div class="q-text">
          <span class="en" data-tooltip="${getTooltip(q)}">${escapeHtml(q.q)}</span>
        </div>
        <div class="q-actions">
          ${bmHTML}
          <button class="btn" onclick="openBmMenu(${q.id})">🔖</button>
          ${bmMenuHTML}
          ${answered ? '<button class="btn" onclick="undoAnswer('+q.id+')">↩️</button>' : ''}
        </div>
      </div>
      <div class="q-topic" style="font-size:.75rem;color:var(--text3);margin-bottom:10px">📁 ${q.topic}</div>
      ${optsHTML}
      ${expHTML}
    `;
    container.appendChild(card);
  }
  applyFilter();
}

function renderSidebar() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = '';
  for (const qid of state.questionOrder) {
    const btn = document.createElement('button');
    btn.className = 'nav-btn';
    btn.textContent = qid;
    btn.onclick = () => scrollToQ(qid);
    
    const answered = state.answers[qid] !== undefined;
    if (answered) {
      const q = QUESTIONS.find(x => x.id === qid);
      const correctIdx = q.opts.findIndex(o => o.c);
      btn.classList.add(state.answers[qid] === correctIdx ? 'answered-correct' : 'answered-wrong');
    }
    
    // Bookmark indicators on nav
    const bms = state.bookmarks[qid] || new Set();
    let i = 0;
    for (const c of bms) {
      const dot = document.createElement('span');
      dot.className = 'bm-indicator' + (i > 0 ? ' bm-indicator-2' : '');
      dot.style.background = `var(${colorVars[c]})`;
      btn.appendChild(dot);
      i++;
      if (i >= 2) break;
    }
    sb.appendChild(btn);
  }
}

function renderTopics() {
  const panel = document.getElementById('topicPanel');
  const topics = [...new Set(QUESTIONS.map(q => q.topic))];
  panel.innerHTML = '<button class="btn topic-btn '+(state.topicFilter===null?'active':'')+'" onclick="filterTopic(null,this)">الكل</button>';
  for (const t of topics) {
    const count = QUESTIONS.filter(q => q.topic === t).length;
    panel.innerHTML += `<button class="btn topic-btn ${state.topicFilter===t?'active':''}" onclick="filterTopic('${t}',this)">${t} (${count})</button>`;
  }
}

// ============ ACTIONS ============
function selectAnswer(qid, idx) {
  if (state.answers[qid] !== undefined) return;
  state.answers[qid] = idx;
  renderAll();
  // Scroll nav button into view
  const navBtns = document.querySelectorAll('.nav-btn');
  const targetBtn = [...navBtns].find(b => b.textContent.trim() == qid);
  if (targetBtn) targetBtn.scrollIntoView({block:'nearest'});
}

function undoAnswer(qid) {
  delete state.answers[qid];
  renderAll();
}

function toggleBookmark(qid, color) {
  if (!state.bookmarks[qid]) state.bookmarks[qid] = new Set();
  if (state.bookmarks[qid].has(color)) {
    state.bookmarks[qid].delete(color);
    if (state.bookmarks[qid].size === 0) delete state.bookmarks[qid];
  } else {
    state.bookmarks[qid].add(color);
  }
  renderAll();
}

function openBmMenu(qid) {
  // Close all others first
  document.querySelectorAll('.bm-menu').forEach(m => m.classList.remove('show'));
  const menu = document.getElementById('bm-menu-' + qid);
  if (menu) menu.classList.toggle('show');
  event.stopPropagation();
}

function scrollToQ(qid) {
  const el = document.getElementById('q-' + qid);
  if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
}

function updateProgress() {
  const total = QUESTIONS.length;
  const answered = Object.keys(state.answers).length;
  const pct = Math.round(answered / total * 100);
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressText').textContent = answered + ' / ' + total;
  document.getElementById('progressPct').textContent = pct + '%';
}

// ============ FILTERS ============
function setFilter(f, btn) {
  state.filter = f;
  document.querySelectorAll('.filter-bar .btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  applyFilter();
}

function applyFilter() {
  const cards = document.querySelectorAll('.q-card');
  let visibleCount = 0;
  cards.forEach(card => {
    const qid = parseInt(card.dataset.qid);
    const q = QUESTIONS.find(x => x.id === qid);
    let show = true;
    
    // Topic filter
    if (state.topicFilter && q.topic !== state.topicFilter) show = false;
    
    // Status filter
    if (show) {
      const answered = state.answers[qid] !== undefined;
      const f = state.filter;
      if (f === 'unanswered' && answered) show = false;
      if (f === 'correct') {
        if (!answered) show = false;
        else { const ci = q.opts.findIndex(o=>o.c); if(state.answers[qid]!==ci) show = false; }
      }
      if (f === 'wrong') {
        if (!answered) show = false;
        else { const ci = q.opts.findIndex(o=>o.c); if(state.answers[qid]===ci) show = false; }
      }
      if (f.startsWith('bm-')) {
        const color = f.replace('bm-','');
        const bms = state.bookmarks[qid] || new Set();
        if (!bms.has(color)) show = false;
      }
    }
    
    card.classList.toggle('filtered-out', !show);
    if (show) visibleCount++;
  });
}

function updateFilterCounts() {
  const total = QUESTIONS.length;
  const answered = Object.keys(state.answers).length;
  let correct = 0, wrong = 0;
  for (const [qid, idx] of Object.entries(state.answers)) {
    const q = QUESTIONS.find(x => x.id === parseInt(qid));
    if (q && q.opts.findIndex(o=>o.c) === idx) correct++;
    else wrong++;
  }
  const unanswered = total - answered;
  
  const bmCounts = {};
  for (const c of colors) {
    bmCounts[c] = Object.values(state.bookmarks).filter(s => s.has(c)).length;
  }
  
  document.querySelector('[data-filter="all"]').textContent = `الكل (${total})`;
  document.querySelector('[data-filter="unanswered"]').textContent = `❓ لم يُجب (${unanswered})`;
  document.querySelector('[data-filter="correct"]').textContent = `✅ صحيح (${correct})`;
  document.querySelector('[data-filter="wrong"]').textContent = `❌ خطأ (${wrong})`;
  for (const c of colors) {
    const btn = document.querySelector(`[data-filter="bm-${c}"]`);
    if (btn) {
      const dot = btn.querySelector('.bookmark-dot');
      const label = btn.querySelector(`.bm-label-${c}`);
      if (label) label.textContent = `${state.bmLabels[c]} (${bmCounts[c]})`;
    }
  }
}

function filterTopic(topic, btn) {
  state.topicFilter = topic;
  document.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  applyFilter();
}

function toggleTopics() {
  document.getElementById('topicPanel').classList.toggle('show');
}

// ============ THEME ============
function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme === 'light' ? 'light' : '');
  document.getElementById('themeBtn').textContent = state.theme === 'dark' ? '🌙 الوضع' : '☀️ الوضع';
}

// ============ SHUFFLE ============
function shuffleQuestions() {
  const arr = [...state.questionOrder];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  state.questionOrder = arr;
  renderAll();
}

// ============ SAVE/LOAD ============
function saveProgress() {
  const data = {
    answers: state.answers,
    bookmarks: {},
    bmLabels: state.bmLabels,
    questionOrder: state.questionOrder,
    theme: state.theme
  };
  for (const [k, v] of Object.entries(state.bookmarks)) {
    data.bookmarks[k] = [...v];
  }
  localStorage.setItem('os_quiz_save', JSON.stringify(data));
  showToast('✅ تم الحفظ');
}

function loadProgress() {
  const raw = localStorage.getItem('os_quiz_save');
  if (!raw) { showToast('⚠️ لا يوجد حفظ سابق'); return; }
  const data = JSON.parse(raw);
  state.answers = data.answers || {};
  state.bmLabels = data.bmLabels || state.bmLabels;
  state.questionOrder = data.questionOrder || QUESTIONS.map(q => q.id);
  state.theme = data.theme || 'dark';
  state.bookmarks = {};
  for (const [k, v] of Object.entries(data.bookmarks || {})) {
    state.bookmarks[k] = new Set(v);
  }
  if (state.theme === 'light') document.documentElement.setAttribute('data-theme', 'light');
  renderAll();
  showToast('✅ تم الاستعادة');
}

// ============ RESET ============
function resetAll() {
  if (!confirm('هل أنت متأكد من مسح جميع الإجابات؟')) return;
  state.answers = {};
  renderAll();
  showToast('🗑️ تم مسح الإجابات');
}

// ============ BOOKMARK MANAGEMENT ============
function undoBookmarkGroup() {
  document.getElementById('undoBmModal').classList.add('show');
}
function closeUndoBmModal() {
  document.getElementById('undoBmModal').classList.remove('show');
}
function removeAllBookmarks(color) {
  for (const qid of Object.keys(state.bookmarks)) {
    state.bookmarks[qid].delete(color);
    if (state.bookmarks[qid].size === 0) delete state.bookmarks[qid];
  }
  closeUndoBmModal();
  renderAll();
  showToast('↩️ تم إزالة العلامات');
}

let currentBmColor = null;
function renameBmPrompt(e) {
  e.stopPropagation();
  document.getElementById('bmModal').classList.add('show');
  document.getElementById('bmLabelInput').value = '';
  document.getElementById('bmLabelInput').focus();
}
function saveBmLabel() {
  const val = document.getElementById('bmLabelInput').value.trim();
  if (!val) return;
  // Find which color to rename - pick from a prompt
  const color = prompt('أي لون تريد تسميته؟ (red/yellow/green/blue)', 'red');
  if (color && state.bmLabels[color] !== undefined) {
    state.bmLabels[color] = val;
    updateBmLabels();
  }
  closeBmModal();
}
function closeBmModal() {
  document.getElementById('bmModal').classList.remove('show');
}
function updateBmLabels() {
  for (const c of colors) {
    const el = document.querySelector(`.bm-label-${c}`);
    if (el) el.textContent = state.bmLabels[c];
  }
}

// ============ RESULTS ============
function showResults() {
  const total = QUESTIONS.length;
  const answered = Object.keys(state.answers).length;
  let correct = 0, wrong = 0;
  const wrongIds = [];
  
  for (const [qid, idx] of Object.entries(state.answers)) {
    const q = QUESTIONS.find(x => x.id === parseInt(qid));
    if (q && q.opts.findIndex(o=>o.c) === idx) correct++;
    else { wrong++; wrongIds.push(parseInt(qid)); }
  }
  
  const pct = answered > 0 ? Math.round(correct / total * 100) : 0;
  document.getElementById('resultScore').textContent = pct + '%';
  
  document.getElementById('resultDetails').innerHTML = `
    <div class="result-stat"><div class="num" style="color:var(--accent)">${answered}</div><div class="label">مُجاب</div></div>
    <div class="result-stat"><div class="num" style="color:var(--correct)">${correct}</div><div class="label">صحيح</div></div>
    <div class="result-stat"><div class="num" style="color:var(--wrong)">${wrong}</div><div class="label">خطأ</div></div>
    <div class="result-stat"><div class="num" style="color:var(--text2)">${total-answered}</div><div class="label">لم يُجب</div></div>
  `;
  
  let wrongHTML = '';
  if (wrongIds.length > 0) {
    wrongHTML = '<h3 style="margin-bottom:8px;color:var(--wrong)">❌ الأسئلة الخاطئة:</h3>';
    wrongIds.sort((a,b) => a-b);
    for (const id of wrongIds) {
      const q = QUESTIONS.find(x => x.id === id);
      wrongHTML += `<div style="padding:6px;cursor:pointer;border-radius:6px;margin-bottom:4px;background:var(--bg);font-size:.85rem" onclick="scrollToQ(${id})">
        <b>سؤال ${id}:</b> ${escapeHtml(q.q).substring(0,60)}...
      </div>`;
    }
  }
  document.getElementById('wrongList').innerHTML = wrongHTML;
  
  const box = document.getElementById('resultBox');
  box.classList.add('show');
  box.scrollIntoView({behavior:'smooth'});
}

// ============ UTILS ============
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showToast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:var(--bg2);color:var(--text);padding:10px 24px;border-radius:99px;z-index:999;font-size:.9rem;border:1px solid var(--bg3);box-shadow:var(--shadow);animation:fadeIn .3s';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2000);
}

function getTooltip(q) {
  // Return Arabic tooltip for question
  return '';  // Will be populated by enrichment
}

// Close menus on click outside
document.addEventListener('click', () => {
  document.querySelectorAll('.bm-menu').forEach(m => m.classList.remove('show'));
});

// ============ INIT ============
renderAll();
</script>
</body>
</html>'''
    
    output_path = os.path.join(SCRIPT_DIR, 'os_quiz.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {output_path}")

def escapeHtml(s):
    return html.escape(s)

if __name__ == '__main__':
    generate()
