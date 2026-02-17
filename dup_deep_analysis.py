import json, re
from collections import Counter, defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','process','when','between','if','all','none',
              'true','false','above','mentioned','these','both','more','most'}

# Questions already solved by earlier rules (from simulation)
ALREADY_SOLVED = set()
TIER1 = ['circular','unauthorized','wait','pages','switching','than','create','web','allows','among','highest']
TIER2 = ['ready','each','compiling','part','executing']
TRAP_WORDS = ['single','allocates','prevention','prevent','prevents','preventing','prevented',
              'reduce','reduces','reduced','reducing','reduction','macos','segmentation','deadlocks','speed','manager']

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# First pass: identify which questions are solved by earlier rules
for q in questions:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    qtext = q["text"]
    is_not = bool(re.search(r'\bnot\b', qtext, re.IGNORECASE))
    
    # All/None/TF/Schedules/Traps
    if len(opts) == 2: ALREADY_SOLVED.add(q['id']); continue
    if any(re.search(r'\ball\s+(of\s+)?(the\s+)?(mentioned|above)', t, re.IGNORECASE) for t,c in opts):
        ALREADY_SOLVED.add(q['id']); continue
    
    # Check if Tier 1 or 2 uniquely solves it
    non_none = [(t,c) for t,c in opts if not re.search(r'\bnone\b', t, re.IGNORECASE)]
    for kw in TIER1:
        matching = [t for t,c in non_none if kw in t.lower().split()]
        if len(matching) == 1:
            ALREADY_SOLVED.add(q['id']); break

print(f"أسئلة محلولة مسبقاً: {len(ALREADY_SOLVED)}/180")
print(f"أسئلة متبقية للتحليل: {180 - len(ALREADY_SOLVED)}")

# Second pass: analyze duplicate keyword ONLY on unsolved questions
remaining_qs = [q for q in questions if q['id'] not in ALREADY_SOLVED]

# Per-word accuracy tracking
word_stats = defaultdict(lambda: {'total': 0, 'correct_in_pair': 0, 'questions': []})

for q in remaining_qs:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    correct_idx = next(i for i,(t,c) in enumerate(opts) if c)
    
    # Find words in exactly 2 options
    word_to_opts = {}
    for i, (text, _) in enumerate(opts):
        words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        for w in words:
            if w in STOP_WORDS or len(w) <= 2:
                continue
            if w not in word_to_opts:
                word_to_opts[w] = []
            word_to_opts[w].append(i)
    
    pair_words = {w: indices for w, indices in word_to_opts.items() if len(indices) == 2}
    
    for word, indices in pair_words.items():
        word_stats[word]['total'] += 1
        if correct_idx in indices:
            word_stats[word]['correct_in_pair'] += 1
            word_stats[word]['questions'].append(f"Q{q['id']}✅")
        else:
            word_stats[word]['questions'].append(f"Q{q['id']}❌")

# Sort by total appearances
print(f"\n{'='*70}")
print("📊 دقة كل كلمة مكررة (بعد استبعاد المحلول مسبقاً)")
print(f"{'='*70}")

print(f"\n--- كلمات ظهرت 3+ مرات (أمكن نثق فيها) ---")
for word, stats in sorted(word_stats.items(), key=lambda x: -x[1]['total']):
    if stats['total'] >= 3:
        pct = stats['correct_in_pair'] * 100 // stats['total']
        emoji = "🟢" if pct >= 75 else ("🟡" if pct >= 50 else "🔴")
        print(f"  {emoji} \"{word}\": {stats['correct_in_pair']}/{stats['total']} = {pct}% — {', '.join(stats['questions'])}")

print(f"\n--- كلمات ظهرت مرتين ---")
for word, stats in sorted(word_stats.items(), key=lambda x: -x[1]['correct_in_pair']):
    if stats['total'] == 2:
        pct = stats['correct_in_pair'] * 100 // stats['total']
        emoji = "🟢" if pct >= 75 else ("🟡" if pct >= 50 else "🔴")
        print(f"  {emoji} \"{word}\": {stats['correct_in_pair']}/{stats['total']} = {pct}% — {', '.join(stats['questions'])}")

# Overall accuracy on remaining questions only
total_with_pairs = 0
correct_pairs = 0
for q in remaining_qs:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    correct_idx = next(i for i,(t,c) in enumerate(opts) if c)
    
    word_to_opts = {}
    for i, (text, _) in enumerate(opts):
        words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        for w in words:
            if w in STOP_WORDS or len(w) <= 2:
                continue
            if w not in word_to_opts:
                word_to_opts[w] = []
            word_to_opts[w].append(i)
    
    pair_words = {w: indices for w, indices in word_to_opts.items() if len(indices) == 2}
    if pair_words:
        total_with_pairs += 1
        # Is correct answer in ANY pair?
        for w, indices in pair_words.items():
            if correct_idx in indices:
                correct_pairs += 1
                break

print(f"\n{'='*70}")
print(f"📊 الدقة على الأسئلة الغير محلولة فقط:")
print(f"  أسئلة فيها نمط: {total_with_pairs}/{len(remaining_qs)}")
print(f"  الجواب أحد الخيارين: {correct_pairs}/{total_with_pairs} = {correct_pairs*100//total_with_pairs if total_with_pairs else 0}%")

# Find HIGH accuracy words (>=75%) that appear 2+ times
print(f"\n{'='*70}")
print(f"🎯 كلمات عالية الدقة (≥75%، ظهرت 2+ مرة):")
good_words = []
for word, stats in sorted(word_stats.items(), key=lambda x: -x[1]['total']):
    if stats['total'] >= 2:
        pct = stats['correct_in_pair'] * 100 // stats['total']
        if pct >= 75:
            good_words.append(word)
            print(f"  ✅ \"{word}\": {stats['correct_in_pair']}/{stats['total']} = {pct}%")

print(f"\n  المجموع: {len(good_words)} كلمة عالية الدقة")
