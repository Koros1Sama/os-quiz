import json, re

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

STOP_WORDS = {'the','a','an','is','are','of','in','to','for','and','or','which','what',
              'following','not','does','that','this','it','by','on','from','with','be',
              'how','do','was','has','have','can','will','one','its','used','called',
              'type','system','operating','os','process','when','between','if','all','none',
              'true','false','above','mentioned','these','both','more','most'}

TIER1 = ['circular','unauthorized','wait','pages','switching','than','create','web','allows','among','highest']
TIER2 = ['ready','each','compiling','part','executing']
TRAP_WORDS = ['single','allocates','prevention','prevent','prevents','preventing','prevented',
              'reduce','reduces','reduced','reducing','reduction','macos','segmentation','deadlocks','speed','manager']

def clean(text):
    return re.sub(r'^[a-d]\)\s*', '', text.strip())

def get_words(text):
    return set(re.findall(r'[a-zA-Z]+', text.lower()))

# Part 1: Check ALL questions where the algorithm picks an answer containing "memory"
# Is "memory" in the chosen answer always wrong?

print("=" * 70)
print("🔍 تحليل: هل memory دايماً غلط بالخيار المختار؟")
print("=" * 70)

# For each question, check if any option has "memory" and if it's correct
memory_in_correct = 0
memory_in_wrong = 0
memory_details = []

for q in questions:
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    for text, correct in opts:
        if 'memory' in text.lower().split():
            if correct:
                memory_in_correct += 1
                memory_details.append((q['id'], text[:60], '✅ صح'))
            else:
                memory_in_wrong += 1
                memory_details.append((q['id'], text[:60], '❌ غلط'))

total_memory = memory_in_correct + memory_in_wrong
print(f"\n📊 خيارات فيها كلمة 'memory':")
print(f"  المجموع: {total_memory}")
print(f"  ✅ الخيار صح: {memory_in_correct}/{total_memory} = {memory_in_correct*100//total_memory}%")
print(f"  ❌ الخيار غلط: {memory_in_wrong}/{total_memory} = {memory_in_wrong*100//total_memory}%")

print(f"\n--- التفاصيل ---")
for qid, text, result in sorted(memory_details, key=lambda x: x[0]):
    print(f"  Q{qid} {result}: {text}")

# Part 2: Now check specifically: in the 68 UNSOLVABLE questions,
# if the algorithm's CHOSEN answer has "memory", is it always wrong?
UNSOLVABLE = {2,4,10,11,13,14,16,21,27,30,32,34,36,39,42,43,44,46,48,49,50,51,54,55,56,58,59,61,62,63,64,66,68,74,84,88,90,95,96,97,101,103,105,106,107,110,111,116,117,123,124,126,127,128,132,133,135,140,141,147,148,150,155,157,162,169,174,176}

print(f"\n{'='*70}")
print("🔍 بالـ 68 سؤال اللي الخوارزمية غلطت فيها:")
print(f"{'='*70}")

for q in questions:
    if q['id'] not in UNSOLVABLE:
        continue
    opts = [(clean(o["text"]), o["correct"]) for o in q["options"]]
    correct_text = next(t for t, c in opts if c)
    wrong_texts = [t for t, c in opts if not c]
    
    # Check if correct answer has memory
    correct_has_memory = 'memory' in correct_text.lower().split()
    # Check if any wrong answer has memory
    wrong_with_memory = [t for t in wrong_texts if 'memory' in t.lower().split()]
    
    if correct_has_memory or wrong_with_memory:
        print(f"\n  Q{q['id']}: {q['text'][:60]}")
        if correct_has_memory:
            print(f"    ✅ الصح فيه memory: {correct_text[:50]}")
        for t in wrong_with_memory:
            print(f"    ❌ غلط فيه memory: {t[:50]}")

# Part 3: Check "memory" as a TRAP word candidate
# When "memory" appears as an option, how often is it WRONG?
print(f"\n{'='*70}")
print("🔍 هل نضيف memory كـ trap word؟")
print(f"{'='*70}")
print(f"\n  memory بالخيار:")
print(f"    صح: {memory_in_correct} مرة")
print(f"    غلط: {memory_in_wrong} مرة")
print(f"    نسبة الغلط: {memory_in_wrong*100//total_memory}%")
if memory_in_wrong * 100 // total_memory >= 70:
    print(f"    ⚠️ نعم! memory غلط {memory_in_wrong*100//total_memory}% → ممكن نعتبرها trap word")
else:
    print(f"    ❌ لا، memory صح {memory_in_correct*100//total_memory}% — مو trap word")
