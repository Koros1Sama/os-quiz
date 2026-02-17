import json
import re
from collections import defaultdict, Counter

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

lines = []
def out(s=""):
    lines.append(s)

# ============================================================
# IDEA 1: Words that appear in options but are ALMOST ALWAYS WRONG
# "Trap words" - if you see them, skip that option
# ============================================================
out("=" * 70)
out("TRAP WORDS: Words in options that are almost always WRONG")
out("=" * 70)

# For each word, count: how many times it appears in an option, and how many of those are correct
word_in_options = defaultdict(lambda: {"correct": 0, "wrong": 0, "correct_qids": [], "wrong_qids": []})

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        words = set(re.findall(r'[a-zA-Z]{3,}', text))
        # Also check multi-word phrases
        for w in words:
            if opt["correct"]:
                word_in_options[w]["correct"] += 1
                word_in_options[w]["correct_qids"].append(q["id"])
            else:
                word_in_options[w]["wrong"] += 1
                word_in_options[w]["wrong_qids"].append(q["id"])

out("\nWords that are WRONG >=80% of the time (appears in >=5 options):")
trap_words = []
for word, stats in word_in_options.items():
    total = stats["correct"] + stats["wrong"]
    if total >= 5:
        wrong_pct = stats["wrong"] / total * 100
        if wrong_pct >= 80:
            trap_words.append((word, stats["correct"], stats["wrong"], total, wrong_pct, stats["correct_qids"]))

trap_words.sort(key=lambda x: (-x[4], -x[3]))
for word, correct, wrong, total, pct, correct_qids in trap_words:
    exc = f" EXCEPTIONS at Q{correct_qids}" if correct_qids else ""
    out(f"  '{word}': WRONG {wrong}/{total} = {pct:.0f}%{exc}")

# ============================================================
# IDEA 1b: Specifically check "Scheduling" in options
# ============================================================
out("\n" + "=" * 70)
out("DETAILED: 'Scheduling' in option text")
out("=" * 70)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if "scheduling" in text.lower():
            is_not_q = " not " in q["text"].lower() or "NOT" in q["text"]
            status = "CORRECT" if opt["correct"] else "WRONG"
            not_flag = " [NOT question]" if is_not_q else ""
            out(f"  Q{q['id']}: '{text}' -> {status}{not_flag}")

# ============================================================
# IDEA 2: Options with PARENTHESES - is the answer always one of them?
# ============================================================
out("\n" + "=" * 70)
out("PARENTHESES PATTERN: When options have (), is answer always one?")
out("=" * 70)

paren_correct = 0
paren_wrong = 0
paren_qs = 0

for q in questions:
    opts_with_parens = []
    opts_without_parens = []
    correct_has_parens = False
    
    for opt in q["options"]:
        text = clean(opt["text"])
        if "(" in text and ")" in text:
            opts_with_parens.append((text, opt["correct"]))
            if opt["correct"]:
                correct_has_parens = True
        else:
            opts_without_parens.append((text, opt["correct"]))
    
    # Only analyze questions where SOME but NOT ALL options have parens
    if opts_with_parens and opts_without_parens:
        paren_qs += 1
        if correct_has_parens:
            paren_correct += 1
        else:
            paren_wrong += 1
            out(f"  EXCEPTION Q{q['id']}: Correct answer WITHOUT parens: '{clean([o for o in q['options'] if o['correct']][0]['text'])}'")
            out(f"    Options with parens: {[t for t,c in opts_with_parens]}")

out(f"\n  Questions with mixed parens: {paren_qs}")
out(f"  Answer HAS parens: {paren_correct}/{paren_qs} = {paren_correct/max(paren_qs,1)*100:.1f}%")
out(f"  Answer NO parens: {paren_wrong}/{paren_qs} = {paren_wrong/max(paren_qs,1)*100:.1f}%")

# ============================================================
# IDEA 3: Similar to "Scheduling", find other words that ALWAYS 
# indicate wrong answer EXCEPT in NOT questions
# ============================================================
out("\n" + "=" * 70)
out("WORDS THAT ARE WRONG NORMALLY BUT CORRECT IN 'NOT' QUESTIONS")
out("=" * 70)

for word, stats in word_in_options.items():
    total = stats["correct"] + stats["wrong"]
    if total >= 4 and stats["wrong"] / total >= 0.75:
        # Check if the correct cases are all NOT questions
        correct_in_not = 0
        correct_not_not = 0
        for qid in stats["correct_qids"]:
            q = [q for q in questions if q["id"] == qid][0]
            if " not " in q["text"].lower() or "NOT" in q["text"]:
                correct_in_not += 1
            else:
                correct_not_not += 1
        
        if correct_in_not > 0 and correct_not_not == 0 and stats["correct"] <= 3:
            out(f"  '{word}': wrong {stats['wrong']}x, correct ONLY in NOT questions ({correct_in_not}x) -> Q{stats['correct_qids']}")

# ============================================================
# IDEA 4: Capitalization patterns (proper nouns vs generic)
# ============================================================
out("\n" + "=" * 70)
out("CAPITALIZATION: Options that start with UPPERCASE proper noun")
out("=" * 70)

# Check if options that are proper nouns (capitalized single/two words) behave differently
proper_noun_correct = 0
proper_noun_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        # Check if it's a short capitalized term (likely a proper noun/name)
        words = text.split()
        if 1 <= len(words) <= 3 and all(w[0].isupper() for w in words if w[0].isalpha()):
            if opt["correct"]:
                proper_noun_correct += 1
            else:
                proper_noun_wrong += 1

out(f"  Short capitalized options: correct={proper_noun_correct}, wrong={proper_noun_wrong}")
out(f"  Accuracy: {proper_noun_correct/(proper_noun_correct+proper_noun_wrong)*100:.1f}%")

# ============================================================
# IDEA 5: Options containing numbers or specific values
# ============================================================
out("\n" + "=" * 70)
out("OPTIONS WITH NUMBERS/VERSIONS")
out("=" * 70)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\d', text):
            status = "CORRECT" if opt["correct"] else "WRONG"
            out(f"  Q{q['id']}: '{text}' -> {status}")

# ============================================================
# IDEA 6: Options that ECHO words from the question
# ============================================================
out("\n" + "=" * 70)
out("ECHO PATTERN: Option that repeats the most words from the question")
out("=" * 70)

echo_correct = 0
echo_total = 0

stop = {'a','an','the','of','in','to','and','is','for','by','it','that','or','on',
        'with','as','be','at','from','not','are','its','has','can','does','do',
        'which','what','following','used','one'}

for q in questions:
    q_words = set(re.findall(r'[a-z]{3,}', q["text"].lower())) - stop
    if len(q_words) < 2:
        continue
    
    best_echo = -1
    best_idx = 0
    for i, opt in enumerate(q["options"]):
        text = clean(opt["text"]).lower()
        opt_words = set(re.findall(r'[a-z]{3,}', text))
        echo = len(q_words & opt_words)
        if echo > best_echo:
            best_echo = echo
            best_idx = i
    
    if best_echo >= 2:
        echo_total += 1
        if q["options"][best_idx]["correct"]:
            echo_correct += 1

out(f"  Option with most question-word echoes (>=2): {echo_correct}/{echo_total} = {echo_correct/max(echo_total,1)*100:.1f}%")

with open("pattern_verification.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done! Results in pattern_verification.txt")
