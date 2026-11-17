from src.loader import load_workspace
from src.analyzer import analyze_portfolio
from src.actions import extract_action_items
from pathlib import Path

def test_sample_workspace_loads():
    workspace = load_workspace(Path("data/sample"))
    assert len(workspace["notes"]) >= 5
    assert len(workspace["kpis"]) >= 5

def test_analysis_returns_expected_sections():
    workspace = load_workspace(Path("data/sample"))
    result = analyze_portfolio(workspace)
    assert {"summary", "risks", "kpis", "dependencies", "initiatives"} <= set(result)
    assert result["summary"]["initiative_count"] >= 5

def test_action_extraction():
    workspace = load_workspace(Path("data/sample"))
    actions = extract_action_items(workspace["notes"])
    assert len(actions) >= 1
    assert "owner" in actions[0]
