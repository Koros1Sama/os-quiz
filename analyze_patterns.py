import json
import re
from collections import Counter, defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

total = len(questions)
print(f"=== Total questions: {total} ===\n")

# ============================================================
# 1. Correct answer POSITION analysis (a/b/c/d or index 0,1,2,3)
# ============================================================
pos_counter = Counter()
for q in questions:
    for i, opt in enumerate(q["options"]):
        if opt["correct"]:
            pos_counter[i] = pos_counter.get(i, 0) + 1

print("=" * 60)
print("1. CORRECT ANSWER POSITION (0-indexed)")
print("=" * 60)
labels = {0: "A (1st)", 1: "B (2nd)", 2: "C (3rd)", 3: "D (4th)"}
for pos in sorted(pos_counter):
    count = pos_counter[pos]
    pct = count / total * 100
    print(f"   {labels.get(pos, pos)}: {count} times ({pct:.1f}%)")

# ============================================================
# 2. "All of the ..." analysis
# ============================================================
all_of_patterns = [
    "all of the mentioned", "all of the above", "all above",
    "all of above", "d) all of the above", "d) all above"
]

print("\n" + "=" * 60)
print("2. 'ALL OF ...' PATTERN ANALYSIS")
print("=" * 60)

all_of_total = 0
all_of_correct = 0
for q in questions:
    for opt in q["options"]:
        txt = opt["text"].strip().lower()
        # Remove prefix like a) b) c) d)
        txt_clean = re.sub(r'^[a-d]\)\s*', '', txt)
        if any(p in txt_clean for p in ["all of the mentioned", "all of the above", "all above", "all of above"]):
            all_of_total += 1
            if opt["correct"]:
                all_of_correct += 1
            else:
                print(f"   EXCEPTION Q{q['id']}: '{opt['text']}' is NOT correct")

print(f"   Total 'All of...' options: {all_of_total}")
print(f"   Correct: {all_of_correct} ({all_of_correct/max(all_of_total,1)*100:.1f}%)")
print(f"   Wrong: {all_of_total - all_of_correct}")

# ============================================================
# 3. "None of the ..." analysis
# ============================================================
print("\n" + "=" * 60)
print("3. 'NONE OF ...' PATTERN ANALYSIS")
print("=" * 60)

none_total = 0
none_correct = 0
for q in questions:
    for opt in q["options"]:
        txt = opt["text"].strip().lower()
        txt_clean = re.sub(r'^[a-d]\)\s*', '', txt)
        if any(p in txt_clean for p in ["none of the mentioned", "none of the above", "none of above", "none of these"]):
            none_total += 1
            if opt["correct"]:
                none_correct += 1
                print(f"   EXCEPTION Q{q['id']}: '{opt['text']}' IS correct!")

print(f"   Total 'None of...' options: {none_total}")
print(f"   Correct: {none_correct} ({none_correct/max(none_total,1)*100:.1f}%)")
print(f"   Wrong: {none_total - none_correct}")

# ============================================================
# 4. LONGEST option analysis
# ============================================================
print("\n" + "=" * 60)
print("4. LONGEST OPTION IS CORRECT?")
print("=" * 60)

longest_correct = 0
longest_total = 0
longest_exceptions = []
for q in questions:
    if len(q["options"]) <= 2:  # skip True/False
        continue
    longest_total += 1
    max_len = max(len(opt["text"]) for opt in q["options"])
    longest_opts = [opt for opt in q["options"] if len(opt["text"]) == max_len]
    if any(opt["correct"] for opt in longest_opts):
        longest_correct += 1
    else:
        correct_opt = [opt for opt in q["options"] if opt["correct"]][0]
        longest_exceptions.append(q["id"])

print(f"   Total (non-T/F): {longest_total}")
print(f"   Longest is correct: {longest_correct} ({longest_correct/max(longest_total,1)*100:.1f}%)")
print(f"   Exceptions (IDs): {longest_exceptions}")

# ============================================================
# 5. SIGNIFICANTLY longer option (2+ words more)
# ============================================================
print("\n" + "=" * 60)
print("5. SIGNIFICANTLY LONGER OPTION (>=2 words more than avg)")
print("=" * 60)

sig_longer_correct = 0
sig_longer_total = 0
sig_longer_exceptions = []
for q in questions:
    if len(q["options"]) <= 2:
        continue
    word_counts = [len(opt["text"].split()) for opt in q["options"]]
    avg_words = sum(word_counts) / len(word_counts)
    
    has_sig_longer = False
    for i, opt in enumerate(q["options"]):
        wc = len(opt["text"].split())
        if wc >= avg_words + 2:
            has_sig_longer = True
            sig_longer_total += 1
            if opt["correct"]:
                sig_longer_correct += 1
            else:
                sig_longer_exceptions.append(q["id"])
    
print(f"   Options significantly longer: {sig_longer_total}")
print(f"   Correct: {sig_longer_correct} ({sig_longer_correct/max(sig_longer_total,1)*100:.1f}%)")
print(f"   Exception IDs: {sig_longer_exceptions}")

# ============================================================
# 6. Options starting with "Schedules" 
# ============================================================
print("\n" + "=" * 60)
print("6. OPTIONS STARTING WITH 'Schedules'")
print("=" * 60)

sched_total = 0
sched_correct = 0
for q in questions:
    for opt in q["options"]:
        txt = opt["text"].strip()
        txt_clean = re.sub(r'^[a-d]\)\s*', '', txt)
        if txt_clean.lower().startswith("schedules"):
            sched_total += 1
            if opt["correct"]:
                sched_correct += 1
                print(f"   EXCEPTION Q{q['id']}: '{opt['text']}' IS correct")

print(f"   Total: {sched_total}, Correct: {sched_correct}, Wrong: {sched_total - sched_correct}")

# ============================================================
# 7. TRUE/FALSE question analysis
# ============================================================
print("\n" + "=" * 60)
print("7. TRUE/FALSE QUESTIONS")
print("=" * 60)

tf_total = 0
true_correct = 0
false_correct = 0
for q in questions:
    opts_text = [opt["text"].strip().lower().rstrip('.') for opt in q["options"]]
    if set(opts_text) == {"true", "false"}:
        tf_total += 1
        for opt in q["options"]:
            if opt["correct"]:
                if "true" in opt["text"].lower():
                    true_correct += 1
                else:
                    false_correct += 1

print(f"   Total T/F questions: {tf_total}")
print(f"   TRUE is correct: {true_correct} ({true_correct/max(tf_total,1)*100:.1f}%)")
print(f"   FALSE is correct: {false_correct} ({false_correct/max(tf_total,1)*100:.1f}%)")

# ============================================================
# 8. Keyword in CORRECT answers analysis
# ============================================================
print("\n" + "=" * 60)
print("8. KEYWORDS THAT APPEAR MORE IN CORRECT ANSWERS")
print("=" * 60)

correct_words = Counter()
wrong_words = Counter()
for q in questions:
    for opt in q["options"]:
        txt = re.sub(r'^[a-d]\)\s*', '', opt["text"].strip().lower())
        words = re.findall(r'[a-z]+', txt)
        if opt["correct"]:
            correct_words.update(words)
        else:
            wrong_words.update(words)

# Find words that are strong indicators of correct answers
print("   Words heavily favoring CORRECT answers:")
stop_words = {'a', 'an', 'the', 'of', 'in', 'to', 'and', 'is', 'for', 'by', 'it', 'that', 'or', 'on', 'with', 'as', 'be', 'at', 'from'}
for word, count in correct_words.most_common(200):
    if word in stop_words or len(word) < 3:
        continue
    total_word = count + wrong_words.get(word, 0)
    if total_word >= 3:
        ratio = count / total_word
        if ratio > 0.55:
            print(f"     '{word}': {count}/{total_word} correct ({ratio*100:.0f}%)")

# ============================================================
# 9. Position A (first option) correct analysis
# ============================================================
print("\n" + "=" * 60)
print("9. FIRST OPTION (A) CORRECT - detailed")
print("=" * 60)

first_correct_ids = []
for q in questions:
    if q["options"][0]["correct"]:
        first_correct_ids.append(q["id"])
print(f"   Questions where A is correct: {len(first_correct_ids)}")
print(f"   IDs: {first_correct_ids}")

# ============================================================
# 10. "Increase/Improve" vs "Decrease/Reduce" pattern
# ============================================================
print("\n" + "=" * 60)
print("10. POSITIVE vs NEGATIVE wording in options")
print("=" * 60)

positive_words = ["increase", "improve", "better", "efficient", "allows", "enables", "provides"]
negative_words = ["decrease", "reduce", "prevent", "less", "lower", "limited"]

pos_total = 0
pos_correct = 0
neg_total = 0
neg_correct = 0

for q in questions:
    for opt in q["options"]:
        txt = opt["text"].strip().lower()
        has_pos = any(w in txt for w in positive_words)
        has_neg = any(w in txt for w in negative_words)
        if has_pos and not has_neg:
            pos_total += 1
            if opt["correct"]:
                pos_correct += 1
        elif has_neg and not has_pos:
            neg_total += 1
            if opt["correct"]:
                neg_correct += 1

print(f"   Positive-worded options: {pos_total}, Correct: {pos_correct} ({pos_correct/max(pos_total,1)*100:.1f}%)")
print(f"   Negative-worded options: {neg_total}, Correct: {neg_correct} ({neg_correct/max(neg_total,1)*100:.1f}%)")

# ============================================================
# 11. Options with specific technical terms tend to be correct
# ============================================================
print("\n" + "=" * 60)
print("11. SPECIFIC vs VAGUE options")
print("=" * 60)

# Options with parentheses (containing abbreviations/clarifications)
paren_total = 0
paren_correct = 0
for q in questions:
    for opt in q["options"]:
        txt = re.sub(r'^[a-d]\)\s*', '', opt["text"].strip())
        if '(' in txt and ')' in txt:
            paren_total += 1
            if opt["correct"]:
                paren_correct += 1

print(f"   Options with parentheses (more specific): {paren_total}")
print(f"   Correct: {paren_correct} ({paren_correct/max(paren_total,1)*100:.1f}%)")

# ============================================================
# 12. Options containing commas (listing multiple things)
# ============================================================
print("\n" + "=" * 60)
print("12. OPTIONS WITH COMMAS (listing multiple items)")
print("=" * 60)

comma_total = 0
comma_correct = 0
for q in questions:
    if len(q["options"]) <= 2:
        continue
    for opt in q["options"]:
        txt = re.sub(r'^[a-d]\)\s*', '', opt["text"].strip())
        if ',' in txt:
            comma_total += 1
            if opt["correct"]:
                comma_correct += 1

print(f"   Options with commas: {comma_total}")
print(f"   Correct: {comma_correct} ({comma_correct/max(comma_total,1)*100:.1f}%)")

# ============================================================
# 13. "NOT" questions - which position tends to be correct?
# ============================================================
print("\n" + "=" * 60)
print("13. 'NOT' QUESTIONS - position analysis")
print("=" * 60)

not_q_pos = Counter()
not_total = 0
for q in questions:
    if "NOT" in q["text"] or "not true" in q["text"].lower():
        not_total += 1
        for i, opt in enumerate(q["options"]):
            if opt["correct"]:
                not_q_pos[i] += 1

print(f"   Total 'NOT' questions: {not_total}")
for pos in sorted(not_q_pos):
    print(f"   Position {labels.get(pos, pos)}: {not_q_pos[pos]} ({not_q_pos[pos]/max(not_total,1)*100:.1f}%)")

# ============================================================
# 14. "Out of place" / irrelevant option is the answer for NOT questions
# ============================================================
print("\n" + "=" * 60)
print("14. OPTION THAT SEEMS 'OUT OF PLACE' IN NOT QUESTIONS")
print("=" * 60)
print("   (In 'NOT' questions, look for an option that doesn't belong)")
print("   Correct answers in NOT questions:")
for q in questions:
    if "NOT" in q["text"] or "not true" in q["text"].lower():
        for opt in q["options"]:
            if opt["correct"]:
                print(f"   Q{q['id']}: '{opt['text']}'")

# ============================================================
# 15. Analyze if question word matches answer word
# ============================================================
print("\n" + "=" * 60)
print("15. KEYWORD ECHO - question keyword appears in correct answer")
print("=" * 60)

echo_total = 0
echo_correct = 0
for q in questions:
    if len(q["options"]) <= 2:
        continue
    q_words = set(re.findall(r'[a-z]{4,}', q["text"].lower()))
    q_words -= stop_words
    
    for opt in q["options"]:
        txt = re.sub(r'^[a-d]\)\s*', '', opt["text"].strip().lower())
        opt_words = set(re.findall(r'[a-z]{4,}', txt))
        common = q_words & opt_words
        if len(common) >= 2:
            echo_total += 1
            if opt["correct"]:
                echo_correct += 1

print(f"   Options echoing 2+ question keywords: {echo_total}")
print(f"   Correct: {echo_correct} ({echo_correct/max(echo_total,1)*100:.1f}%)")

# ============================================================
# 16. Most common CORRECT option position for each question range
# ============================================================
print("\n" + "=" * 60)
print("16. CORRECT POSITION BY QUESTION RANGE")
print("=" * 60)

ranges = [(1,30), (31,60), (61,90), (91,120), (121,150), (151,180)]
for start, end in ranges:
    range_pos = Counter()
    for q in questions:
        if start <= q["id"] <= end:
            for i, opt in enumerate(q["options"]):
                if opt["correct"]:
                    range_pos[i] += 1
    total_range = sum(range_pos.values())
    print(f"   Q{start}-Q{end}:")
    for pos in sorted(range_pos):
        print(f"     {labels.get(pos, pos)}: {range_pos[pos]} ({range_pos[pos]/total_range*100:.1f}%)")
