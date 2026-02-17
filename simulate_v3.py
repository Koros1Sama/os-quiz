import json, re

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

def get_words(text):
    return set(re.findall(r'[a-zA-Z]+', text.lower()))

STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','process','when','between','if','all','none',
              'true','false','above','mentioned','these','both'}

TIER1 = ['circular','unauthorized','wait','pages','switching','than','create','web','allows','among','highest']
TIER2 = ['ready','each','compiling','part','executing']
TIER3 = ['all','data','scheduler','more','about','stores','ntfs','collection','response','physical','hard','share','accounting','metadata','managing']
TRAP_WORDS = ['single','allocates','prevention','prevent','prevents','preventing','prevented',
              'reduce','reduces','reduced','reducing','reduction',
              'macos','segmentation','deadlocks','speed','manager',
              'memory']  # NEW: memory is 86% wrong!

# Golden duplicate keywords: when in EXACTLY 2 options, answer is one of them (100%)
GOLDEN_DUP_WORDS_2ONLY = ['cpu', 'file', 'threads']  # only work at exactly 2
GOLDEN_DUP_WORDS_ANY = ['process']  # works at 2+ options

def apply_algorithm(q):
    opts = q["options"]
    q_text = q["text"]
    is_not = bool(re.search(r'\bnot\b', q_text, re.IGNORECASE))
    is_tf = len(opts) == 2
    cleaned = [(clean(o["text"]), o["correct"]) for o in opts]
    
    # T/F
    if is_tf:
        for text, correct in cleaned:
            if re.search(r'\bnot\b|does not|cannot|can not', text, re.IGNORECASE):
                return (False, 'certain', 'T/F: negation')
        return (True, 'certain', 'T/F: positive')
    
    # All of mentioned
    for text, correct in cleaned:
        if re.search(r'\ball\s+(of\s+)?(the\s+)?(mentioned|above)', text, re.IGNORECASE):
            return (correct, 'certain', 'All of the mentioned')
    
    # Eliminate None
    has_none = False
    non_none = []
    for text, correct in cleaned:
        if re.search(r'\bnone\b', text, re.IGNORECASE):
            has_none = True
        else:
            non_none.append((text, correct))
    if has_none and len(non_none) < len(cleaned):
        cleaned = non_none
    
    # Eliminate Schedules
    filtered = [(t, c) for t, c in cleaned if not t.lower().startswith('schedules')]
    if len(filtered) < len(cleaned) and len(filtered) > 0:
        cleaned = filtered
    
    # Eliminate trap words (including memory now!)
    # But skip memory trap if the question is ABOUT memory (has memory in question text)
    q_about_memory = 'memory' in q_text.lower()
    
    filtered = []
    for text, correct in cleaned:
        words = text.lower().split()
        has_trap = False
        for tw in TRAP_WORDS:
            if tw in words:
                # Skip memory filter if question is about memory
                if tw == 'memory' and q_about_memory:
                    continue
                has_stronger = any(kw in words for kw in TIER1) or any(kw in words for kw in TIER2)
                if not has_stronger:
                    has_trap = True
                    break
        if not has_trap:
            filtered.append((text, correct))
    if len(filtered) > 0 and len(filtered) < len(cleaned):
        cleaned = filtered
    
    # Scheduling filter
    if not is_not and not re.search(r'schedul', q_text, re.IGNORECASE):
        filtered = [(t, c) for t, c in cleaned if 'scheduling' not in t.lower().split()]
        if len(filtered) > 0 and len(filtered) < len(cleaned):
            cleaned = filtered
    
    if len(cleaned) == 1:
        return (cleaned[0][1], 'certain', 'Only option left')
    
    # NOT
    if is_not:
        for text, correct in cleaned:
            words = text.lower().split()
            t1_options = [(t, c) for t, c in cleaned if any(kw in t.lower().split() for kw in TIER1)]
            if len(t1_options) == 1:
                return (t1_options[0][1], 'certain', 'NOT + Tier1')
        shortest = min(cleaned, key=lambda x: len(x[0]))
        return (shortest[1], 'probable', 'NOT: shortest')
    
    # Tier 1
    for kw in TIER1:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            return (matching[0][1], 'certain', f'Tier1: {kw}')
    
    # Tier 2
    for kw in TIER2:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            if kw == 'each':
                if any('share' in t.lower().split() or 'among' in t.lower().split() for t, c in cleaned):
                    continue
            return (matching[0][1], 'probable', f'Tier2: {kw}')
    
    # Parentheses
    paren_opts = [(t, c) for t, c in cleaned if '(' in t and ')' in t]
    non_paren = [(t, c) for t, c in cleaned if '(' not in t or ')' not in t]
    if len(paren_opts) > 0 and len(non_paren) > 0 and len(paren_opts) < len(cleaned):
        return (paren_opts[0][1], 'probable', 'Parentheses')
    
    # Echo
    q_words = get_words(q_text) - STOP_WORDS
    echo_scores = []
    for text, correct in cleaned:
        opt_words = get_words(text)
        shared = q_words & opt_words
        echo_scores.append((len(shared), text, correct))
    max_echo = max(s[0] for s in echo_scores)
    if max_echo > 0:
        echo_winners = [s for s in echo_scores if s[0] == max_echo]
        if len(echo_winners) == 1:
            return (echo_winners[0][2], 'probable', 'Echo')
    
    # ★ NEW: Golden Duplicate Keywords (100% when in exactly 2 options)
    word_to_opts = {}
    for i, (text, correct) in enumerate(cleaned):
        words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        for w in words:
            if w not in word_to_opts:
                word_to_opts[w] = []
            word_to_opts[w].append(i)
    
    # Check "any count" golden words first (process)
    for gw in GOLDEN_DUP_WORDS_ANY:
        if gw in word_to_opts and len(word_to_opts[gw]) >= 2 and len(word_to_opts[gw]) < len(cleaned):
            indices = word_to_opts[gw]
            candidates = [(cleaned[i][0], cleaned[i][1]) for i in indices]
            longest = max(candidates, key=lambda x: len(x[0].split()))
            return (longest[1], 'probable', f'GoldenDup({gw}): longest')
    
    # Check "2 only" golden words (cpu, file, threads)
    for gw in GOLDEN_DUP_WORDS_2ONLY:
        if gw in word_to_opts and len(word_to_opts[gw]) == 2:
            indices = word_to_opts[gw]
            opt_a, correct_a = cleaned[indices[0]]
            opt_b, correct_b = cleaned[indices[1]]
            if len(opt_a.split()) >= len(opt_b.split()):
                return (correct_a, 'probable', f'GoldenDup({gw}): longer')
            else:
                return (correct_b, 'probable', f'GoldenDup({gw}): longer')
    
    # Longest
    word_counts = [(len(t.split()), t, c) for t, c in cleaned]
    max_wc = max(s[0] for s in word_counts)
    longest_winners = [s for s in word_counts if s[0] == max_wc]
    if len(longest_winners) == 1:
        conf = 'gamble' if has_none else 'probable'
        return (longest_winners[0][2], conf, 'Longest')
    
    # Tier 3
    for kw in TIER3:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            return (matching[0][1], 'gamble', f'Tier3: {kw}')
    
    return (longest_winners[0][2], 'gamble', 'Tie-breaker')

# RUN
total_correct = 0
certain_c, certain_t = 0, 0
probable_c, probable_t = 0, 0
gamble_c, gamble_t = 0, 0
wrong_qs = []

for q in questions:
    result, confidence, rule = apply_algorithm(q)
    is_correct = result == True
    if is_correct: total_correct += 1
    else: wrong_qs.append(q['id'])
    if confidence == 'certain':
        certain_t += 1
        if is_correct: certain_c += 1
    elif confidence == 'probable':
        probable_t += 1
        if is_correct: probable_c += 1
    else:
        gamble_t += 1
        if is_correct: gamble_c += 1

print("=" * 60)
print("📊 النتائج بعد إضافة memory كفخ + كلمات ذهبية مكررة")
print("=" * 60)
print(f"\n✅ المجموع: {total_correct}/180 = {total_correct*100//180}%")
print(f"🟢 مؤكد: {certain_c}/{certain_t} = {certain_c*100//certain_t if certain_t else 0}%")
print(f"🟡 محتمل: {probable_c}/{probable_t} = {probable_c*100//probable_t if probable_t else 0}%")
print(f"🔴 مقامرة: {gamble_c}/{gamble_t} = {gamble_c*100//gamble_t if gamble_t else 0}%")
print(f"\n❌ أسئلة غلط ({len(wrong_qs)}): {sorted(wrong_qs)}")

# Show what each new rule contributed
print(f"\n--- تفاصيل القواعد الجديدة ---")
for q in questions:
    result, confidence, rule = apply_algorithm(q)
    if 'GoldenDup' in rule or ('memory' in rule.lower()):
        correct_text = clean([o["text"] for o in q["options"] if o["correct"]][0])
        emoji = "✅" if result else "❌"
        print(f"  {emoji} Q{q['id']}: {rule} → {correct_text[:50]}")
