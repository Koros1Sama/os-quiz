#!/usr/bin/env python3
"""Parse QuestionsBank.txt into structured JSON"""
import re, json, os

def parse_questions(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned = []
    skip_strings = ['الجمهورية اليمنية', 'جامعة صنعاء', 'مركز الاختبارات الالكترونية', 
                     'قائمة الاسئلة', 'Powered by TCPDF']
    
    for line in lines:
        line = line.strip('\r\n').strip()
        if not line:
            continue
        if any(s in line for s in skip_strings):
            continue
        if re.match(r'^\s*الصفحة\s+\d+\s*/\s*\d+', line):
            continue
        if 'نظم تشغيل' in line:
            continue
        if line.startswith('د مالك'):
            continue
        cleaned.append(line)
    
    # Handle merged lines (like Q4 options merged)
    expanded = []
    for line in cleaned:
        # Check for merged option pattern: "1) - text2) - text"
        parts = re.split(r'(?<=\S)(\d\)\s*[+-])', line)
        if len(parts) > 1:
            current = parts[0]
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    expanded.append(current.strip())
                    current = parts[i] + parts[i+1]
                else:
                    current += parts[i]
            if current.strip():
                expanded.append(current.strip())
        else:
            expanded.append(line)
    
    questions = []
    current_q = None
    i = 0
    
    while i < len(expanded):
        line = expanded[i]
        m = re.match(r'^(\d+)\)\s*(.*)', line)
        
        if m:
            num = int(m.group(1))
            rest = m.group(2).strip()
            
            # Determine if option (starts with + or -) or question
            is_option = bool(re.match(r'^[+-]', rest))
            
            # Also check: if rest starts with "?" it's a question
            if rest.startswith('?'):
                is_option = False
                rest = rest.lstrip('? ').strip()
            
            if is_option and current_q and num <= 4:
                correct = rest[0] == '+'
                text = rest[1:].strip()
                current_q['options'].append({
                    'text': text,
                    'correct': correct
                })
            else:
                # New question
                if current_q:
                    questions.append(current_q)
                
                # Check for multi-line question text
                q_text = rest
                while i + 1 < len(expanded):
                    next_line = expanded[i + 1]
                    next_m = re.match(r'^(\d+)\)\s*', next_line)
                    if next_m:
                        break
                    q_text += ' ' + next_line
                    i += 1
                
                current_q = {
                    'id': num,
                    'text': q_text,
                    'options': []
                }
        i += 1
    
    if current_q:
        questions.append(current_q)
    
    return questions

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, 'QuestionsBank.txt')
    questions = parse_questions(filepath)
    
    print(f"Parsed {len(questions)} questions")
    for q in questions:
        opts = len(q['options'])
        correct = sum(1 for o in q['options'] if o['correct'])
        if opts < 2 or correct != 1:
            print(f"  WARNING Q{q['id']}: {opts} options, {correct} correct")
    
    output = os.path.join(script_dir, 'questions.json')
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output}")
