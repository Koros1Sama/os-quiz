import json
import re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

golden_tier1 = ['circular', 'unauthorized', 'wait', 'pages', 'switching', 'than', 'create', 'web', 'allows', 'among']
golden_tier2 = ['ready', 'compiling', 'part', 'executing']
golden_tier3 = ['all', 'data', 'scheduler', 'more', 'about', 'stores', 'ntfs', 'collection', 'response', 'physical', 'hard', 'share', 'accounting', 'metadata', 'managing']
all_golden = golden_tier1 + golden_tier2 + golden_tier3

lines = []
def out(s=""):
    lines.append(s)

# ============================================================
# Q1: NOT questions - do ALL golden keywords fail?
# ============================================================
out("=" * 70)
out("ANALYSIS 1: Golden keywords in NOT questions")
out("=" * 70)

not_questions = [q for q in questions if " not " in q["text"].lower() or "NOT" in q["text"]]
out(f"Total NOT questions: {len(not_questions)}")

kw_correct_in_not = 0
kw_wrong_in_not = 0
kw_neutral_in_not = 0

for q in not_questions:
    correct_opt = None
    for opt in q["options"]:
        if opt["correct"]:
            correct_opt = clean(opt["text"])
    
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        words = set(text.split())
        has_golden = [gk for gk in all_golden if gk in words]
        
        if has_golden:
            if opt["correct"]:
                kw_correct_in_not += 1
                out(f"  Q{q['id']}: KEYWORD CORRECT in NOT! Keywords={has_golden} -> '{clean(opt['text'])[:50]}'")
            else:
                kw_wrong_in_not += 1

out(f"\nIn NOT questions: golden keywords correct={kw_correct_in_not}, wrong={kw_wrong_in_not}")
out(f"GOLDEN KEYWORDS WRONG IN NOT: {kw_wrong_in_not}/{kw_correct_in_not+kw_wrong_in_not} = {kw_wrong_in_not/(kw_correct_in_not+kw_wrong_in_not)*100:.0f}%")

# Check tier by tier
for tier_name, tier_words in [("Tier1", golden_tier1), ("Tier2", golden_tier2), ("Tier3", golden_tier3)]:
    c = 0
    w = 0
    for q in not_questions:
        for opt in q["options"]:
            text = clean(opt["text"]).lower()
            words = set(text.split())
            has = [gk for gk in tier_words if gk in words]
            if has:
                if opt["correct"]:
                    c += 1
                else:
                    w += 1
    total = c + w
    if total > 0:
        out(f"  {tier_name}: correct={c}, wrong={w} ({w/total*100:.0f}% wrong)")

# ============================================================
# Q2: LONGEST vs KEYWORDS - who wins when they conflict?
# ============================================================
out("\n" + "=" * 70)
out("ANALYSIS 2: LONGEST option vs GOLDEN KEYWORDS - conflicts")
out("=" * 70)

longest_wins = 0
kw_wins = 0
both_agree = 0
neither = 0

longest_beats_kw_qs = []
kw_beats_longest_qs = []

for q in questions:
    opts = [(clean(opt["text"]), opt["correct"], i) for i, opt in enumerate(q["options"])]
    
    # Find longest option
    longest_idx = max(range(len(opts)), key=lambda i: len(opts[i][0].split()))
    longest_correct = opts[longest_idx][1]
    
    # Find option with highest-tier golden keyword
    best_kw_idx = None
    best_tier = 99
    for i, (text, correct, idx) in enumerate(opts):
        words = set(text.lower().split())
        for gk in golden_tier1:
            if gk in words:
                # Check if ONLY this option has it
                other_has = any(gk in set(clean(q["options"][j]["text"]).lower().split()) for j in range(len(q["options"])) if j != i)
                if not other_has and best_tier > 1:
                    best_kw_idx = i
                    best_tier = 1
        if best_tier > 2:
            for gk in golden_tier2:
                if gk in words:
                    other_has = any(gk in set(clean(q["options"][j]["text"]).lower().split()) for j in range(len(q["options"])) if j != i)
                    if not other_has and best_tier > 2:
                        best_kw_idx = i
                        best_tier = 2
        if best_tier > 3:
            for gk in golden_tier3:
                if gk in words:
                    other_has = any(gk in set(clean(q["options"][j]["text"]).lower().split()) for j in range(len(q["options"])) if j != i)
                    if not other_has and best_tier > 3:
                        best_kw_idx = i
                        best_tier = 3
    
    if best_kw_idx is None:
        continue
    
    kw_correct = opts[best_kw_idx][1]
    
    if longest_idx == best_kw_idx:
        both_agree += 1
    elif kw_correct and not longest_correct:
        kw_wins += 1
        kw_beats_longest_qs.append(q["id"])
    elif longest_correct and not kw_correct:
        longest_wins += 1
        longest_beats_kw_qs.append(q["id"])
    else:
        neither += 1

out(f"Both agree (same option): {both_agree}")
out(f"KEYWORD wins over LONGEST: {kw_wins} at Q{kw_beats_longest_qs}")
out(f"LONGEST wins over KEYWORD: {longest_wins} at Q{longest_beats_kw_qs}")
out(f"Neither correct: {neither}")

# Check by tier
for tier_name, tier_words in [("Tier1", golden_tier1), ("Tier2", golden_tier2), ("Tier3", golden_tier3)]:
    tw = 0
    lw = 0
    for q in questions:
        opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
        longest_idx = max(range(len(opts)), key=lambda i: len(opts[i][0].split()))
        
        for i, (text, correct) in enumerate(opts):
            words = set(text.lower().split())
            has = [gk for gk in tier_words if gk in words]
            if has:
                other_has = False
                for j in range(len(opts)):
                    if j != i:
                        ow = set(opts[j][0].lower().split())
                        if any(gk in ow for gk in has):
                            other_has = True
                            break
                if not other_has and i != longest_idx:
                    if correct:
                        tw += 1
                    elif opts[longest_idx][1]:
                        lw += 1
    if tw + lw > 0:
        out(f"  {tier_name} vs Longest: {tier_name} wins {tw}x, Longest wins {lw}x")

# ============================================================
# Q3: Q117 specifically - why data lost
# ============================================================
out("\n" + "=" * 70)
out("ANALYSIS 3: Q117 - Why 'data' lost")
out("=" * 70)

q117 = [q for q in questions if q["id"] == 117][0]
out(f"Q: {q117['text']}")
for opt in q117["options"]:
    text = clean(opt["text"])
    words = set(text.lower().split())
    golden_found = [gk for gk in all_golden if gk in words]
    status = "CORRECT" if opt["correct"] else "WRONG"
    is_longest = len(text.split()) == max(len(clean(o["text"]).split()) for o in q117["options"])
    out(f"  {status}: '{text}' | golden={golden_found} | longest={is_longest}")

# ============================================================
# Q4: Simulate full algorithm with priority rules
# ============================================================
out("\n" + "=" * 70)
out("SIMULATION: Full algorithm accuracy with priority rules")
out("=" * 70)

def apply_algorithm(q):
    """Returns (predicted_correct, rule_used)"""
    opts = [(clean(opt["text"]), opt["correct"]) for opt in q["options"]]
    is_not = " not " in q["text"].lower() or "NOT" in q["text"]
    
    # Rule 1: All of the mentioned/above
    for i, (text, correct) in enumerate(opts):
        if any(p in text.lower() for p in ["all of the mentioned", "all of the above", "all above", "all of above"]):
            return correct, "ALL_OF"
    
    # Rule 2: Eliminate None of
    remaining = [(i, t, c) for i, (t, c) in enumerate(opts) if "none of the" not in t.lower() and "none of above" not in t.lower()]
    if len(remaining) < len(opts):
        if len(remaining) == 1:
            return remaining[0][2], "NONE_ELIM"
    
    # Rule 3: Eliminate Schedules
    remaining2 = [(i, t, c) for i, t, c in remaining if not t.startswith("Schedules")]
    if len(remaining2) < len(remaining) and len(remaining2) >= 1:
        remaining = remaining2
    
    # Rule 4: Trap words elimination
    trap_words = ['single', 'allocates', 'prevention', 'segmentation', 'deadlocks', 'speed', 'manager']
    remaining3 = []
    for i, t, c in remaining:
        words = set(t.lower().split())
        if not any(tw in words for tw in trap_words) and 'macos' not in t.lower():
            remaining3.append((i, t, c))
    if remaining3 and len(remaining3) < len(remaining):
        remaining = remaining3
    
    # Rule 5: Scheduling avoidance (unless NOT question or question about scheduling itself)
    if not is_not:
        q_about_scheduling = any(w in q["text"].lower() for w in ["which scheduling", "what scheduling", "name the scheduling", "which type of scheduling"])
        if not q_about_scheduling:
            remaining4 = [(i, t, c) for i, t, c in remaining if 'scheduling' not in t.lower()]
            if remaining4 and len(remaining4) < len(remaining):
                remaining = remaining4
    
    # In NOT questions, skip golden keywords entirely
    if not is_not:
        # Rule 6: Tier 1 golden keywords
        for gk in golden_tier1:
            kw_opts = [(i, t, c) for i, t, c in remaining if gk in set(t.lower().split())]
            if len(kw_opts) == 1:
                return kw_opts[0][2], f"TIER1:{gk}"
        
        # Rule 7: Tier 2 golden keywords
        for gk in golden_tier2:
            kw_opts = [(i, t, c) for i, t, c in remaining if gk in set(t.lower().split())]
            if len(kw_opts) == 1:
                return kw_opts[0][2], f"TIER2:{gk}"
    
    # Rule 8: Parentheses
    paren_opts = [(i, t, c) for i, t, c in remaining if "(" in t and ")" in t]
    non_paren = [(i, t, c) for i, t, c in remaining if "(" not in t]
    if paren_opts and non_paren:
        # Pick longest paren option
        best = max(paren_opts, key=lambda x: len(x[1].split()))
        return best[2], "PARENS"
    
    # Rule 9: Longest option
    if remaining:
        best = max(remaining, key=lambda x: len(x[1].split()))
        return best[2], "LONGEST"
    
    return opts[0][1], "FALLBACK"

correct_count = 0
wrong_qs = []
rule_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})

for q in questions:
    result, rule = apply_algorithm(q)
    rule_stats[rule]["correct" if result else "wrong"] += 1
    if result:
        correct_count += 1
    else:
        wrong_qs.append((q["id"], rule))

out(f"\nTotal correct: {correct_count}/180 = {correct_count/180*100:.1f}%")
out(f"Wrong: {len(wrong_qs)}")
out(f"\nWrong questions:")
for qid, rule in wrong_qs:
    q = [q for q in questions if q["id"] == qid][0]
    correct = clean([o for o in q["options"] if o["correct"]][0]["text"])
    out(f"  Q{qid} (rule: {rule}): correct='{correct[:50]}'")

out(f"\nRule breakdown:")
for rule, stats in sorted(rule_stats.items(), key=lambda x: -(x[1]["correct"]+x[1]["wrong"])):
    total = stats["correct"] + stats["wrong"]
    pct = stats["correct"] / total * 100
    out(f"  {rule}: {stats['correct']}/{total} = {pct:.0f}%")

with open("priority_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done! Results in priority_analysis.txt")
