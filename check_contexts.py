import json

data = json.load(open('funny_test_data.json'))
tasks = data['TASK']
print("Tasks and their CONTEXT IDs:")
for t in tasks:
    print(f"  Task: {t['TITLE'][:50]:50} | CONTEXT: {t['CONTEXT']}")

