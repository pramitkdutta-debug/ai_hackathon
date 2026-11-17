from pathlib import Path
import streamlit as st
import pandas as pd

from src.loader import load_workspace
from src.analyzer import analyze_portfolio
from src.memo import generate_executive_memo
from src.actions import extract_action_items
from src.reporting import build_downloads

st.set_page_config(page_title="Initiative-to-Decision Copilot", page_icon="🧭", layout="wide")
st.title("🧭 Initiative-to-Decision Executive Brief Synthesizer")
st.caption("Turn weekly initiative notes and KPI trackers into decision-ready leadership briefs.")

with st.sidebar:
    st.header("Workspace")
    data_dir = st.text_input("Sample / local data folder", value="data/sample")
    st.markdown("---")
    st.subheader("Optional AI narrative")
    use_llm = st.checkbox("Use OpenAI for memo narrative", value=False)
    model = st.text_input("Model", value="gpt-4.1-mini", disabled=not use_llm)
    st.caption("Without an API key, the app uses a deterministic memo template. Risk scoring always remains rules-based.")

st.info("Upload .md/.txt status notes and one KPI CSV, or use the included sample workspace.")
uploads = st.file_uploader("Add status notes (.md, .txt) and KPI CSV", type=["md", "txt", "csv"], accept_multiple_files=True)

if st.button("Analyze workspace", type="primary"):
    try:
        if uploads:
            temp = Path(".runtime_uploads")
            temp.mkdir(exist_ok=True)
            for p in temp.iterdir():
                if p.is_file():
                    p.unlink()
            for f in uploads:
                (temp / f.name).write_bytes(f.getvalue())
            workspace = load_workspace(temp)
        else:
            workspace = load_workspace(Path(data_dir))

        st.session_state["workspace"] = workspace
        st.session_state["analysis"] = analyze_portfolio(workspace)
        st.success(f"Loaded {len(workspace['notes'])} notes and {len(workspace['kpis'])} KPI rows.")
    except Exception as exc:
        st.error(f"Could not analyze workspace: {exc}")

if "analysis" in st.session_state:
    workspace = st.session_state["workspace"]
    result = st.session_state["analysis"]
    summary = result["summary"]
    a, b, c, d = st.columns(4)
    a.metric("Initiatives", summary["initiative_count"])
    b.metric("High risks", summary["high_risk_count"])
    c.metric("Off-track KPIs", summary["off_track_kpi_count"])
    d.metric("Open actions", len(extract_action_items(workspace["notes"])))

    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio overview", "Risk & dependencies", "Executive memo", "Action items"])
    with tab1:
        st.subheader("Initiative health")
        if result["initiatives"]:
            st.dataframe(pd.DataFrame(result["initiatives"]), use_container_width=True, hide_index=True)
        st.subheader("KPI performance")
        st.dataframe(pd.DataFrame(result["kpis"]), use_container_width=True, hide_index=True)
    with tab2:
        st.subheader("Risk register")
        st.dataframe(pd.DataFrame(result["risks"]), use_container_width=True, hide_index=True)
        st.subheader("Dependency signals")
        st.dataframe(pd.DataFrame(result["dependencies"]), use_container_width=True, hide_index=True)
    with tab3:
        st.subheader("Decision-ready brief")
        if st.button("Generate executive memo"):
            memo = generate_executive_memo(workspace, result, use_llm=use_llm, model=model)
            st.session_state["memo"] = memo
        if "memo" in st.session_state:
            st.markdown(st.session_state["memo"])
            st.download_button("Download memo (.md)", st.session_state["memo"], file_name="executive_decision_brief.md")
    with tab4:
        actions = extract_action_items(workspace["notes"])
        action_df = pd.DataFrame(actions)
        st.dataframe(action_df, use_container_width=True, hide_index=True)
        st.download_button("Download actions (.csv)", action_df.to_csv(index=False), file_name="action_items.csv")
    downloads = build_downloads(result, extract_action_items(workspace["notes"]))
    st.download_button("Download full analysis (.json)", json.dumps(downloads, indent=2), file_name="portfolio_analysis.json")
else:
    st.markdown("### Quick start")
    st.markdown("1. Keep the sample files in `data/sample/` or upload your own files.\n2. Click **Analyze workspace**.\n3. Review risks, generate the executive memo, and export action items.")
