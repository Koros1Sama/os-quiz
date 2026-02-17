import json, re
from collections import Counter

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','when','between','if','all','none',
              'true','false','above','mentioned','these','both'}

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

def get_words(text):
    return [w.lower() for w in re.findall(r'[a-zA-Z]+', text)]

# ============ ANALYSIS ============
# For each question, find words appearing in EXACTLY 2 options
# Check if the correct answer is always one of those 2

total_questions_with_pairs = 0
correct_in_pair = 0
correct_not_in_pair = 0
pair_details = []

# Also track: when correct is in the pair, is it the longer one?
longer_wins = 0
shorter_wins = 0
same_len = 0

for q in questions:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    
    # Count word frequency across options
    word_to_opts = {}  # word -> list of option indices
    for i, (text, _) in enumerate(opts):
        words = set(get_words(text))
        for w in words:
            if w in STOP_WORDS or len(w) <= 2:
                continue
            if w not in word_to_opts:
                word_to_opts[w] = []
            word_to_opts[w].append(i)
    
    # Find words in exactly 2 options
    pair_words = {w: indices for w, indices in word_to_opts.items() if len(indices) == 2}
    
    if not pair_words:
        continue
    
    # For each pair word, check if correct answer is in the pair
    correct_idx = next(i for i, (_, c) in enumerate(opts) if c)
    
    best_pair = None
    for word, indices in pair_words.items():
        if correct_idx in indices:
            if best_pair is None or len(word) > len(best_pair[0]):
                best_pair = (word, indices)
    
    # Track overall stats
    any_pair_has_correct = any(correct_idx in indices for indices in pair_words.values())
    
    total_questions_with_pairs += 1
    if any_pair_has_correct:
        correct_in_pair += 1
    else:
        correct_not_in_pair += 1
    
    # Tiebreaker analysis: when correct IS in the pair
    if best_pair:
        word, indices = best_pair
        opt_a = opts[indices[0]][0]
        opt_b = opts[indices[1]][0]
        len_a = len(opt_a.split())
        len_b = len(opt_b.split())
        correct_is = indices[0] if opts[indices[0]][1] else indices[1]
        wrong_is = indices[1] if correct_is == indices[0] else indices[0]
        
        correct_len = len(opts[correct_is][0].split())
        wrong_len = len(opts[wrong_is][0].split())
        
        if correct_len > wrong_len:
            longer_wins += 1
        elif correct_len < wrong_len:
            shorter_wins += 1
        else:
            same_len += 1
        
        pair_details.append({
            'qid': q['id'],
            'word': word,
            'correct_opt': opts[correct_is][0][:50],
            'wrong_opt': opts[wrong_is][0][:50],
            'correct_longer': correct_len > wrong_len,
        })

print("=" * 70)
print("📊 تحليل نمط الكلمة المكررة في خيارين")
print("=" * 70)

print(f"\n📈 الأسئلة اللي فيها كلمة مكررة بخيارين: {total_questions_with_pairs}/180")
print(f"✅ الجواب الصح كان أحد الخيارين: {correct_in_pair}/{total_questions_with_pairs} = {correct_in_pair*100//total_questions_with_pairs}%")
print(f"❌ الجواب الصح ما كان بالخيارين: {correct_not_in_pair}/{total_questions_with_pairs} = {correct_not_in_pair*100//total_questions_with_pairs}%")

print(f"\n--- الترجيح بين الخيارين ---")
print(f"📏 الأطول فاز: {longer_wins}/{correct_in_pair} = {longer_wins*100//correct_in_pair if correct_in_pair else 0}%")
print(f"📐 الأقصر فاز: {shorter_wins}/{correct_in_pair} = {shorter_wins*100//correct_in_pair if correct_in_pair else 0}%")
print(f"🤝 نفس الطول: {same_len}/{correct_in_pair}")

# Now check if this helps with the 68 unsolvable questions
UNSOLVABLE = {2,4,10,11,13,14,16,21,27,30,32,34,36,39,42,43,44,46,48,49,50,51,54,55,56,58,59,61,62,63,64,66,68,74,84,88,90,95,96,97,101,103,105,106,107,110,111,116,117,123,124,126,127,128,132,133,135,140,141,147,148,150,155,157,162,169,174,176}

print(f"\n--- التأثير على الـ 68 سؤال اللي الخوارزمية ما حلتها ---")
helped = 0
for d in pair_details:
    if d['qid'] in UNSOLVABLE:
        helped += 1
        print(f"  Q{d['qid']}: كلمة \"{d['word']}\" → {'الأطول صح' if d['correct_longer'] else 'الأقصر صح'}")
        print(f"    ✅ {d['correct_opt']}")
        print(f"    ❌ {d['wrong_opt']}")

print(f"\n  عدد الأسئلة اللي ممكن نحلها: {helped}/{len(UNSOLVABLE)}")

# Check which unsolvable questions DON'T have any pair pattern
print(f"\n--- الأسئلة اللي ما فيها نمط التكرار ---")
paired_qids = {d['qid'] for d in pair_details}
no_pair = UNSOLVABLE - paired_qids
for qid in sorted(no_pair):
    q = [q for q in questions if q['id'] == qid][0]
    correct_text = clean([o["text"] for o in q["options"] if o["correct"]][0])
    print(f"  Q{qid}: {q['text'][:50]}... → {correct_text[:40]}")
