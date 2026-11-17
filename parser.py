import re

def parse_note(note: dict) -> dict:
    text = note["text"]
    def field(pattern, default="Unknown"):
        match = re.search(pattern, text, re.I | re.M)
        return match.group(1).strip() if match else default
    title = field(r"^#\s*(.+)$", note["file"])
    initiative = field(r"^Initiative:\s*(.+)$", title)
    owner = field(r"^Owner:\s*(.+)$")
    status = field(r"^Status:\s*(.+)$")
    progress = field(r"^Progress:\s*(\d+)%", "0")
    due = field(r"^(?:Target date|Due date):\s*(.+)$")
    return {
        "file": note["file"], "title": title, "initiative": initiative,
        "owner": owner, "status": status, "progress_pct": int(progress),
        "due_date": due, "text": text
    }
