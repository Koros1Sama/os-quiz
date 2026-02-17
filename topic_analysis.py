import json
import re
from collections import defaultdict, Counter

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# ============================================================
# TOPIC DETECTION: Categorize each question by topic keywords
# ============================================================

topic_keywords = {
    "deadlock": ["deadlock", "circular wait", "banker", "resource allocation graph", "rag"],
    "scheduling": ["scheduling", "scheduler", "fcfs", "sjn", "round robin", "convoy", "burst time", "preemptive", "edf", "time-sharing", "cpu time"],
    "memory": ["memory", "paging", "page table", "page fault", "thrashing", "virtual memory", "fragmentation", "tlb", "swapping", "demand paging", "page replacement", "lru", "opt"],
    "process": ["process state", "process control", "pcb", "fork", "thread", "multithreading", "context switching", "race condition", "critical section", "synchronization", "semaphore", "parallelism"],
    "file_system": ["file system", "file allocation", "directory", "inode", "fat", "ntfs", "ext4", "journaling", "file extension", "hard link", "file attribute"],
    "os_basics": ["operating system", "kernel", "shell", "bootloader", "device driver", "interrupt", "dual-mode", "system call", "os service", "os function"],
    "io_device": ["i/o", "dma", "spooling", "disk scheduling", "block device", "character", "device management", "sstf"],
    "security": ["security", "firewall", "authentication", "access control", "acl", "unauthorized", "spoofing"],
}

def detect_topic(q_text):
    q_lower = q_text.lower()
    scores = {}
    for topic, keywords in topic_keywords.items():
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > 0:
            scores[topic] = score
    if scores:
        return max(scores, key=scores.get)
    return "other"

# Categorize all questions
topic_questions = defaultdict(list)
for q in questions:
    topic = detect_topic(q["text"])
    correct = None
    for opt in q["options"]:
        if opt["correct"]:
            correct = clean(opt["text"])
    topic_questions[topic].append({"id": q["id"], "text": q["text"], "correct": correct, "options": q["options"]})

lines = []
def out(s=""):
    lines.append(s)

out("TOPIC ANALYSIS RESULTS")
out("=" * 70)

for topic, qs in sorted(topic_questions.items(), key=lambda x: -len(x[1])):
    out(f"\n{'='*70}")
    out(f"TOPIC: {topic.upper()} ({len(qs)} questions)")
    out(f"{'='*70}")
    
    # Find common words in correct answers for this topic
    correct_words = Counter()
    for q in qs:
        words = re.findall(r'[a-zA-Z]{3,}', q["correct"].lower())
        for w in words:
            correct_words[w] += 1
    
    out(f"Most common words in correct answers:")
    for word, count in correct_words.most_common(15):
        pct = count / len(qs) * 100
        if count >= 2:
            out(f"  '{word}': {count}/{len(qs)} ({pct:.0f}%)")
    
    # For each question, what pattern in the correct answer distinguishes it?
    out(f"\nQuestion-by-question patterns:")
    for q in qs:
        correct = q["correct"]
        wrong = [clean(opt["text"]) for opt in q["options"] if not opt["correct"]]
        
        # Check structural patterns
        patterns = []
        
        # Is it longest?
        correct_len = len(correct.split())
        wrong_lens = [len(w.split()) for w in wrong]
        avg_wrong = sum(wrong_lens) / max(len(wrong_lens), 1)
        if correct_len >= avg_wrong + 2:
            patterns.append("LONGEST")
        
        # Does it contain "all of"?
        if any(p in correct.lower() for p in ["all of the", "all above", "all of above"]):
            patterns.append("ALL_OF")
        
        # Does correct have commas?
        if "," in correct and not any("," in w for w in wrong):
            patterns.append("HAS_COMMAS")
        
        # Does correct have parentheses?
        if "(" in correct:
            patterns.append("HAS_PARENS")
        
        # Is correct the most specific/detailed?
        if correct_len == max(correct_len, *wrong_lens):
            patterns.append("MOST_DETAILED")
        
        pattern_str = ", ".join(patterns) if patterns else "NO_STRUCTURAL"
        out(f"  Q{q['id']}: [{pattern_str}] -> {correct[:60]}")

# ============================================================
# CROSS-TOPIC PATTERN: Question keyword -> Answer keyword mapping
# ============================================================
out(f"\n{'='*70}")
out("QUESTION->ANSWER KEYWORD MAPPING")
out("When question contains X, correct answer often contains Y")
out(f"{'='*70}")

# For each topic, find: if question mentions X, answer contains Y
q_to_a_patterns = defaultdict(lambda: defaultdict(int))

for q in questions:
    q_lower = q["text"].lower()
    correct = None
    for opt in q["options"]:
        if opt["correct"]:
            correct = clean(opt["text"]).lower()
    
    # Check specific patterns
    q_keywords = {
        "deadlock": "deadlock" in q_lower,
        "NOT": " not " in q_lower.replace("?", " ?"),
        "scheduling": "scheduling" in q_lower or "scheduler" in q_lower,
        "page": "page" in q_lower,
        "file system": "file system" in q_lower or "file allocation" in q_lower,
        "thread": "thread" in q_lower,
        "process state": "process state" in q_lower or "state of" in q_lower,
        "memory": "memory" in q_lower,
        "os service": "os service" in q_lower or "operating system service" in q_lower,
        "advantage": "advantage" in q_lower,
        "purpose": "purpose" in q_lower,
        "example": "example" in q_lower,
    }
    
    for qk, present in q_keywords.items():
        if present:
            a_words = re.findall(r'[a-zA-Z]{3,}', correct)
            for aw in a_words:
                q_to_a_patterns[qk][aw] += 1

for qk, answers in sorted(q_to_a_patterns.items()):
    out(f"\nWhen question mentions '{qk}':")
    for aw, count in sorted(answers.items(), key=lambda x: -x[1])[:8]:
        if count >= 2:
            out(f"  -> answer contains '{aw}': {count} times")

# ============================================================
# STRUCTURAL PATTERN COVERAGE
# ============================================================
out(f"\n{'='*70}")
out("STRUCTURAL PATTERN ACCURACY")
out(f"{'='*70}")

# Test: for each structural pattern, how many questions does it cover correctly?
structural_results = defaultdict(lambda: {"correct": 0, "wrong": 0, "ids_wrong": []})

for q in questions:
    correct_opt = None
    wrong_opts = []
    all_opts = []
    for i, opt in enumerate(q["options"]):
        cleaned = clean(opt["text"])
        all_opts.append((cleaned, opt["correct"], i))
        if opt["correct"]:
            correct_opt = (cleaned, i)
        else:
            wrong_opts.append((cleaned, i))
    
    # Pattern: pick the option with most words
    longest_idx = max(range(len(all_opts)), key=lambda i: len(all_opts[i][0].split()))
    if all_opts[longest_idx][1]:
        structural_results["longest"]["correct"] += 1
    else:
        structural_results["longest"]["wrong"] += 1
        structural_results["longest"]["ids_wrong"].append(q["id"])
    
    # Pattern: pick option with parentheses (if only one has them)
    paren_opts = [(i, o) for i, (o, c, idx) in enumerate(all_opts) if "(" in o]
    if len(paren_opts) == 1:
        if all_opts[paren_opts[0][0]][1]:
            structural_results["unique_parens"]["correct"] += 1
        else:
            structural_results["unique_parens"]["wrong"] += 1
            structural_results["unique_parens"]["ids_wrong"].append(q["id"])
    
    # Pattern: pick option with most capital letters
    caps = [(i, sum(1 for c in o if c.isupper())) for i, (o, correct, idx) in enumerate(all_opts)]
    most_caps_idx = max(caps, key=lambda x: x[1])[0]
    if all_opts[most_caps_idx][1]:
        structural_results["most_caps"]["correct"] += 1
    else:
        structural_results["most_caps"]["wrong"] += 1

for pattern, stats in structural_results.items():
    total = stats["correct"] + stats["wrong"]
    pct = stats["correct"] / total * 100
    out(f"  {pattern}: {stats['correct']}/{total} = {pct:.1f}%")
    if stats.get("ids_wrong") and len(stats["ids_wrong"]) <= 20:
        out(f"    Wrong: {stats['ids_wrong']}")

with open("topic_analysis_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done! Results in topic_analysis_output.txt")
