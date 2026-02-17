import json, re

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# ============================================================
# 1. ALL forms of "prevent" (prevent, prevents, preventing, prevented, prevention)
# ============================================================
print("=" * 60)
print("ALL 'prevent*' forms in options")
print("=" * 60)

prevent_correct = 0
prevent_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bprevent\w*\b', text, re.IGNORECASE):
            status = "✅" if opt["correct"] else "❌"
            # Check what other keywords exist in the correct answer
            competing = []
            if opt["correct"]:
                for kw in ['unauthorized', 'circular', 'wait', 'pages', 'switching', 'than', 'create', 'web', 'allows', 'among', 'highest', 'each', 'share', 'ready', 'reduce']:
                    if re.search(r'\b' + kw + r'\b', text, re.IGNORECASE):
                        competing.append(kw)
            form = re.search(r'\b(prevent\w*)\b', text, re.IGNORECASE).group(1)
            print(f"  Q{q['id']}: {status} [{form}] '{text[:70]}' {('← has: ' + str(competing)) if competing else ''}")
            if opt["correct"]:
                prevent_correct += 1
            else:
                prevent_wrong += 1

print(f"\nPrevent*: correct={prevent_correct}, wrong={prevent_wrong}")
print(f"Wrong rate: {prevent_wrong}/{prevent_correct+prevent_wrong} = {prevent_wrong*100//(prevent_correct+prevent_wrong)}%")

# ============================================================
# 2. "reduce" / "reduces" / "reduced" / "reducing"
# ============================================================
print("\n" + "=" * 60)
print("ALL 'reduce*' forms in options")
print("=" * 60)

reduce_correct = 0
reduce_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\breduc\w*\b', text, re.IGNORECASE):
            status = "✅" if opt["correct"] else "❌"
            form = re.search(r'\b(reduc\w*)\b', text, re.IGNORECASE).group(1)
            print(f"  Q{q['id']}: {status} [{form}] '{text[:70]}'")
            if opt["correct"]:
                reduce_correct += 1
            else:
                reduce_wrong += 1

print(f"\nReduce*: correct={reduce_correct}, wrong={reduce_wrong}")
print(f"Wrong rate: {reduce_wrong}/{reduce_correct+reduce_wrong} = {reduce_wrong*100//(reduce_correct+reduce_wrong)}%")

# ============================================================
# 3. "increase" / "increases" / "increased" / "increasing"  
# ============================================================
print("\n" + "=" * 60)
print("ALL 'increase*' forms in options")
print("=" * 60)

inc_correct = 0
inc_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bincrease\w*\b', text, re.IGNORECASE):
            status = "✅" if opt["correct"] else "❌"
            form = re.search(r'\b(increase\w*)\b', text, re.IGNORECASE).group(1)
            # Check for other golden keywords
            competing = []
            for kw in ['unauthorized', 'circular', 'wait', 'pages', 'switching', 'than', 'create', 'web', 'allows', 'among', 'highest', 'each', 'share']:
                if re.search(r'\b' + kw + r'\b', text, re.IGNORECASE):
                    competing.append(kw)
            print(f"  Q{q['id']}: {status} [{form}] '{text[:70]}' {('← has: ' + str(competing)) if competing else ''}")
            if opt["correct"]:
                inc_correct += 1
            else:
                inc_wrong += 1

print(f"\nIncrease*: correct={inc_correct}, wrong={inc_wrong}")
print(f"Correct rate: {inc_correct}/{inc_correct+inc_wrong} = {inc_correct*100//(inc_correct+inc_wrong)}%")

# ============================================================
# 4. For the Q117 exception - what makes it special?
# ============================================================
print("\n" + "=" * 60)
print("Q117 analysis - why is Reduce correct here?")
print("=" * 60)
q117 = [q for q in questions if q["id"] == 117][0]
print(f"Q: {q117['text']}")
for opt in q117["options"]:
    text = clean(opt["text"])
    longest = len(text.split()) == max(len(clean(o["text"]).split()) for o in q117["options"])
    print(f"  {'✅' if opt['correct'] else '❌'} '{text}' | longest={longest}")

# ============================================================
# 5. Echo pattern - does question keyword match answer?
# ============================================================
print("\n" + "=" * 60)
print("'Echo' pattern - answer contains question's keyword")
print("=" * 60)
echo_pairs = [
    ("device driver", "device", [49]),
    ("process schedul", "schedul", [52, 55, 132, 157, 177]),
    ("file system", "file", [122, 154]),
    ("input and output", "I/O", [126]),
    ("interrupt", "interrupt", [136]),
    ("memory", "memory", [25, 143, 160]),
]
# Just show them for reference

# ============================================================
# 6. "Improve" / "Improved"
# ============================================================
print("\n" + "=" * 60)
print("ALL 'improve*' forms in options")
print("=" * 60)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bimprov\w*\b', text, re.IGNORECASE):
            status = "✅" if opt["correct"] else "❌"
            form = re.search(r'\b(improv\w*)\b', text, re.IGNORECASE).group(1)
            print(f"  Q{q['id']}: {status} [{form}] '{text[:70]}'")

# ============================================================
# 7. "within" 
# ============================================================
print("\n" + "=" * 60)
print("'within' in options")
print("=" * 60)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\bwithin\b', text, re.IGNORECASE):
            print(f"  Q{q['id']}: {'✅' if opt['correct'] else '❌'} '{text[:70]}'")

# ============================================================
# 8. "lightweight"
# ============================================================
print("\n" + "=" * 60)
print("'lightweight' in options")
print("=" * 60)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"])
        if re.search(r'\blightweight\b', text, re.IGNORECASE):
            print(f"  Q{q['id']}: {'✅' if opt['correct'] else '❌'} '{text[:70]}'")
