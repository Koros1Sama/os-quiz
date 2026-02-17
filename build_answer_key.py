import json
import re
from collections import defaultdict

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

def get_words(text):
    return re.findall(r'[a-zA-Z]+', text.lower())

output_lines = []

def out(line=""):
    output_lines.append(line)

results = []

for q in questions:
    correct_opt = None
    wrong_opts = []
    for opt in q["options"]:
        cleaned = clean(opt["text"])
        if opt["correct"]:
            correct_opt = cleaned
        else:
            wrong_opts.append(cleaned)
    
    correct_words = get_words(correct_opt)
    all_wrong_text = ' '.join(wrong_opts).lower()
    
    # Find words unique to correct answer
    unique_words = []
    for w in correct_words:
        if w not in all_wrong_text and len(w) >= 2:
            unique_words.append(w)
    
    # If no unique single word, try 2-word combos
    unique_phrase = None
    if unique_words:
        unique_words.sort(key=len)
        unique_phrase = unique_words[0]
    else:
        correct_lower = correct_opt.lower()
        wrong_lower = all_wrong_text.lower()
        words = correct_lower.split()
        for i in range(len(words) - 1):
            phrase = words[i] + ' ' + words[i+1]
            if phrase not in wrong_lower:
                unique_phrase = phrase
                break
    
    if not unique_phrase:
        unique_phrase = None
    
    results.append({
        "id": q["id"],
        "q_text": q["text"],
        "correct": correct_opt,
        "trigger": unique_phrase,
        "unique_words": unique_words
    })

# Count coverage
has_trigger = [r for r in results if r["trigger"]]
no_trigger = [r for r in results if not r["trigger"]]

# Build the markdown file directly
out("# 🎯 مفتاح الاجابة الكامل — 180 سؤال")
out("")
out("> **الطريقة:** لكل سؤال، دور في الخيارات على **الكلمة المفتاحية** المكتوبة بالجدول.")
out("> الخيار اللي فيه هالكلمة = الجواب الصحيح. ترتيب الخيارات ما يأثر.")
out("")
out(f"> تغطية الكلمات المفتاحية: **{len(has_trigger)}/{len(questions)}** سؤال")
out("")

# Group by question ranges
ranges = [(1,30,"Q1-Q30"), (31,60,"Q31-Q60"), (61,90,"Q61-Q90"), 
          (91,120,"Q91-Q120"), (121,150,"Q121-Q150"), (151,180,"Q151-Q180")]

for start, end, label in ranges:
    out(f"## {label}")
    out("")
    out("| # | بداية السؤال | دور على هالكلمة | الجواب الكامل |")
    out("|---|-------------|----------------|--------------|")
    
    for r in results:
        if start <= r["id"] <= end:
            q_short = r["q_text"][:55].replace("|", "/")
            correct_short = r["correct"][:60].replace("|", "/")
            trigger = r["trigger"] if r["trigger"] else "---"
            
            # Add alternative words if available
            alts = ""
            if len(r["unique_words"]) > 1:
                alts = f" ({', '.join(r['unique_words'][1:3])})"
            
            out(f"| {r['id']} | {q_short} | **{trigger}**{alts} | {correct_short} |")
    
    out("")

# Special section for questions with no trigger
if no_trigger:
    out("## ⚠️ اسئلة بدون كلمة مفتاحية فريدة")
    out("")
    out("> هذي الاسئلة كل كلمات الجواب الصحيح موجودة بالخيارات الغلط بعد.")
    out("> لازم تحفظ الجواب الكامل او جزء مميز منه.")
    out("")
    for r in no_trigger:
        out(f"**Q{r['id']}:** {r['q_text']}")
        out(f"- الجواب: **{r['correct']}**")
        out("")

# Shared triggers section
out("---")
out("")
out("## 🔁 كلمات مشتركة (نفس الكلمة = الجواب في اكثر من سؤال)")
out("")

trigger_groups = defaultdict(list)
for r in has_trigger:
    trigger_groups[r["trigger"].lower()].append(r["id"])

shared = [(t, ids) for t, ids in trigger_groups.items() if len(ids) >= 2]
shared.sort(key=lambda x: -len(x[1]))

if shared:
    out("| الكلمة | الاسئلة |")
    out("|--------|--------|")
    for trigger, ids in shared:
        id_str = ", ".join(f"Q{i}" for i in ids)
        out(f"| **{trigger}** | {id_str} |")
else:
    out("لا توجد كلمات مشتركة")

# Write to file
with open("خوارزمية_الاختبار.md", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Done! {len(has_trigger)}/{len(questions)} questions covered with trigger words.")
print(f"{len(no_trigger)} questions need full answer memorization.")
if no_trigger:
    print("Questions without triggers:", [r["id"] for r in no_trigger])
