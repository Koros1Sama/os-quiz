import json
import re

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

# ============================================================
# 1. Verify "each" keyword
# ============================================================
print("=" * 60)
print("KEYWORD: 'each'")
print("=" * 60)

each_correct = 0
each_wrong = 0

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        words = set(text.split())
        if "each" in words:
            status = "✅" if opt["correct"] else "❌"
            print(f"  Q{q['id']}: {status} '{clean(opt['text'])[:60]}'")
            if opt["correct"]:
                each_correct += 1
            else:
                each_wrong += 1

print(f"\n'each': correct={each_correct}, wrong={each_wrong}, rate={each_correct}/{each_correct+each_wrong}")

# Check uniqueness (each in only 1 option)
print("\nUnique 'each' (in only 1 option):")
for q in questions:
    opts_with_each = []
    for i, opt in enumerate(q["options"]):
        text = clean(opt["text"]).lower()
        if "each" in set(text.split()):
            opts_with_each.append((i, clean(opt["text"]), opt["correct"]))
    
    if len(opts_with_each) == 1:
        idx, text, correct = opts_with_each[0]
        print(f"  Q{q['id']}: {'✅' if correct else '❌'} '{text[:60]}'")
    elif len(opts_with_each) > 1:
        print(f"  Q{q['id']}: MULTIPLE ({len(opts_with_each)} options have 'each')")
        for idx, text, correct in opts_with_each:
            print(f"    {'✅' if correct else '❌'} '{text[:60]}'")

# ============================================================
# 2. Verify "highest" keyword
# ============================================================
print("\n" + "=" * 60)
print("KEYWORD: 'highest'")
print("=" * 60)

for q in questions:
    for opt in q["options"]:
        text = clean(opt["text"]).lower()
        if "highest" in set(text.split()):
            status = "✅" if opt["correct"] else "❌"
            print(f"  Q{q['id']}: {status} '{clean(opt['text'])[:60]}'")

# Check Q20 specifically
print("\n" + "=" * 60)
print("Q20 details:")
print("=" * 60)
q20 = [q for q in questions if q["id"] == 20][0]
print(f"Q: {q20['text']}")
for opt in q20["options"]:
    text = clean(opt["text"])
    words = set(text.lower().split())
    kws = []
    for kw in ['all', 'each', 'highest', 'among', 'share']:
        if kw in words:
            kws.append(kw)
    print(f"  {'✅' if opt['correct'] else '❌'} '{text}' | keywords={kws}")

# Check Q4 specifically
print("\n" + "=" * 60)
print("Q4 details:")
print("=" * 60)
q4 = [q for q in questions if q["id"] == 4][0]
print(f"Q: {q4['text']}")
for opt in q4["options"]:
    text = clean(opt["text"])
    words = set(text.lower().split())
    kws = []
    for kw in ['all', 'each', 'highest', 'among', 'share', 'none']:
        if kw in words:
            kws.append(kw)
    longest = len(text.split()) == max(len(clean(o["text"]).split()) for o in q4["options"])
    print(f"  {'✅' if opt['correct'] else '❌'} '{text}' | keywords={kws} | longest={longest}")
