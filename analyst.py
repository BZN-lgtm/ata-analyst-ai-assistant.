"""Data analysis core: load a spreadsheet, profile it, surface insights."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class Analysis:
    name: str
    rows: int
    cols: int
    numeric: list[str]
    categorical: list[str]
    missing: dict[str, int]
    stats: pd.DataFrame
    insights: list[str] = field(default_factory=list)
    df: pd.DataFrame | None = None


def load(path: str | Path, sheet: str | int = 0) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(p, sheet_name=sheet)
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if "docs.google.com/spreadsheets" in str(path):
        # public/link-shared Google Sheet -> CSV export URL
        sid = str(path).split("/d/")[1].split("/")[0]
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv")
    raise ValueError(f"Unsupported file: {path}")


def analyze(df: pd.DataFrame, name: str = "dataset") -> Analysis:
    num = df.select_dtypes("number").columns.tolist()
    cat = [c for c in df.columns if c not in num and df[c].nunique() <= max(20, len(df) // 5)]
    a = Analysis(
        name=name, rows=len(df), cols=df.shape[1], numeric=num, categorical=cat,
        missing={c: int(n) for c, n in df.isna().sum().items() if n},
        stats=df[num].describe().T.round(2) if num else pd.DataFrame(), df=df,
    )
    a.insights = _insights(df, num, cat)
    return a


def _insights(df: pd.DataFrame, num: list[str], cat: list[str]) -> list[str]:
    out: list[str] = []
    for c in num[:4]:
        s = df[c].dropna()
        if s.empty:
            continue
        out.append(f"{c}: total {s.sum():,.0f}, average {s.mean():,.1f}, range {s.min():,.0f}–{s.max():,.0f}.")
        q1, q3 = s.quantile([0.25, 0.75])
        outliers = s[(s < q1 - 1.5 * (q3 - q1)) | (s > q3 + 1.5 * (q3 - q1))]
        if len(outliers):
            out.append(f"{c} has {len(outliers)} outlier value(s), e.g. {outliers.iloc[0]:,.0f}.")
    if cat and num:
        g = df.groupby(cat[0])[num[0]].sum().sort_values(ascending=False)
        share = 100 * g.iloc[0] / g.sum() if g.sum() else 0
        out.append(f"Top {cat[0]} by {num[0]} is '{g.index[0]}' with {share:.0f}% of the total.")
    if len(num) >= 2:
        corr = df[num].corr().abs().where(lambda m: m < 1).stack()
        if not corr.empty and corr.max() > 0.7:
            a, b = corr.idxmax()
            out.append(f"{a} and {b} move together strongly (r={df[a].corr(df[b]):.2f}).")
    return out


def answer(df: pd.DataFrame, question: str) -> str:
    """Rule-based answers for common spoken questions; the LLM handles the rest."""
    q = question.lower()
    num = df.select_dtypes("number").columns
    for c in df.columns:
        if c.lower() in q and c in num:
            if "total" in q or "sum" in q:
                return f"Total {c} is {df[c].sum():,.0f}."
            if "average" in q or "mean" in q:
                return f"Average {c} is {df[c].mean():,.1f}."
            if "max" in q or "highest" in q:
                return f"Highest {c} is {df[c].max():,.0f}."
    if "rows" in q or "how many" in q:
        return f"The data has {len(df)} rows and {df.shape[1]} columns."
    return ""
