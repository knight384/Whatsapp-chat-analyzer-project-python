# WhatsApp Chat Analyzer - main.py
import re
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import csv
import os
try:
    from dateutil import parser as dtparser
except Exception:
    dtparser = None

# OCR support for image processing
try:
    from PIL import Image
    import pytesseract
    import os
    
    # Try to auto-detect Tesseract on Windows if not in PATH
    if os.name == 'nt':  # Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Tesseract-OCR\tesseract.exe',
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    # Test if Tesseract is available
    try:
        pytesseract.get_tesseract_version()
        OCR_AVAILABLE = True
    except Exception:
        OCR_AVAILABLE = False
except Exception:
    OCR_AVAILABLE = False

# Multiple regex patterns for different WhatsApp formats
TIMESTAMP_PATTERNS = [
    # Android format with am/pm (lowercase): dd/mm/yyyy, h:mm am/pm - Name: Message
    re.compile(r'^(?P<date>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}),\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm|AM|PM))\s*[-\u2013\u2014]\s+(?P<rest>.*)$', re.IGNORECASE),
    # Android format: dd/mm/yyyy, hh:mm - Name: Message
    re.compile(r'^(?P<date>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s*[-\u2013\u2014]\s+(?P<rest>.*)$'),
    # iOS format: [dd/mm/yyyy, hh:mm:ss AM/PM] Name: Message
    re.compile(r'^\[(?P<date>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\]?\s*(?P<rest>.*)$', re.IGNORECASE),
    # Alternative format: mm/dd/yyyy, hh:mm - Name: Message
    re.compile(r'^(?P<date>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s*[-\u2013\u2014]\s+(?P<rest>.*)$'),
    # Format without separator: dd/mm/yyyy hh:mm Name: Message
    re.compile(r'^(?P<date>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s+(?P<rest>.*)$'),
    # Format with dots: dd.mm.yyyy, hh:mm - Name: Message
    re.compile(r'^(?P<date>\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s*[-\u2013\u2014]\s+(?P<rest>.*)$'),
]

def parse_line(line):
    """Attempts to parse a line and return (datetime, author, message) or None"""
    # Try each pattern
    for pattern in TIMESTAMP_PATTERNS:
        m = pattern.match(line)
        if m:
            date = m.group('date')
            time = m.group('time').strip()
            rest = m.group('rest').strip()
            
            # Skip if rest is empty
            if not rest:
                continue
                
            # Split author and message
            # Look for ": " but handle cases where colon might be in message
            # WhatsApp format is typically "Name: Message" or system messages without author
            # System messages usually don't have ": " separator
            if ': ' in rest:
                parts = rest.split(': ', 1)
                author = parts[0].strip()
                message = parts[1].strip() if len(parts) > 1 else ""
                # If author looks like a system message (very long or contains special patterns), treat as no author
                if len(author) > 100 or author.startswith('Messages and calls') or author.startswith('You '):
                    author = None
                    message = rest
            else:
                # No author found, might be system message
                author = None
                message = rest
            
            # Parse datetime with multiple format attempts
            dt = None
            
            # Clean up time (remove AM/PM if present for parsing)
            time_upper = time.upper()
            time_clean = re.sub(r'\s*(AM|PM)\s*', '', time, flags=re.IGNORECASE).strip()
            is_pm = 'PM' in time_upper
            is_am = 'AM' in time_upper
            
            if dtparser:
                try:
                    # Try parsing with dayfirst (dd/mm/yyyy format)
                    dt = dtparser.parse(f"{date} {time_clean}", dayfirst=True)
                    # Convert to 24-hour format if needed
                    if is_pm and dt.hour < 12:
                        dt = dt.replace(hour=dt.hour + 12)
                    elif is_am and dt.hour == 12:
                        dt = dt.replace(hour=0)
                except Exception:
                    try:
                        # Try without dayfirst (mm/dd/yyyy format)
                        dt = dtparser.parse(f"{date} {time_clean}")
                        if is_pm and dt.hour < 12:
                            dt = dt.replace(hour=dt.hour + 12)
                        elif is_am and dt.hour == 12:
                            dt = dt.replace(hour=0)
                    except Exception:
                        dt = None
            else:
                # Best-effort parse with multiple formats
                date_formats = [
                    ("%d/%m/%Y", "%H:%M"),
                    ("%d/%m/%y", "%H:%M"),
                    ("%d-%m-%Y", "%H:%M"),
                    ("%d-%m-%y", "%H:%M"),
                    ("%m/%d/%Y", "%H:%M"),
                    ("%m/%d/%y", "%H:%M"),
                    ("%Y-%m-%d", "%H:%M"),
                    ("%d.%m.%Y", "%H:%M"),
                    ("%d.%m.%y", "%H:%M"),
                ]
                
                for date_fmt, time_fmt in date_formats:
                    try:
                        time_part = time_clean
                        if ':' in time_part:
                            if time_part.count(':') == 1:
                                dt = datetime.strptime(f"{date} {time_part}", f"{date_fmt} {time_fmt}")
                            else:
                                # Has seconds
                                dt = datetime.strptime(f"{date} {time_part}", f"{date_fmt} %H:%M:%S")
                        
                        if dt:
                            # Convert to 24-hour format if needed
                            if is_pm and dt.hour < 12:
                                dt = dt.replace(hour=dt.hour + 12)
                            elif is_am and dt.hour == 12:
                                dt = dt.replace(hour=0)
                            break
                    except Exception:
                        continue
            
            return dt, author, message
    
    return None

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        raise Exception("OCR libraries not available. Please install: pip install Pillow pytesseract. Also install Tesseract OCR from https://github.com/tesseract-ocr/tesseract")
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        if not text or len(text.strip()) < 10:
            raise Exception("Could not extract sufficient text from image. Please ensure the image is clear and contains readable WhatsApp chat text.")
        return text
    except Exception as e:
        error_msg = str(e).lower()
        if "tesseract" in error_msg and ("not found" in error_msg or "no such file" in error_msg):
            raise Exception("Tesseract OCR not found. Please install Tesseract OCR from https://github.com/tesseract-ocr/tesseract and ensure it's in your system PATH.")
        elif "tesseract" in error_msg:
            raise Exception(f"OCR error: {str(e)}. Please ensure Tesseract OCR is installed and configured correctly.")
        else:
            raise Exception(f"Failed to process image: {str(e)}")

def analyze(filepath, top_n=20, is_image=False):
    total = 0
    per_user = Counter()
    per_day = Counter()
    per_hour = Counter()
    per_weekday = Counter()
    word_counts = Counter()
    media_count = 0
    emoji_count = 0
    link_count = 0
    question_count = 0
    longest_message = ""
    longest_message_length = 0
    message_lengths = []
    first_date = None
    last_date = None
    active_periods = defaultdict(int)  # Morning, Afternoon, Evening, Night

    # Extended stopwords list
    stopwords = set(["the","and","to","a","of","in","is","it","you","i","for","on","that","this","with","are","was","as","but","be","have","has","not","we","they","what","when","where","who","why","how","can","will","would","should","could","may","might","must","shall"])

    # Process file or image
    if is_image:
        try:
            text = extract_text_from_image(filepath)
            lines = text.split('\n')
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

    # Track current message for multi-line messages
    current_message_parts = []
    current_author = None
    current_dt = None
    unparsed_lines = []
    
    def process_message(dt, author, message):
        """Process a complete message"""
        nonlocal total, per_user, per_day, per_hour, per_weekday
        nonlocal word_counts, media_count, emoji_count, link_count, question_count
        nonlocal longest_message, longest_message_length, message_lengths
        nonlocal first_date, last_date, active_periods
        
        total += 1
        if author:
            per_user[author] += 1
        if dt:
            date_str = dt.date().isoformat()
            per_day[date_str] += 1
            per_hour[dt.hour] += 1
            per_weekday[dt.strftime('%A')] += 1
            
            # Track date range
            if first_date is None or dt.date() < first_date:
                first_date = dt.date()
            if last_date is None or dt.date() > last_date:
                last_date = dt.date()
            
            # Categorize by time of day
            hour = dt.hour
            if 5 <= hour < 12:
                active_periods['Morning'] += 1
            elif 12 <= hour < 17:
                active_periods['Afternoon'] += 1
            elif 17 <= hour < 22:
                active_periods['Evening'] += 1
            else:
                active_periods['Night'] += 1
        
        msg_lower = message.lower()
        msg_length = len(message)
        message_lengths.append(msg_length)
        
        # Track longest message
        if msg_length > longest_message_length:
            longest_message_length = msg_length
            longest_message = message[:100] + "..." if len(message) > 100 else message
        
        # Media detection
        if '<media omitted>' in msg_lower or 'media omitted' in msg_lower or '<image omitted>' in msg_lower or 'image omitted' in msg_lower:
            media_count += 1
        
        # Link detection
        if 'http://' in msg_lower or 'https://' in msg_lower or 'www.' in msg_lower:
            link_count += 1
        
        # Question detection
        if '?' in message:
            question_count += 1
        
        # Emoji detection
        emoji_count += sum(1 for ch in message if ord(ch) > 1000)
        
        # Word analysis
        words = re.findall(r"\b\w+\b", msg_lower)
        for w in words:
            if w and w not in stopwords and len(w) > 1:
                word_counts[w] += 1
    
    for raw in lines:
        line = raw.rstrip()  # Keep right whitespace, remove trailing newline
        if not line.strip():
            # Empty line - finish current message if any
            if current_message_parts:
                message = ' '.join(current_message_parts)
                process_message(current_dt, current_author, message)
                current_message_parts = []
                current_author = None
                current_dt = None
            continue
            
        parsed = parse_line(line)
        if parsed is None:
            # This line doesn't have a timestamp
            # It might be a continuation of the previous message
            if current_message_parts:
                # Append to current message
                current_message_parts.append(line.strip())
                continue
            else:
                # First unparsed line - might be a format we don't recognize
                unparsed_lines.append(line)
                continue
        
        # We have a new message line - process previous message first
        if current_message_parts:
            message = ' '.join(current_message_parts)
            process_message(current_dt, current_author, message)
            current_message_parts = []
        
        # Start new message
        dt, author, message = parsed
        current_dt = dt
        current_author = author
        current_message_parts = [message] if message else []
    
    # Don't forget the last message
    if current_message_parts:
        message = ' '.join(current_message_parts)
        process_message(current_dt, current_author, message)

    # If no messages were parsed, provide helpful error
    if total == 0:
        error_lines_sample = '\n'.join(unparsed_lines[:5]) if unparsed_lines else "No lines found"
        raise Exception(
            f"No messages could be parsed from the file. This might be due to:\n"
            f"1. Unsupported WhatsApp export format\n"
            f"2. File encoding issues\n"
            f"3. Empty or invalid file\n\n"
            f"First few unparsed lines:\n{error_lines_sample}\n\n"
            f"Please ensure your file is a valid WhatsApp export (.txt) with format like:\n"
            f"dd/mm/yyyy, hh:mm - Name: Message"
        )
    
    # Calculate statistics
    avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    total_days = (last_date - first_date).days + 1 if first_date and last_date else 1
    messages_per_day_avg = total / total_days if total_days > 0 else 0
    
    # Determine most active user
    most_active_user = per_user.most_common(1)[0] if per_user else (None, 0)
    
    # Calculate user participation percentage
    user_percentages = {}
    if total > 0:
        for user, count in per_user.items():
            user_percentages[user] = (count / total) * 100
    
    # Determine most active time period
    most_active_period = max(active_periods.items(), key=lambda x: x[1]) if active_periods else (None, 0)
    
    # Determine most active day of week
    most_active_day = max(per_weekday.items(), key=lambda x: x[1]) if per_weekday else (None, 0)
    
    # Generate insights
    insights = []
    if total > 0:
        insights.append(f"📊 Analyzed {total:,} messages across {total_days} days")
        insights.append(f"💬 Average of {messages_per_day_avg:.1f} messages per day")
        if most_active_user[0]:
            insights.append(f"🏆 {most_active_user[0]} is the most active with {most_active_user[1]:,} messages ({user_percentages.get(most_active_user[0], 0):.1f}%)")
        if most_active_period[0]:
            insights.append(f"⏰ Most active time: {most_active_period[0]} ({most_active_period[1]:,} messages)")
        if most_active_day[0]:
            insights.append(f"📅 Most active day: {most_active_day[0]} ({most_active_day[1]:,} messages)")
        if media_count > 0:
            insights.append(f"🖼️ {media_count:,} media files shared")
        if link_count > 0:
            insights.append(f"🔗 {link_count:,} links shared")
        if question_count > 0:
            insights.append(f"❓ {question_count:,} questions asked")
        if emoji_count > 0:
            insights.append(f"😊 {emoji_count:,} emojis used (approx)")
        insights.append(f"📝 Average message length: {avg_message_length:.0f} characters")

    summary = {
        'total_messages': total,
        'per_user': per_user,
        'per_day': per_day,
        'per_hour': per_hour,
        'per_weekday': per_weekday,
        'top_words': word_counts.most_common(top_n),
        'media_count': media_count,
        'emoji_count': emoji_count,
        'link_count': link_count,
        'question_count': question_count,
        'avg_message_length': round(avg_message_length, 1),
        'longest_message': longest_message,
        'longest_message_length': longest_message_length,
        'first_date': first_date.isoformat() if first_date else None,
        'last_date': last_date.isoformat() if last_date else None,
        'total_days': total_days,
        'messages_per_day_avg': round(messages_per_day_avg, 2),
        'user_percentages': user_percentages,
        'active_periods': dict(active_periods),
        'most_active_user': most_active_user[0] if most_active_user[0] else None,
        'most_active_period': most_active_period[0] if most_active_period[0] else None,
        'most_active_day': most_active_day[0] if most_active_day[0] else None,
        'insights': insights
    }
    return summary

def export_csv(summary, outpath):
    # Export comprehensive data to CSV
    with open(outpath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['metric','key','value'])
        writer.writerow(['total_messages','','%d' % summary['total_messages']])
        writer.writerow(['media_count','','%d' % summary['media_count']])
        writer.writerow(['emoji_count','','%d' % summary['emoji_count']])
        writer.writerow(['link_count','','%d' % summary.get('link_count', 0)])
        writer.writerow(['question_count','','%d' % summary.get('question_count', 0)])
        writer.writerow(['avg_message_length','','%.1f' % summary.get('avg_message_length', 0)])
        if summary.get('first_date'):
            writer.writerow(['first_date','',summary['first_date']])
        if summary.get('last_date'):
            writer.writerow(['last_date','',summary['last_date']])
        writer.writerow(['total_days','','%d' % summary.get('total_days', 0)])
        writer.writerow(['messages_per_day_avg','','%.2f' % summary.get('messages_per_day_avg', 0)])
        writer.writerow([])
        writer.writerow(['per_user','user','count','percentage'])
        for user, cnt in summary['per_user'].most_common():
            pct = summary.get('user_percentages', {}).get(user, 0)
            writer.writerow(['per_user', user, cnt, '%.2f' % pct])
        writer.writerow([])
        writer.writerow(['top_words','word','count'])
        for word, cnt in summary['top_words']:
            writer.writerow(['top_words', word, cnt])

def export_html(summary, outpath):
    # Very small HTML report
    html = []
    html.append('<!doctype html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('<meta charset="utf-8">')
    html.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    html.append('<title>WhatsApp Chat Analysis</title>')
    html.append('<style>body{font-family:Segoe UI,Roboto,Arial;margin:20px;background:#f7f7f7;color:#111}h1{color:#0b5}table{border-collapse:collapse;margin-top:10px;width:100%;max-width:800px}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#eee}</style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<h1>WhatsApp Chat Analysis</h1>')
    html.append(f'<p><strong>Total messages:</strong> {summary["total_messages"]}</p>')
    html.append(f'<p><strong>Media messages:</strong> {summary["media_count"]}</p>')
    html.append(f'<p><strong>Emoji count (approx):</strong> {summary["emoji_count"]}</p>')

    html.append('<h2>Messages per user</h2>')
    html.append('<table>')
    html.append('<tr><th>User</th><th>Count</th></tr>')
    for user, cnt in summary['per_user'].most_common():
        html.append(f'<tr><td>{user}</td><td>{cnt}</td></tr>')
    html.append('</table>')

    html.append('<h2>Top words</h2>')
    html.append('<table>')
    html.append('<tr><th>Word</th><th>Count</th></tr>')
    for word, cnt in summary['top_words']:
        html.append(f'<tr><td>{word}</td><td>{cnt}</td></tr>')
    html.append('</table>')

    html.append('</body></html>')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))

def main():
    parser = argparse.ArgumentParser(description='WhatsApp Chat Analyzer')
    parser.add_argument('--file', '-f', required=True, help='Path to exported chat .txt file')
    parser.add_argument('--top', type=int, default=20, help='Top N words')
    parser.add_argument('--export', help='Export summary CSV path')
    parser.add_argument('--export-html', help='Export summary HTML path')
    args = parser.parse_args()
    summary = analyze(args.file, top_n=args.top)
    print('\n=== Summary ===')
    print('Total messages:', summary['total_messages'])
    print('Media messages:', summary['media_count'])
    print('Emoji count (approx):', summary['emoji_count'])
    print('\nMessages per user:')
    for user, cnt in summary['per_user'].most_common():
        print(f'  {user}: {cnt}')
    print('\nTop words:')
    for w, cnt in summary['top_words']:
        print(f'  {w}: {cnt}')
    if args.export:
        export_csv(summary, args.export)
        print('\nExported summary to', args.export)
    if getattr(args, 'export_html', None):
        export_html(summary, args.export_html)
        print('\nExported HTML report to', args.export_html)

if __name__ == '__main__':
    main()
