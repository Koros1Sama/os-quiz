import json
import re
from collections import Counter, defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ============================================================
# ADVANCED KEYWORD PRIORITY ANALYSIS
# Goal: Find keywords where picking the option with that keyword
# gives a HIGH hit rate, and build a priority chain.
# ============================================================

stop_words = {'a', 'an', 'the', 'of', 'in', 'to', 'and', 'is', 'for', 'by',
              'it', 'that', 'or', 'on', 'with', 'as', 'be', 'at', 'from',
              'not', 'are', 'its', 'has', 'can', 'does', 'do', 'each',
              'than', 'into', 'which', 'what', 'this', 'when', 'how', 'all',
              'will', 'one', 'new', 'more', 'used', 'program', 'programs',
              'system', 'systems', 'operating', 'following', 'process',
              'processes', 'memory', 'file', 'management', 'cpu',
              'type', 'types', 'called', 'between'}

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip().lower())

def get_words(text):
    return set(re.findall(r'[a-z]{3,}', text)) - stop_words

# Skip T/F and "All of..." questions since those are already covered
def should_skip(q):
    opts_text = [clean(opt["text"]) for opt in q["options"]]
    # T/F
    if len(q["options"]) == 2:
        return True
    # All of...
    for ot in opts_text:
        if any(p in ot for p in ["all of the mentioned", "all of the above", "all above", "all of above"]):
            return True
    return False

# ============================================================
# PHASE 1: For each keyword, compute:
#   - How many questions have this keyword in at least one option
#   - If you always pick the option(s) with this keyword, how often are you correct?
# ============================================================

keyword_stats = {}  # word -> {questions_with_word, correct_if_picked, question_ids}

remaining_questions = [q for q in questions if not should_skip(q)]
print(f"Analyzing {len(remaining_questions)} questions (excluding T/F and 'All of...' questions)\n")

for q in remaining_questions:
    # For each option, get its keywords
    for opt in q["options"]:
        txt = clean(opt["text"])
        words = get_words(txt)
        for w in words:
            if w not in keyword_stats:
                keyword_stats[w] = {"appears_in_options": 0, "correct_picks": 0, "q_ids": [], "total_options_with_word": 0}
            
    # Now per question: does picking the option with word W give us the correct answer?
    seen_words_this_q = set()
    for opt in q["options"]:
        txt = clean(opt["text"])
        words = get_words(txt)
        for w in words:
            keyword_stats[w]["total_options_with_word"] += 1
            if w not in seen_words_this_q:
                seen_words_this_q.add(w)
                keyword_stats[w]["appears_in_options"] += 1
                
    # The key metric: if ONLY the correct option has this word, picking it works
    correct_opt = [opt for opt in q["options"] if opt["correct"]][0]
    correct_words = get_words(clean(correct_opt["text"]))
    wrong_opts = [opt for opt in q["options"] if not opt["correct"]]
    all_wrong_words = set()
    for wopt in wrong_opts:
        all_wrong_words |= get_words(clean(wopt["text"]))
    
    # Words UNIQUE to correct answer (not in any wrong option)
    unique_correct_words = correct_words - all_wrong_words
    for w in unique_correct_words:
        keyword_stats[w]["correct_picks"] += 1
        keyword_stats[w]["q_ids"].append(q["id"])

# ============================================================
# PHASE 2: Strategy - if a word appears in options and ONLY in
# the correct option, picking that word = correct answer.
# Find words with highest "unique correctness" ratio.
# ============================================================

print("=" * 70)
print("KEYWORDS UNIQUE TO CORRECT ANSWER (appear in correct but NOT in wrong)")
print("=" * 70)

good_keywords = []
for word, stats in keyword_stats.items():
    if stats["correct_picks"] >= 2:  # at least 2 questions
        good_keywords.append((word, stats["correct_picks"], stats["appears_in_options"], stats["q_ids"]))

good_keywords.sort(key=lambda x: (-x[1], x[0]))

for word, correct, total_q, qids in good_keywords:
    print(f"  '{word}': unique to correct in {correct} questions → IDs: {qids}")

# ============================================================
# PHASE 3: SIMULATION - Build priority chain and simulate accuracy
# ============================================================

print("\n" + "=" * 70)
print("SIMULATION: Testing keyword selection strategy")
print("=" * 70)

# Strategy: For each question, find the option that contains the most
# "high-value" unique keywords. 

# First, build a lookup: word -> how many times it's uniquely correct
word_score = {}
for word, stats in keyword_stats.items():
    if stats["correct_picks"] >= 2:
        word_score[word] = stats["correct_picks"]

# Now simulate: for each question, score each option by summing word_scores
# of unique keywords, pick the highest scored option
correct_by_keywords = 0
questions_with_signal = 0

for q in remaining_questions:
    option_scores = []
    for opt in q["options"]:
        txt = clean(opt["text"])
        words = get_words(txt)
        score = sum(word_score.get(w, 0) for w in words)
        option_scores.append((score, opt["correct"], opt["text"]))
    
    max_score = max(s for s, _, _ in option_scores)
    if max_score > 0:
        questions_with_signal += 1
        # Pick the option with highest score
        best = [opt for s, c, opt in option_scores if s == max_score]
        best_correct = any(c for s, c, _ in option_scores if s == max_score)
        if best_correct:
            correct_by_keywords += 1

print(f"  Questions with keyword signal: {questions_with_signal}/{len(remaining_questions)}")
print(f"  Correct by keywords: {correct_by_keywords}/{questions_with_signal} ({correct_by_keywords/max(questions_with_signal,1)*100:.1f}%)")

# ============================================================
# PHASE 4: SINGLE-WORD DECISION RULES
# For each word, check: "If I see this word in exactly one option, 
# and I pick that option, what's my accuracy?"
# ============================================================

print("\n" + "=" * 70)
print("SINGLE-WORD DECISION RULES (word in exactly 1 option → pick it)")
print("=" * 70)

word_decision_stats = defaultdict(lambda: {"total": 0, "correct": 0, "wrong_qids": []})

for q in remaining_questions:
    # Count how many options have each word
    word_to_options = defaultdict(list)
    for i, opt in enumerate(q["options"]):
        txt = clean(opt["text"])
        words = get_words(txt)
        for w in words:
            word_to_options[w].append((i, opt["correct"]))
    
    # Words that appear in exactly 1 option
    for w, opts in word_to_options.items():
        if len(opts) == 1:
            idx, is_correct = opts[0]
            word_decision_stats[w]["total"] += 1
            if is_correct:
                word_decision_stats[w]["correct"] += 1
            else:
                word_decision_stats[w]["wrong_qids"].append(q["id"])

print("\nHigh-value decision words (>=3 questions, >=80% accuracy):")
decision_words = []
for word, stats in word_decision_stats.items():
    if stats["total"] >= 3 and stats["correct"] / stats["total"] >= 0.80:
        accuracy = stats["correct"] / stats["total"] * 100
        decision_words.append((word, stats["correct"], stats["total"], accuracy, stats["wrong_qids"]))

decision_words.sort(key=lambda x: (-x[3], -x[2]))

for word, correct, total, acc, wrong_qids in decision_words:
    exc = f" (exceptions: {wrong_qids})" if wrong_qids else ""
    print(f"  '{word}': {correct}/{total} = {acc:.0f}%{exc}")

# ============================================================
# PHASE 5: WORD-PAIR PRIORITY ANALYSIS
# When two "good" words conflict (in different options), which wins?
# ============================================================

print("\n" + "=" * 70)
print("WORD-PAIR CONFLICTS (when good keywords are in different options)")
print("=" * 70)

good_word_set = set(w for w, c, t, a, _ in decision_words if a >= 80)

conflict_count = 0
for q in remaining_questions:
    opt_good_words = []
    for opt in q["options"]:
        txt = clean(opt["text"])
        words = get_words(txt) & good_word_set
        opt_good_words.append((words, opt["correct"], opt["text"]))
    
    # Find conflicts: multiple options with good words
    options_with_good = [(i, ws, c, t) for i, (ws, c, t) in enumerate(opt_good_words) if ws]
    if len(options_with_good) >= 2:
        conflict_count += 1
        correct_opt = [(i, ws, t) for i, ws, c, t in options_with_good if c]
        wrong_opt = [(i, ws, t) for i, ws, c, t in options_with_good if not c]
        if correct_opt and wrong_opt:
            print(f"  Q{q['id']}: CORRECT has {correct_opt[0][1]}, WRONG has {[w[1] for w in wrong_opt]}")

print(f"\n  Total conflicts: {conflict_count}")

# ============================================================
# PHASE 6: FULL SIMULATION with all rules combined
# ============================================================

print("\n" + "=" * 70)
print("FULL ALGORITHM SIMULATION (all rules)")
print("=" * 70)

total_correct = 0
total_questions = len(questions)
rule_used = Counter()

for q in questions:
    opts = q["options"]
    opts_clean = [clean(opt["text"]) for opt in opts]
    
    picked_correct = False
    used_rule = "none"
    
    # Rule 1: All of the mentioned/above
    for i, ot in enumerate(opts_clean):
        if any(p in ot for p in ["all of the mentioned", "all of the above", "all above", "all of above"]):
            picked_correct = opts[i]["correct"]
            used_rule = "all_of"
            break
    
    if used_rule != "none":
        if picked_correct:
            total_correct += 1
        rule_used[used_rule] += 1
        continue
    
    # Rule 2: Eliminate "None of..."
    remaining_opts = []
    for i, ot in enumerate(opts_clean):
        if not any(p in ot for p in ["none of the mentioned", "none of the above", "none of above", "none of these"]):
            remaining_opts.append(i)
    
    # Rule 3: Eliminate "Schedules..."
    remaining_opts = [i for i in remaining_opts if not opts_clean[i].startswith("schedules")]
    
    if len(remaining_opts) == 1:
        picked_correct = opts[remaining_opts[0]]["correct"]
        used_rule = "elimination"
        if picked_correct:
            total_correct += 1
        rule_used[used_rule] += 1
        continue
    
    # Rule 4: NOT questions - pick the "odd one out"
    # (skip for simulation, hard to automate)
    
    # Rule 5: Significantly longer option
    if len(opts) > 2:
        word_counts = [len(opts[i]["text"].split()) for i in remaining_opts]
        if word_counts:
            avg_words = sum(word_counts) / len(word_counts)
            sig_longer = [(remaining_opts[j], word_counts[j]) for j in range(len(remaining_opts)) if word_counts[j] >= avg_words + 2]
            if len(sig_longer) == 1:
                picked_correct = opts[sig_longer[0][0]]["correct"]
                used_rule = "sig_longer"
                if picked_correct:
                    total_correct += 1
                rule_used[used_rule] += 1
                continue
    
    # Rule 6: Options with commas
    comma_opts = [i for i in remaining_opts if ',' in opts_clean[i]]
    if len(comma_opts) == 1:
        picked_correct = opts[comma_opts[0]]["correct"]
        used_rule = "comma"
        if picked_correct:
            total_correct += 1
        rule_used[used_rule] += 1
        continue
    
    # Rule 7: Keyword scoring
    if len(opts) > 2:
        best_score = -1
        best_idx = remaining_opts[0] if remaining_opts else 0
        for i in remaining_opts:
            txt = clean(opts[i]["text"])
            words = get_words(txt)
            score = sum(word_score.get(w, 0) for w in words)
            if score > best_score:
                best_score = score
                best_idx = i
        
        if best_score > 0:
            picked_correct = opts[best_idx]["correct"]
            used_rule = "keyword_score"
            if picked_correct:
                total_correct += 1
            rule_used[used_rule] += 1
            continue
    
    # Rule 8: Pick longest remaining option
    if remaining_opts:
        longest_idx = max(remaining_opts, key=lambda i: len(opts[i]["text"]))
        picked_correct = opts[longest_idx]["correct"]
        used_rule = "longest"
    else:
        picked_correct = opts[0]["correct"]
        used_rule = "fallback"
    
    if picked_correct:
        total_correct += 1
    rule_used[used_rule] += 1

print(f"\n  TOTAL CORRECT: {total_correct}/{total_questions} = {total_correct/total_questions*100:.1f}%")
print(f"\n  Rules breakdown:")
for rule, count in rule_used.most_common():
    print(f"    {rule}: used {count} times")
