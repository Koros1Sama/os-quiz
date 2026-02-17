import json

with open("questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("questions_data.js", "w", encoding="utf-8") as f:
    f.write("const QUESTIONS_DATA = ")
    json.dump(data, f, ensure_ascii=True)
    f.write(";")

print(f"Done! Created questions_data.js with {len(data)} questions")
