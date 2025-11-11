import re

SKIP_PATTERNS = [
    r'^Subject:', r'^Course\s*Code', r'^Program:', r'^Topic:',
    r'^Example:', r'^Used\s+in\s+the\s+form', r'^Ethyl\s+fluid',
    r'^QUESTION\s+FOR\s+PRACTICE', r'^THANK\s+YOU', r'^[A-Z]\s*\+',
]

def extract_topics(text):
    """Extract clean, concise topic lines from syllabus text."""
    topics = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if any(re.match(pat, line, re.IGNORECASE) for pat in SKIP_PATTERNS):
            continue

        if any(ch in line for ch in ['=', '•', '(', ')', '%', '–', '𝐻', '𝑂', '2']):
            continue

        words = line.split()
        if not (2 <= len(words) <= 7):
            continue

        if not line[0].isupper() or line[0].isdigit():
            continue

        clean_line = line.rstrip(':').strip()
        if clean_line not in topics:
            topics.append(clean_line)

    return topics
