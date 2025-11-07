#!/usr/bin/env python
"""Diagnostic tool to check WhatsApp chat file format"""
import sys
import os

def diagnose_file(filepath):
    """Analyze a WhatsApp chat file and show its format"""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found!")
        return
    
    print("=" * 70)
    print("WhatsApp Chat File Diagnostic Tool")
    print("=" * 70)
    print(f"\nAnalyzing: {filepath}\n")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"Total lines in file: {len(lines)}\n")
    
    # Show first 10 non-empty lines
    print("First 10 non-empty lines:")
    print("-" * 70)
    shown = 0
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"Line {i}: {line.rstrip()[:80]}")
            shown += 1
            if shown >= 10:
                break
    
    if shown == 0:
        print("No non-empty lines found in file!")
        return
    
    print("\n" + "-" * 70)
    print("\nTesting parser...")
    
    from main import parse_line, analyze
    
    parsed_count = 0
    unparsed_sample = []
    
    for line in lines[:50]:  # Check first 50 lines
        if line.strip():
            result = parse_line(line.strip())
            if result:
                parsed_count += 1
            else:
                if len(unparsed_sample) < 5:
                    unparsed_sample.append(line.strip()[:100])
    
    print(f"Parsed {parsed_count} messages from first 50 lines")
    
    if parsed_count == 0:
        print("\n[WARNING] No messages could be parsed!")
        print("\nUnparsed line samples:")
        for line in unparsed_sample:
            print(f"  - {line}")
        print("\nThis suggests your file format might not be supported.")
        print("Please check that your file is a valid WhatsApp export.")
    else:
        print("\n[OK] Parser can read your file format!")
        print("\nTrying full analysis...")
        try:
            summary = analyze(filepath, top_n=5)
            print(f"\n[SUCCESS] Full analysis completed!")
            print(f"  Total messages: {summary['total_messages']}")
            print(f"  Users found: {list(summary['per_user'].keys())}")
        except Exception as e:
            print(f"\n[ERROR] Analysis failed: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python diagnose_file.py <chat_file.txt>")
        print("\nExample: python diagnose_file.py sample_chat.txt")
    else:
        diagnose_file(sys.argv[1])

