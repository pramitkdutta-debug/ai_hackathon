from datetime import date
from .parser import parse_note

HIGH_STATUSES = {"blocked", "at risk", "critical", "delayed"}

def _risk_level(score):
    return "High" if score >= 60 else "Medium" if score >= 30 else "Low"

def analyze_portfolio(workspace: dict) -> dict:
    parsed = [parse_note(n) for n in workspace["notes"]]
    risks, dependencies, initiatives = [], [], []
    for item in parsed:
        text = item["text"]
        status = item["status"].lower()
        score, reasons = 0, []
        if status in HIGH_STATUSES:
            score += 45; reasons.append(f"Status is {item['status']}")
        if item["progress_pct"] < 50:
            score += 15; reasons.append("Progress is below 50%")
        if any(word in text.lower() for word in ["blocked", "slippage", "delay", "延期"]):
            score += 20; reasons.append("Blocker or schedule slippage mentioned")
        if any(word in text.lower() for word in ["resource", "capacity", "staffing", "bandwidth"]):
            score += 15; reasons.append("Resource/capacity pressure mentioned")
        score = min(score, 100)
        initiatives.append({
            "initiative": item["initiative"], "business_unit": _business_unit(text),
            "owner": item["owner"], "status": item["status"],
            "progress_pct": item["progress_pct"], "due_date": item["due_date"],
            "risk_level": _risk_level(score), "risk_score": score
        })
        if reasons:
            risks.append({"initiative": item["initiative"], "risk_level": _risk_level(score),
                          "risk_score": score, "signals": "; ".join(reasons),
                          "recommended_response": _response(score)})
        for line in text.splitlines():
            low = line.lower()
            if "depends on" in low or "dependency:" in low or "blocked by" in low:
                dependencies.append({"initiative": item["initiative"], "dependency": line.lstrip("- ").strip(),
                                     "signal": "Dependency / sequencing"})
    kpis = []
    for row in workspace["kpis"]:
        actual, target = float(row["actual"]), float(row["target"])
        # Assumes higher is better. Set direction=lower in CSV to reverse the comparison.
        direction = str(row.get("direction", "higher")).lower()
        on_track = actual <= target if direction == "lower" else actual >= target
        variance = actual - target
        kpis.append({**row, "variance": round(variance, 2),
                     "performance_pct": round((actual / target * 100) if target else 0, 1),
                     "health": "On track" if on_track else "Off track"})
        if not on_track:
            risks.append({"initiative": row["initiative"], "risk_level": "High" if abs(variance) > abs(target)*.15 else "Medium",
                          "risk_score": 70 if abs(variance) > abs(target)*.15 else 40,
                          "signals": f"KPI {row['metric']} is off track ({actual} vs target {target})",
                          "recommended_response": "Confirm root cause, owner, and recovery forecast."})
    return {"initiatives": initiatives, "kpis": kpis, "risks": risks, "dependencies": dependencies,
            "summary": {"initiative_count": len(initiatives),
                        "high_risk_count": sum(1 for r in risks if r["risk_level"] == "High"),
                        "off_track_kpi_count": sum(1 for k in kpis if k["health"] == "Off track")}}

def _business_unit(text):
    import re
    m = re.search(r"^Business unit:\s*(.+)$", text, re.I | re.M)
    return m.group(1).strip() if m else "Unspecified"

def _response(score):
    if score >= 60: return "Escalate to sponsor; agree recovery owner and date."
    if score >= 30: return "Review weekly; resolve the leading blocker."
    return "Maintain current plan and monitor."
