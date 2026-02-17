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

# ============================================================
# 1. ECHO in NOT questions
# ============================================================
print("=" * 70)
print("1. ECHO in NOT questions")
print("=" * 70)

not_questions = [q for q in questions if re.search(r'\bnot\b', q['text'], re.IGNORECASE) and len(q["options"]) > 2]

echo_not_correct = 0
echo_not_wrong = 0
echo_not_tie = 0

for q in not_questions:
    q_words = get_words(q["text"]) - STOP_WORDS
    
    scores = []
    for opt in q["options"]:
        text = clean(opt["text"])
        opt_words = get_words(text)
        shared = q_words & opt_words
        scores.append((len(shared), opt["correct"], text))
    
    max_score = max(s[0] for s in scores)
    if max_score == 0:
        continue
    
    winners = [s for s in scores if s[0] == max_score]
    
    if len(winners) == 1:
        status = "✅" if winners[0][1] else "❌"
        echo_not_correct += 1 if winners[0][1] else 0
        echo_not_wrong += 0 if winners[0][1] else 1
        print(f"  Q{q['id']}: {status} echo='{winners[0][2][:50]}' | Q: '{q['text'][:50]}'")
    else:
        echo_not_tie += 1
        print(f"  Q{q['id']}: 🔄 tie ({len(winners)} options with {max_score} shared words)")

total = echo_not_correct + echo_not_wrong
if total > 0:
    print(f"\nEcho in NOT: correct={echo_not_correct}, wrong={echo_not_wrong}, tie={echo_not_tie}")
    print(f"Accuracy: {echo_not_correct}/{total} = {echo_not_correct*100//total}%")
else:
    print(f"\nNo single-winner echo in NOT questions. Ties={echo_not_tie}")

# ============================================================
# 2. Questions that HAVE a "None" option — analysis
# ============================================================
print("\n" + "=" * 70)
print("2. Questions with 'None' options — how do other rules work?")
print("=" * 70)

none_questions = []
for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bnone\b', text, re.IGNORECASE) and len(q["options"]) > 2:
            none_questions.append(q)
            break

print(f"\nTotal questions with 'None' option: {len(none_questions)}")

# 2a. Echo in None questions
echo_none_correct = 0
echo_none_wrong = 0
echo_none_tie = 0

for q in none_questions:
    q_words = get_words(q["text"]) - STOP_WORDS
    is_not = bool(re.search(r'\bnot\b', q['text'], re.IGNORECASE))
    
    scores = []
    for opt in q["options"]:
        text = clean(opt["text"])
        opt_words = get_words(text)
        shared = q_words & opt_words
        scores.append((len(shared), opt["correct"], text))
    
    max_score = max(s[0] for s in scores)
    if max_score == 0:
        continue
    
    winners = [s for s in scores if s[0] == max_score]
    
    if len(winners) == 1:
        if winners[0][1]:
            echo_none_correct += 1
        else:
            echo_none_wrong += 1
    else:
        echo_none_tie += 1

total = echo_none_correct + echo_none_wrong
if total > 0:
    print(f"\n2a. Echo in None-questions: correct={echo_none_correct}, wrong={echo_none_wrong}, tie={echo_none_tie}")
    print(f"    Accuracy: {echo_none_correct}/{total} = {echo_none_correct*100//total}%")

# 2b. Longest in None questions (excluding None itself as longest)
longest_none_correct = 0
longest_none_wrong = 0

for q in none_questions:
    is_not = bool(re.search(r'\bnot\b', q['text'], re.IGNORECASE))
    
    # Get longest option (excluding None options)
    non_none_opts = []
    for opt in q["options"]:
        text = clean(opt["text"])
        if not re.search(r'\bnone\b', text, re.IGNORECASE):
            non_none_opts.append((len(text.split()), opt["correct"], text))
    
    if not non_none_opts:
        continue
    
    max_len = max(s[0] for s in non_none_opts)
    longest = [s for s in non_none_opts if s[0] == max_len]
    
    if len(longest) == 1:
        if longest[0][1]:
            longest_none_correct += 1
        else:
            longest_none_wrong += 1

total = longest_none_correct + longest_none_wrong
if total > 0:
    print(f"\n2b. Longest in None-questions (excl None): correct={longest_none_correct}, wrong={longest_none_wrong}")
    print(f"    Accuracy: {longest_none_correct}/{total} = {longest_none_correct*100//total}%")

# 2c. Is None ever correct?
none_correct = 0
none_total = 0
for q in none_questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bnone\b', text, re.IGNORECASE):
            none_total += 1
            if opt["correct"]:
                none_correct += 1
                print(f"    ⚠️ None CORRECT at Q{q['id']}: '{text}'")

print(f"\n2c. None option correct: {none_correct}/{none_total}")

# 2d. None + NOT combination
print(f"\n2d. Questions with BOTH None AND NOT:")
none_and_not = 0
for q in none_questions:
    is_not = bool(re.search(r'\bnot\b', q['text'], re.IGNORECASE))
    if is_not:
        none_and_not += 1
        correct_txt = [clean(o["text"]) for o in q["options"] if o["correct"]][0]
        # Is longest the correct?
        non_none = [(len(clean(o["text"]).split()), clean(o["text"]), o["correct"]) for o in q["options"] if not re.search(r'\bnone\b', clean(o["text"]), re.IGNORECASE)]
        max_l = max(x[0] for x in non_none)
        longest_opt = [x for x in non_none if x[0] == max_l]
        longest_is_correct = longest_opt[0][2] if len(longest_opt)==1 else "tie"
        print(f"  Q{q['id']}: correct='{correct_txt[:50]}' | longest_correct={longest_is_correct}")

print(f"\n  Total None+NOT: {none_and_not}")

# ============================================================
# 3. Does having None affect Longest accuracy?
# ============================================================
print("\n" + "=" * 70)
print("3. Longest accuracy: WITH None option vs WITHOUT")
print("=" * 70)

none_ids = set(q['id'] for q in none_questions)

longest_with_none_c = 0
longest_with_none_w = 0
longest_no_none_c = 0
longest_no_none_w = 0

for q in questions:
    if len(q["options"]) <= 2:
        continue
    
    opts = [(len(clean(o["text"]).split()), o["correct"], clean(o["text"])) for o in q["options"]]
    max_l = max(x[0] for x in opts)
    longest = [x for x in opts if x[0] == max_l]
    
    if len(longest) != 1:
        continue
    
    if q['id'] in none_ids:
        if longest[0][1]:
            longest_with_none_c += 1
        else:
            longest_with_none_w += 1
    else:
        if longest[0][1]:
            longest_no_none_c += 1
        else:
            longest_no_none_w += 1

t1 = longest_with_none_c + longest_with_none_w
t2 = longest_no_none_c + longest_no_none_w
print(f"WITH None: {longest_with_none_c}/{t1} = {longest_with_none_c*100//t1 if t1 else 0}%")
print(f"WITHOUT None: {longest_no_none_c}/{t2} = {longest_no_none_c*100//t2 if t2 else 0}%")
