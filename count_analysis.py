import json, re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','when','between','if','all','none',
              'true','false','above','mentioned','these','both','more','most'}

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# For each keyword, track accuracy when it appears in EXACTLY 2 vs 3+ options
# word -> { 2: {correct, total, questions}, 3: {correct, total, questions}, 4: ... }
word_by_count = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0, 'questions': []}))

for q in questions:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    correct_idx = next(i for i, (t, c) in enumerate(opts) if c)
    
    # Count word frequency across options
    word_to_opts = {}
    for i, (text, _) in enumerate(opts):
        words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        for w in words:
            if w in STOP_WORDS or len(w) <= 2:
                continue
            if w not in word_to_opts:
                word_to_opts[w] = []
            word_to_opts[w].append(i)
    
    for word, indices in word_to_opts.items():
        count = len(indices)
        if count < 2: continue  # skip unique words
        
        stats = word_by_count[word][count]
        stats['total'] += 1
        correct_in = correct_idx in indices
        if correct_in:
            stats['correct'] += 1
            stats['questions'].append(f"Q{q['id']}✅")
        else:
            stats['questions'].append(f"Q{q['id']}❌")

# Show results for interesting words
FOCUS_WORDS = ['cpu', 'file', 'threads', 'memory', 'management', 'first', 'scheduling',
               'time', 'user', 'process', 'kernel', 'program', 'data', 'page', 'thread',
               'resource', 'execution', 'virtual', 'disk', 'hardware', 'software']

print("=" * 70)
print("📊 تحليل: هل عدد التكرارات يأثر؟ (2 vs 3 vs 4)")
print("=" * 70)

for word in FOCUS_WORDS:
    if word not in word_by_count:
        continue
    counts = word_by_count[word]
    if not counts:
        continue
    
    print(f"\n🔑 \"{word}\":")
    for n in sorted(counts.keys()):
        stats = counts[n]
        if stats['total'] == 0: continue
        pct = stats['correct'] * 100 // stats['total']
        emoji = "🟢" if pct >= 75 else ("🟡" if pct >= 50 else "🔴")
        # For n options containing word, chance of random = n/4
        random_pct = n * 100 // 4
        better = "أفضل من عشوائي" if pct > random_pct else "أسوأ من عشوائي!"
        print(f"  بـ {n} خيارات: {emoji} {stats['correct']}/{stats['total']} = {pct}% ({better}, عشوائي={random_pct}%)")
        if stats['total'] <= 6:
            print(f"    {', '.join(stats['questions'])}")

# Summary table
print(f"\n{'='*70}")
print("📊 ملخص: الكلمات اللي تكررت بـ 2 خيار (أحسن فلتر)")
print(f"{'='*70}")
print(f"{'كلمة':<15} {'بـ 2':<20} {'بـ 3+':<20} {'الحكم'}")
print("-" * 70)

for word in sorted(word_by_count.keys()):
    counts = word_by_count[word]
    if 2 not in counts or counts[2]['total'] < 2:
        continue
    
    s2 = counts[2]
    pct2 = s2['correct'] * 100 // s2['total']
    
    s3_total = sum(counts[n]['total'] for n in counts if n >= 3)
    s3_correct = sum(counts[n]['correct'] for n in counts if n >= 3)
    
    if s3_total > 0:
        pct3 = s3_correct * 100 // s3_total
        col3 = f"{s3_correct}/{s3_total} = {pct3}%"
    else:
        col3 = "—"
    
    if pct2 >= 80:
        verdict = "✅ بـ2 = ذهبي!"
    elif pct2 >= 60:
        verdict = "🟡 بـ2 = متوسط"
    else:
        verdict = "🔴 بـ2 = ضعيف"
    
    print(f"  {word:<13} {s2['correct']}/{s2['total']} = {pct2}%{'':<10} {col3:<18} {verdict}")
