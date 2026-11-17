import re

def extract_action_items(notes: list) -> list:
    actions = []
    for note in notes:
        initiative_match = re.search(r"^Initiative:\s*(.+)$", note["text"], re.I | re.M)
        initiative = initiative_match.group(1).strip() if initiative_match else note["file"]
        for line in note["text"].splitlines():
            clean = line.strip().lstrip("-* ").strip()
            if re.match(r"^(action|next step|decision needed)\s*:", clean, re.I):
                body = clean.split(":", 1)[1].strip()
                owner = re.search(r"\bowner\s*=\s*([^;,]+)", body, re.I)
                due = re.search(r"\b(?:due|by)\s*=\s*([^;,]+)", body, re.I)
                escalation = re.search(r"\b(escalate|escalation)\b", body, re.I)
                actions.append({
                    "initiative": initiative, "action": body,
                    "owner": owner.group(1).strip() if owner else "Unassigned",
                    "deadline": due.group(1).strip() if due else "Not specified",
                    "escalation_required": "Yes" if escalation else "No",
                    "source_file": note["file"]
                })
    return actions
