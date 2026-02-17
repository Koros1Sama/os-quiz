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
              'type','system','operating','os','process','when','between'}

TIER1 = ['circular','unauthorized','wait','pages','switching','than','create','web','allows','among','highest']
TIER2 = ['ready','each','compiling','part','executing']
TIER3 = ['all','data','scheduler','more','about','stores','ntfs','collection','response','physical','hard','share','accounting','metadata','managing']
TRAP_WORDS = ['single','allocates','prevention','prevent','prevents','preventing','prevented',
              'reduce','reduces','reduced','reducing','reduction',
              'macos','segmentation','deadlocks','speed','manager']

def apply_algorithm(q):
    """Apply the algorithm to a question. Returns (pick, confidence, rule_used)"""
    opts = q["options"]
    q_text = q["text"]
    is_not = bool(re.search(r'\bnot\b', q_text, re.IGNORECASE))
    is_tf = len(opts) == 2
    
    cleaned = [(clean(o["text"]), o["correct"]) for o in opts]
    
    # STEP 0: True/False
    if is_tf:
        for text, correct in cleaned:
            if re.search(r'\bnot\b|does not|cannot|can not', text, re.IGNORECASE):
                return (False, 'certain', 'T/F: negation → FALSE')  # pick FALSE
        return (True, 'certain', 'T/F: positive → TRUE')  # pick TRUE (always correct for positive)
    
    # STEP 1a: "All of the mentioned/above"
    for text, correct in cleaned:
        if re.search(r'\ball\s+(of\s+)?(the\s+)?(mentioned|above)', text, re.IGNORECASE):
            return (correct, 'certain', 'All of the mentioned')
    
    # STEP 1b: Eliminate "None" options (always wrong)
    has_none = False
    non_none = []
    for text, correct in cleaned:
        if re.search(r'\bnone\b', text, re.IGNORECASE):
            has_none = True
        else:
            non_none.append((text, correct))
    
    if has_none and len(non_none) < len(cleaned):
        cleaned = non_none  # remove None from consideration
    
    # STEP 1c: Eliminate "Schedules..." options
    filtered = [(t, c) for t, c in cleaned if not t.lower().startswith('schedules')]
    if len(filtered) < len(cleaned) and len(filtered) > 0:
        cleaned = filtered
    
    # STEP 1d: Eliminate trap words
    filtered = []
    for text, correct in cleaned:
        words = text.lower().split()
        has_trap = False
        for tw in TRAP_WORDS:
            if tw in words:
                # Check if a stronger keyword saves it
                has_stronger = False
                for kw in TIER1:
                    if kw in words:
                        has_stronger = True
                        break
                if not has_stronger:
                    # Check Tier 2
                    for kw in TIER2:
                        if kw in words:
                            has_stronger = True
                            break
                if not has_stronger:
                    has_trap = True
                    break
        if not has_trap:
            filtered.append((text, correct))
    
    if len(filtered) > 0 and len(filtered) < len(cleaned):
        cleaned = filtered
    
    # STEP 1e: "Scheduling" filter (88% wrong, except in NOT or scheduling-about questions)
    if not is_not and not re.search(r'schedul', q_text, re.IGNORECASE):
        filtered = [(t, c) for t, c in cleaned if 'scheduling' not in t.lower().split()]
        if len(filtered) > 0 and len(filtered) < len(cleaned):
            cleaned = filtered
    
    # If only 1 option left after elimination → pick it
    if len(cleaned) == 1:
        return (cleaned[0][1], 'certain', 'Only option left after elimination')
    
    # NOT QUESTIONS - special handling
    if is_not:
        # Tier 1 still works in NOT
        for text, correct in cleaned:
            words = text.lower().split()
            t1_count = sum(1 for kw in TIER1 if kw in words)
            if t1_count > 0:
                # Check if only one option has Tier 1
                t1_options = [(t, c) for t, c in cleaned if any(kw in t.lower().split() for kw in TIER1)]
                if len(t1_options) == 1:
                    return (t1_options[0][1], 'certain', f'NOT + Tier1 unique')
        
        # NOT - pick the "odd one out" (shortest/most different)
        # Don't use longest!
        shortest = min(cleaned, key=lambda x: len(x[0]))
        return (shortest[1], 'probable', 'NOT: shortest/odd-one-out')
    
    # STEP 3: Golden Keywords - Tier 1
    for kw in TIER1:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            return (matching[0][1], 'certain', f'Tier1: {kw}')
    
    # STEP 3: Golden Keywords - Tier 2
    for kw in TIER2:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            # Check for T2 that lose to others
            if kw == 'each':
                # each loses to share/among
                for t, c in cleaned:
                    if 'share' in t.lower().split() or 'among' in t.lower().split():
                        break
                else:
                    return (matching[0][1], 'probable', f'Tier2: {kw}')
            else:
                return (matching[0][1], 'probable', f'Tier2: {kw}')
    
    # STEP: Parentheses rule (90%)
    paren_opts = [(t, c) for t, c in cleaned if '(' in t and ')' in t]
    non_paren = [(t, c) for t, c in cleaned if '(' not in t or ')' not in t]
    if len(paren_opts) > 0 and len(non_paren) > 0 and len(paren_opts) < len(cleaned):
        return (paren_opts[0][1], 'probable', 'Parentheses rule')
    
    # STEP: Echo rule (69%)
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
            # Echo has a clear winner
            # Also check longest
            word_counts = [(len(t.split()), t, c) for t, c in cleaned]
            max_wc = max(s[0] for s in word_counts)
            longest_winners = [s for s in word_counts if s[0] == max_wc]
            
            if len(longest_winners) == 1 and longest_winners[0][1] == echo_winners[0][1]:
                # Echo and Longest AGREE
                return (echo_winners[0][2], 'probable', 'Echo+Longest agree')
            else:
                # Echo alone
                return (echo_winners[0][2], 'probable', 'Echo rule')
    
    # STEP: Longest option (with None penalty)
    word_counts = [(len(t.split()), t, c) for t, c in cleaned]
    max_wc = max(s[0] for s in word_counts)
    longest_winners = [s for s in word_counts if s[0] == max_wc]
    
    if len(longest_winners) == 1:
        conf = 'gamble' if has_none else 'probable'
        return (longest_winners[0][2], conf, f'Longest option {"(with None penalty)" if has_none else ""}')
    
    # STEP: Tier 3
    for kw in TIER3:
        matching = [(t, c) for t, c in cleaned if kw in t.lower().split()]
        if len(matching) == 1:
            return (matching[0][1], 'gamble', f'Tier3: {kw}')
    
    # Last resort: pick longest among ties
    return (longest_winners[0][2], 'gamble', 'Tie-breaker: first longest')

# RUN SIMULATION
certain_correct = 0
certain_total = 0
probable_correct = 0
probable_total = 0
gamble_correct = 0
gamble_total = 0
total_correct = 0

results = []

for q in questions:
    result, confidence, rule = apply_algorithm(q)
    is_correct = result == True
    
    results.append({
        'id': q['id'],
        'correct': is_correct,
        'confidence': confidence,
        'rule': rule
    })
    
    if is_correct:
        total_correct += 1
    
    if confidence == 'certain':
        certain_total += 1
        if is_correct:
            certain_correct += 1
    elif confidence == 'probable':
        probable_total += 1
        if is_correct:
            probable_correct += 1
    else:
        gamble_total += 1
        if is_correct:
            gamble_correct += 1

print("=" * 70)
print("📊 نتائج محاكاة الخوارزمية على 180 سؤال")
print("=" * 70)

print(f"\n✅ إجمالي الأسئلة الصحيحة: {total_correct}/180 = {total_correct*100//180}%")

print(f"\n--- تفصيل حسب مستوى الثقة ---")
print(f"🟢 مؤكد (certain):  {certain_correct}/{certain_total} = {certain_correct*100//certain_total if certain_total else 0}%")
print(f"🟡 محتمل (probable): {probable_correct}/{probable_total} = {probable_correct*100//probable_total if probable_total else 0}%")
print(f"🔴 مقامرة (gamble):  {gamble_correct}/{gamble_total} = {gamble_correct*100//gamble_total if gamble_total else 0}%")

print(f"\n--- مدى النتيجة ---")
min_score = certain_correct  # guaranteed minimum
mid_score = certain_correct + probable_correct
max_score = total_correct
print(f"🔒 الحد الأدنى المضمون: {min_score}/180 = {min_score*100//180}%")
print(f"📈 مع المحتمل: {mid_score}/180 = {mid_score*100//180}%")
print(f"🎯 أقصى حد (كل شي يشتغل): {max_score}/180 = {max_score*100//180}%")

# Print wrong answers for review
print(f"\n--- الأسئلة اللي الخوارزمية غلطت فيها ---")
for r in results:
    if not r['correct']:
        q = [q for q in questions if q['id'] == r['id']][0]
        correct_text = [clean(o["text"]) for o in q["options"] if o["correct"]][0]
        print(f"  Q{r['id']} [{r['confidence']}] ({r['rule']})")
        print(f"    → الجواب الصحيح: {correct_text[:60]}")

# Print certain+wrong (bugs in algorithm)
print(f"\n--- ⚠️ أخطاء 'مؤكدة' (باقات بالخوارزمية) ---")
bugs = [r for r in results if not r['correct'] and r['confidence'] == 'certain']
for r in bugs:
    q = [q for q in questions if q['id'] == r['id']][0]
    correct_text = [clean(o["text"]) for o in q["options"] if o["correct"]][0]
    print(f"  Q{r['id']}: ({r['rule']}) → الصح: {correct_text[:60]}")

print(f"\n  عدد الباقات: {len(bugs)}")
