from pathlib import Path
import pandas as pd

REQUIRED_KPI_COLUMNS = {"initiative", "business_unit", "metric", "actual", "target", "unit"}

def load_workspace(folder: Path) -> dict:
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Data folder not found: {folder}")
    notes = []
    csv_files = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in {".md", ".txt"}:
            notes.append({"file": path.name, "text": path.read_text(encoding="utf-8")})
        elif path.suffix.lower() == ".csv":
            csv_files.append(path)
    if not notes:
        raise ValueError("No .md or .txt status notes found.")
    if not csv_files:
        raise ValueError("No KPI .csv file found.")
    frames = [pd.read_csv(p) for p in csv_files]
    kpis = pd.concat(frames, ignore_index=True)
    missing = REQUIRED_KPI_COLUMNS - set(kpis.columns)
    if missing:
        raise ValueError(f"KPI CSV missing required columns: {', '.join(sorted(missing))}")
    for col in ["actual", "target"]:
        kpis[col] = pd.to_numeric(kpis[col], errors="coerce")
    if kpis[["actual", "target"]].isna().any().any():
        raise ValueError("KPI actual and target columns must contain numeric values.")
    return {"notes": notes, "kpis": kpis.to_dict(orient="records")}
