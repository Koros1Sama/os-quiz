import json
import re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

lines = []
def out(s=""):
    lines.append(s)

# ============================================================
# 1. ALL "None" variants - are they ALL always wrong?
# ============================================================
out("=" * 70)
out("ALL 'NONE' VARIANTS IN OPTIONS")
out("=" * 70)

none_correct = 0
none_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        if text.startswith("none"):
            status = "CORRECT" if opt["correct"] else "WRONG"
            out(f"  Q{q['id']}: '{clean(opt['text'])}' -> {status}")
            if opt["correct"]:
                none_correct += 1
            else:
                none_wrong += 1

out(f"\nTotal None: correct={none_correct}, wrong={none_wrong}")
if none_correct + none_wrong > 0:
    out(f"None ALWAYS wrong: {none_wrong}/{none_correct+none_wrong} = {none_wrong/(none_correct+none_wrong)*100:.0f}%")

# ============================================================
# 2. NOT questions: is LONGEST correct or wrong?
# ============================================================
out("\n" + "=" * 70)
out("NOT QUESTIONS: Is the LONGEST option correct?")
out("=" * 70)

not_longest_correct = 0
not_longest_wrong = 0

for q in questions:
    is_not = " not " in q["text"].lower() or "NOT" in q["text"]
    if not is_not:
        continue
    
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    longest_idx = max(range(len(opts)), key=lambda i: len(opts[i][0].split()))
    
    if opts[longest_idx][1]:
        not_longest_correct += 1
    else:
        not_longest_wrong += 1
        correct = [t for t, c in opts if c][0]
        out(f"  Q{q['id']}: Longest WRONG. Correct='{correct[:50]}'")

out(f"\nIn NOT questions: Longest correct={not_longest_correct}/{not_longest_correct+not_longest_wrong}")
out(f"  = {not_longest_correct/(not_longest_correct+not_longest_wrong)*100:.0f}%")

# ============================================================
# 2b. NOT questions: is SHORTEST correct?
# ============================================================
out("\n" + "=" * 70)
out("NOT QUESTIONS: Is the SHORTEST option correct?")
out("=" * 70)

not_shortest_correct = 0
not_shortest_wrong = 0

for q in questions:
    is_not = " not " in q["text"].lower() or "NOT" in q["text"]
    if not is_not:
        continue
    
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    shortest_idx = min(range(len(opts)), key=lambda i: len(opts[i][0].split()))
    
    if opts[shortest_idx][1]:
        not_shortest_correct += 1
    else:
        not_shortest_wrong += 1

out(f"In NOT questions: Shortest correct={not_shortest_correct}/{not_shortest_correct+not_shortest_wrong}")
out(f"  = {not_shortest_correct/(not_shortest_correct+not_shortest_wrong)*100:.0f}%")

# ============================================================
# 3. LONGEST behavior: WITH keywords vs WITHOUT keywords
# ============================================================
out("\n" + "=" * 70)
out("LONGEST: When there ARE golden keywords vs when there AREN'T")
out("=" * 70)

golden_all = ['circular', 'unauthorized', 'wait', 'pages', 'switching', 'than', 'create', 'web', 
              'allows', 'among', 'ready', 'compiling', 'part', 'executing',
              'all', 'data', 'scheduler', 'more', 'about', 'stores', 'ntfs', 'collection', 
              'response', 'physical', 'hard', 'share', 'accounting', 'metadata', 'managing']

longest_with_kw_correct = 0
longest_with_kw_wrong = 0
longest_no_kw_correct = 0
longest_no_kw_wrong = 0

for q in questions:
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    longest_idx = max(range(len(opts)), key=lambda i: len(opts[i][0].split()))
    
    # Check if any option has a unique golden keyword
    has_unique_kw = False
    for gk in golden_all:
        kw_opts = [i for i in range(len(opts)) if gk in set(opts[i][0].lower().split())]
        if len(kw_opts) == 1:
            has_unique_kw = True
            break
    
    if has_unique_kw:
        if opts[longest_idx][1]:
            longest_with_kw_correct += 1
        else:
            longest_with_kw_wrong += 1
    else:
        if opts[longest_idx][1]:
            longest_no_kw_correct += 1
        else:
            longest_no_kw_wrong += 1

out(f"Longest WITH golden keyword present: {longest_with_kw_correct}/{longest_with_kw_correct+longest_with_kw_wrong} = {longest_with_kw_correct/(longest_with_kw_correct+longest_with_kw_wrong)*100:.0f}%")
out(f"Longest WITHOUT any golden keyword:  {longest_no_kw_correct}/{longest_no_kw_correct+longest_no_kw_wrong} = {longest_no_kw_correct/(longest_no_kw_correct+longest_no_kw_wrong)*100:.0f}%")

# ============================================================
# 4. LONGEST after removing None options - does accuracy improve?
# ============================================================
out("\n" + "=" * 70)
out("LONGEST after removing 'None' options")
out("=" * 70)

lc = 0
lw = 0
for q in questions:
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    # Remove none options
    filtered = [(t, c) for t, c in opts if not t.lower().startswith("none")]
    if not filtered:
        continue
    
    longest_idx = max(range(len(filtered)), key=lambda i: len(filtered[i][0].split()))
    if filtered[longest_idx][1]:
        lc += 1
    else:
        lw += 1

out(f"Longest (after None removal): {lc}/{lc+lw} = {lc/(lc+lw)*100:.1f}%")

# ============================================================
# 5. LONGEST after removing ALL trap words + None + Scheduling
# ============================================================
out("\n" + "=" * 70)
out("LONGEST after removing ALL traps (None + trap words + Scheduling)")
out("=" * 70)

trap_words = ['single', 'allocates', 'prevention', 'segmentation', 'deadlocks', 'speed', 'manager']

lc2 = 0
lw2 = 0
for q in questions:
    is_not = " not " in q["text"].lower() or "NOT" in q["text"]
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    
    # Remove none, trap words, scheduling (if not NOT question)
    filtered = []
    for t, c in opts:
        words = set(t.lower().split())
        if t.lower().startswith("none"):
            continue
        if any(tw in words for tw in trap_words) or 'macos' in t.lower():
            continue
        if not is_not and 'scheduling' in t.lower():
            continue
        if t.startswith("Schedules"):
            continue
        filtered.append((t, c))
    
    if not filtered:
        continue
    
    longest_idx = max(range(len(filtered)), key=lambda i: len(filtered[i][0].split()))
    if filtered[longest_idx][1]:
        lc2 += 1
    else:
        lw2 += 1

out(f"Longest (after ALL trap removal): {lc2}/{lc2+lw2} = {lc2/(lc2+lw2)*100:.1f}%")

# ============================================================
# 6. Full breakdown: NOT + longest + traps
# ============================================================
out("\n" + "=" * 70)
out("NOT questions breakdown with longest after trap removal")
out("=" * 70)

for q in questions:
    is_not = " not " in q["text"].lower() or "NOT" in q["text"]
    if not is_not:
        continue
    
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    
    # Remove traps
    filtered = []
    for t, c in opts:
        words = set(t.lower().split())
        if t.lower().startswith("none"):
            continue
        if any(tw in words for tw in trap_words) or 'macos' in t.lower():
            continue
        if t.startswith("Schedules"):
            continue
        filtered.append((t, c))
    
    if not filtered:
        continue
    
    longest_idx = max(range(len(filtered)), key=lambda i: len(filtered[i][0].split()))
    shortest_idx = min(range(len(filtered)), key=lambda i: len(filtered[i][0].split()))
    
    correct = [t for t, c in filtered if c]
    correct_t = correct[0] if correct else "?"
    
    out(f"  Q{q['id']}: Longest={'✅' if filtered[longest_idx][1] else '❌'} Shortest={'✅' if filtered[shortest_idx][1] else '❌'} Correct='{correct_t[:45]}'")

with open("longest_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done! Results in longest_analysis.txt")
