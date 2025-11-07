#!/usr/bin/env python
"""Quick test script to check if parsing works"""
from main import parse_line, analyze

# Test with sample file
print("Testing parser with sample_chat.txt...")
try:
    summary = analyze('sample_chat.txt', top_n=10)
    print(f"\n[OK] Success! Parsed {summary['total_messages']} messages")
    print(f"Users: {list(summary['per_user'].keys())}")
    print(f"Top words: {summary['top_words'][:5]}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

# Test individual line parsing
print("\n" + "="*60)
print("Testing individual line parsing...")
test_lines = [
    "12/09/2025, 21:02 - Alice: Hey! How are you?",
    "12/09/2025, 21:03 - Bob: I'm fine, thanks! :)",
    "[12/09/2025, 9:02 PM] Alice: iOS format test",
    "12-09-2025 21:02 Name: Alternative format",
]

for line in test_lines:
    result = parse_line(line)
    if result:
        dt, author, msg = result
        print(f"[OK] Parsed: {line[:50]}...")
        print(f"  -> Date: {dt}, Author: {author}, Message: {msg[:30]}...")
    else:
        print(f"[FAIL] Failed: {line}")

