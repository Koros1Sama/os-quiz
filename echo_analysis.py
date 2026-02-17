import json, re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

def get_words(text):
    return set(re.findall(r'[a-zA-Z]+', text.lower()))

# Key question words to ignore (too generic)
STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','process','when','between'}

# ============================================================
# ECHO PATTERN ANALYSIS  
# ============================================================
print("=" * 70)
print("ECHO PATTERN: Does the correct answer contain a keyword from the question?")
print("=" * 70)

echo_results = []
no_echo = []

for q in questions:
    # Skip True/False
    if len(q["options"]) <= 2:
        continue
    
    q_words = get_words(q["text"]) - STOP_WORDS
    
    correct_opt = None
    wrong_opts = []
    for opt in q["options"]:
        text = clean(opt["text"])
        if opt["correct"]:
            correct_opt = text
        else:
            wrong_opts.append(text)
    
    if not correct_opt:
        continue
    
    correct_words = get_words(correct_opt)
    
    # Find words that appear in BOTH question AND correct answer
    echo_words = q_words & correct_words
    
    # Check if wrong options also have echo words
    wrong_echo_counts = []
    for wo in wrong_opts:
        wo_words = get_words(wo)
        wo_echo = q_words & wo_words
        wrong_echo_counts.append(len(wo_echo - STOP_WORDS))
    
    # "Unique echo" = correct answer echoes question words that NO wrong option does
    unique_echo = set()
    for ew in echo_words:
        found_in_wrong = False
        for wo in wrong_opts:
            if ew in get_words(wo):
                found_in_wrong = True
                break
        if not found_in_wrong:
            unique_echo.add(ew)
    
    if echo_words:
        echo_results.append({
            'id': q['id'],
            'echo_words': echo_words,
            'unique_echo': unique_echo,
            'correct': correct_opt,
            'is_not': bool(re.search(r'\bnot\b', q['text'], re.IGNORECASE)),
        })

# Now analyze: when ONLY the correct option has the echo word (unique echo)
print("\n--- UNIQUE ECHO: correct option echoes a Q-word that NO wrong option has ---")
unique_echo_correct = 0
unique_echo_total = 0

for e in echo_results:
    if e['unique_echo']:
        unique_echo_total += 1
        unique_echo_correct += 1  # by definition it's the correct one
        if e['is_not']:
            tag = " [NOT]"
        else:
            tag = ""
        print(f"  Q{e['id']}{tag}: echo={e['unique_echo']} → '{e['correct'][:60]}'")

print(f"\nUnique echo found in {unique_echo_total} questions (all correct by definition)")

# ============================================================
# Now the REAL test: if we use echo as a RULE, how often does it work?
# For each question, check: which option(s) share the most words with the question?
# ============================================================
print("\n" + "=" * 70)
print("ECHO AS RULE: Pick option with most shared words with question")
print("=" * 70)

echo_rule_correct = 0
echo_rule_wrong = 0
echo_rule_tie = 0
echo_not_correct = 0
echo_not_wrong = 0

golden_t1 = ['circular','unauthorized','wait','pages','switching','than','create','web','allows','among','highest']

for q in questions:
    if len(q["options"]) <= 2:
        continue
    
    q_words = get_words(q["text"]) - STOP_WORDS
    is_not = bool(re.search(r'\bnot\b', q['text'], re.IGNORECASE))
    
    # Score each option by echo words count
    scores = []
    for opt in q["options"]:
        text = clean(opt["text"])
        opt_words = get_words(text)
        shared = q_words & opt_words
        scores.append((len(shared), opt["correct"], text))
    
    max_score = max(s[0] for s in scores)
    if max_score == 0:
        continue  # no echo at all
    
    winners = [s for s in scores if s[0] == max_score]
    
    if len(winners) == 1:
        if winners[0][1]:  # correct
            echo_rule_correct += 1
            if is_not:
                echo_not_correct += 1
        else:
            echo_rule_wrong += 1
            if is_not:
                echo_not_wrong += 1
    else:
        echo_rule_tie += 1

total_echo = echo_rule_correct + echo_rule_wrong
print(f"Echo rule (single winner): correct={echo_rule_correct}, wrong={echo_rule_wrong}")
print(f"Accuracy: {echo_rule_correct}/{total_echo} = {echo_rule_correct*100//total_echo}%")
print(f"Ties (multiple options same echo score): {echo_rule_tie}")
print(f"In NOT questions: correct={echo_not_correct}, wrong={echo_not_wrong}")

# ============================================================
# Echo when NO golden keyword exists
# ============================================================
print("\n" + "=" * 70)
print("ECHO when NO golden keyword is in any option")
print("=" * 70)

echo_no_kw_correct = 0
echo_no_kw_wrong = 0

for q in questions:
    if len(q["options"]) <= 2:
        continue
    
    # Check if any option has a golden keyword
    has_golden = False
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        for kw in golden_t1:
            if kw in text.split():
                has_golden = True
                break
    
    if has_golden:
        continue
    
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
        if winners[0][1]:
            echo_no_kw_correct += 1
        else:
            echo_no_kw_wrong += 1

total = echo_no_kw_correct + echo_no_kw_wrong
if total > 0:
    print(f"Without golden keywords: correct={echo_no_kw_correct}, wrong={echo_no_kw_wrong}")
    print(f"Accuracy: {echo_no_kw_correct}/{total} = {echo_no_kw_correct*100//total}%")

# ============================================================
# Echo vs Longest
# ============================================================
print("\n" + "=" * 70)
print("ECHO vs LONGEST: When they disagree, who wins?")
print("=" * 70)

echo_wins = 0
longest_wins = 0

for q in questions:
    if len(q["options"]) <= 2:
        continue
    
    q_words = get_words(q["text"]) - STOP_WORDS
    
    # Echo winner
    scores = []
    for opt in q["options"]:
        text = clean(opt["text"])
        opt_words = get_words(text)
        shared = q_words & opt_words
        scores.append((len(shared), len(text.split()), opt["correct"], text))
    
    max_echo = max(s[0] for s in scores)
    echo_winners = [s for s in scores if s[0] == max_echo]
    
    # Longest winner
    max_len = max(s[1] for s in scores)
    longest_winners = [s for s in scores if s[1] == max_len]
    
    if len(echo_winners) == 1 and len(longest_winners) == 1:
        echo_pick = echo_winners[0]
        longest_pick = longest_winners[0]
        
        if echo_pick[3] != longest_pick[3]:  # they disagree
            if echo_pick[2] and not longest_pick[2]:
                echo_wins += 1
            elif longest_pick[2] and not echo_pick[2]:
                longest_wins += 1

print(f"When they disagree: Echo wins={echo_wins}, Longest wins={longest_wins}")
