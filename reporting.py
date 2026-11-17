def build_downloads(analysis, actions):
    return {"summary": analysis["summary"], "initiatives": analysis["initiatives"],
            "kpis": analysis["kpis"], "risks": analysis["risks"],
            "dependencies": analysis["dependencies"], "actions": actions}
