import os

def generate_executive_memo(workspace: dict, analysis: dict, use_llm=False, model="gpt-4.1-mini") -> str:
    if use_llm and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = _prompt(analysis)
            response = client.responses.create(model=model, input=prompt)
            return response.output_text
        except Exception as exc:
            fallback = _template(analysis)
            return fallback + f"\n\n> AI narrative unavailable; deterministic template used ({type(exc).__name__})."
    return _template(analysis)

def _prompt(data):
    return ("Write a concise executive decision memo using only the supplied facts. "
            "Include executive summary, decisions requested, options and trade-offs, "
            "recommendation, risks, actions, and assumptions. Do not invent facts.\n\n"
            + str(data))

def _template(data):
    risks = data["risks"]
    high = [r for r in risks if r["risk_level"] == "High"]
    off = [k for k in data["kpis"] if k["health"] == "Off track"]
    lines = [
        "# Executive Decision Brief",
        "",
        f"**Portfolio scope:** {data['summary']['initiative_count']} initiatives | "
        f"{len(data['kpis'])} KPI observations | {len(risks)} risk signals",
        "",
        "## Executive summary",
        f"There are {len(high)} high-severity risk signals and {len(off)} off-track KPI observations. "
        "Leadership attention should focus on the items below and confirm accountable recovery plans.",
        "",
        "## Decisions requested",
        "1. Confirm executive sponsor and recovery owner for each high-severity item.",
        "2. Approve or reject any capacity reallocation after validating impact on committed milestones.",
        "3. Confirm whether off-track KPI targets remain valid or require a formally approved reset.",
        "",
        "## Strategic options and trade-offs",
        "- **Option A — Protect current scope:** preserve commitments; accept schedule or KPI exposure if blockers persist.",
        "- **Option B — Reallocate capacity:** improve critical-path delivery; may slow lower-priority work.",
        "- **Option C — Re-sequence scope:** protect the most valuable outcomes; may defer secondary deliverables.",
        "",
        "## Recommended actions",
        "Prioritize sponsor-led recovery for high-severity risks, validate dependencies, and assign dated actions. "
        "Do not change baseline targets without an explicit decision.",
        "",
        "## Risk and KPI watchlist"
    ]
    if risks:
        for r in risks:
            lines.append(f"- **{r['risk_level']} — {r['initiative']}:** {r['signals']} Recommended: {r['recommended_response']}")
    else:
        lines.append("- No rule-based risk signals detected from the supplied notes and KPI data.")
    lines += ["", "## Off-track KPIs"]
    if off:
        for k in off:
            lines.append(f"- {k['initiative']} / {k['metric']}: actual {k['actual']} vs target {k['target']} {k['unit']}.")
    else:
        lines.append("- None detected.")
    lines += ["", "## Assumptions and limitations",
              "- Risk flags are heuristic indicators, not a substitute for owner validation.",
              "- KPI direction defaults to higher-is-better; use a `direction` column with `lower` for lower-is-better metrics.",
              "- Dates and owners are extracted from note text; ambiguous entries require human review."]
    return "\n".join(lines)
