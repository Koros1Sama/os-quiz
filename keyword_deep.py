import json
import re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# Golden keywords from original analysis
golden_words = [
    'all', 'data', 'above', 'wait', 'ready', 'managing', 'pages', 'multiple',
    'metadata', 'about', 'create', 'web', 'devices', 'scheduler', 'than',
    'circular', 'unauthorized', 'more', 'switching', 'stores', 'ntfs',
    'among', 'collection', 'compiling', 'response', 'allows', 'physical',
    'hard', 'transfer', 'part', 'share', 'executing', 'accounting'
]

lines = []
def out(s=""):
    lines.append(s)

out("DEEP KEYWORD ANALYSIS - Finding patterns in exceptions")
out("=" * 70)

# For each golden keyword:
# - List all questions where it appears in ANY option
# - Show when it's correct vs wrong
# - Analyze the wrong cases: is there a pattern?

keyword_data = {}

for kw in golden_words:
    correct_qs = []
    wrong_qs = []
    
    for q in questions:
        # Check all options for this keyword
        opts_with_kw = []
        correct_opt = None
        
        for opt in q["options"]:
            text = clean(opt["text"])
            if kw in text.lower().split():  # exact word match
                opts_with_kw.append((text, opt["correct"]))
            if opt["correct"]:
                correct_opt = text
        
        if not opts_with_kw:
            continue
        
        # Is correct answer among options with this keyword?
        correct_has_kw = any(c for _, c in opts_with_kw)
        is_not_q = " not " in q["text"].lower() or "NOT" in q["text"]
        
        entry = {
            "id": q["id"],
            "q_text": q["text"][:70],
            "correct_answer": correct_opt[:60] if correct_opt else "?",
            "is_not": is_not_q,
            "opts_with_kw": [(t[:50], c) for t, c in opts_with_kw],
            "num_opts_with_kw": len(opts_with_kw),
        }
        
        if correct_has_kw:
            correct_qs.append(entry)
        else:
            wrong_qs.append(entry)
    
    total = len(correct_qs) + len(wrong_qs)
    if total < 2:
        continue
    
    correct_rate = len(correct_qs) / total * 100
    
    keyword_data[kw] = {
        "correct": correct_qs,
        "wrong": wrong_qs,
        "total": total,
        "rate": correct_rate
    }

# Sort by accuracy descending
sorted_keywords = sorted(keyword_data.items(), key=lambda x: (-x[1]["rate"], -x[1]["total"]))

for kw, data in sorted_keywords:
    out(f"\n{'='*70}")
    out(f"KEYWORD: '{kw}' - {len(data['correct'])}/{data['total']} correct ({data['rate']:.0f}%)")
    out(f"{'='*70}")
    
    out(f"  CORRECT in Q: {[e['id'] for e in data['correct']]}")
    
    if data['wrong']:
        out(f"  WRONG in Q: {[e['id'] for e in data['wrong']]}")
        out(f"  --- EXCEPTION ANALYSIS ---")
        for e in data['wrong']:
            not_flag = " [NOT Q]" if e['is_not'] else ""
            out(f"    Q{e['id']}{not_flag}: Correct was: '{e['correct_answer']}'")
            out(f"      Options with '{kw}': {[(t, 'C' if c else 'W') for t, c in e['opts_with_kw']]}")
            
            # Check patterns
            patterns = []
            if e['is_not']:
                patterns.append("NOT_QUESTION")
            if e['num_opts_with_kw'] > 1:
                patterns.append(f"MULTI_OPTS({e['num_opts_with_kw']})")
            
            # Check if another golden keyword is in the correct answer
            correct_words = set(e['correct_answer'].lower().split())
            competing_kws = [gk for gk in golden_words if gk in correct_words and gk != kw]
            if competing_kws:
                patterns.append(f"COMPETING_KW: {competing_kws}")
            
            if patterns:
                out(f"      Patterns: {', '.join(patterns)}")
    else:
        out(f"  NO EXCEPTIONS - 100% accurate!")

# ============================================================
# PRIORITY CHAIN ANALYSIS
# When two golden keywords compete, which one wins?
# ============================================================
out(f"\n\n{'='*70}")
out("KEYWORD CONFLICTS - When 2 golden keywords are in different options")
out("=" * 70)

conflicts = defaultdict(lambda: {"wins": 0, "loses": 0, "qs": []})

for q in questions:
    # Map each option to its golden keywords
    opt_kws = []
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        words = set(text.split())
        kws = [gk for gk in golden_words if gk in words]
        opt_kws.append((kws, opt["correct"], clean(opt["text"])[:50]))
    
    # Find conflicts: correct option has kw_A, wrong option has kw_B
    correct_kws = set()
    wrong_kws = set()
    for kws, is_correct, txt in opt_kws:
        if is_correct:
            correct_kws.update(kws)
        else:
            wrong_kws.update(kws)
    
    # Keywords that appear in BOTH correct and wrong don't help
    conflicting_wrong = wrong_kws - correct_kws
    unique_correct = correct_kws - wrong_kws
    
    if conflicting_wrong and unique_correct:
        for wk in conflicting_wrong:
            for ck in unique_correct:
                conflicts[(ck, wk)]["wins"] += 1
                conflicts[(ck, wk)]["qs"].append(q["id"])

out("\nWinner beats Loser in these questions:")
for (winner, loser), stats in sorted(conflicts.items(), key=lambda x: -x[1]["wins"]):
    if stats["wins"] >= 2:
        out(f"  '{winner}' BEATS '{loser}': {stats['wins']}x at Q{stats['qs']}")

# ============================================================
# SINGLE-OPTION RULE: keyword appears in EXACTLY 1 option
# ============================================================
out(f"\n\n{'='*70}")
out("SINGLE-OPTION: Keyword in exactly 1 option (most reliable)")
out("=" * 70)

for kw, data in sorted_keywords:
    single_correct = 0
    single_wrong = 0
    single_wrong_qs = []
    
    for e in data['correct']:
        if e['num_opts_with_kw'] == 1:
            single_correct += 1
    for e in data['wrong']:
        if e['num_opts_with_kw'] == 1:
            single_wrong += 1
            single_wrong_qs.append(e['id'])
    
    single_total = single_correct + single_wrong
    if single_total >= 2:
        pct = single_correct / single_total * 100
        exc = f" (wrong at Q{single_wrong_qs})" if single_wrong_qs else ""
        out(f"  '{kw}': {single_correct}/{single_total} = {pct:.0f}%{exc}")

with open("keyword_deep_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done! Results in keyword_deep_analysis.txt")
