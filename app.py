"""
Indian Job Market Analysis - Streamlit dashboard
=================================================
Run:   streamlit run app.py
Needs: cleaned_indian_job_market.csv in the same folder as this file.
"""
from __future__ import annotations

import html
import math
import re
from difflib import SequenceMatcher
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

try:  # altair ships with streamlit, but we stay safe anyway
    import altair as alt

    HAS_ALTAIR = True
except Exception:  # pragma: no cover
    alt = None
    HAS_ALTAIR = False

# ------------------------------------------------------------------
# PAGE SETTINGS (must be the first Streamlit call)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Indian Job Market Analysis",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSV_NAME = "cleaned_indian_job_market.csv"
BRAND = "#2e75b6"
BRAND_DARK = "#1f4e79"
ACCENT = "#f59e0b"

P_HOME = "🏠 Home"
P_DASH = "📊 Dashboard"
P_EXPL = "🔎 Job Explorer"
P_CAREER = "🎯 Career Insights"
P_AI = "🤖 Smart Career Tools"
PAGES = [P_HOME, P_DASH, P_EXPL, P_CAREER, P_AI]

EXP_ORDER = [
    "Fresher (0-2 yrs)",
    "Junior (3-5 yrs)",
    "Mid-Level (6-9 yrs)",
    "Senior (10-14 yrs)",
    "Expert (15+ yrs)",
]
EXP_BINS = [-1, 2, 5, 9, 14, 1000]
EXP_CAP = 20  # top end of the experience slider means "20+ / no limit"
POSTED_OPTIONS = ["Any time", "Last 3 days", "Last 5 days", "Last 7 days"]
WORK_MODES = ["On-site", "Hybrid", "Remote"]
NON_CITY = {"Remote", "Unknown"}

CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bangalore rural": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bengaluru/bangalore": "Bengaluru",
    "gurgaon": "Gurugram",
    "new delhi": "Delhi",
    "delhi / ncr": "Delhi NCR",
    "delhi/ncr": "Delhi NCR",
    "ncr": "Delhi NCR",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "calcutta": "Kolkata",
    "navi mumbai": "Navi Mumbai",
    "all india": "Remote",
    "pan india": "Remote",
}

# ------------------------------------------------------------------
# STYLING
# ------------------------------------------------------------------
CSS = """
<style>
/* =========================
   MEDIUM MODERN THEME
   ========================= */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}
footer {visibility: hidden;}

/* Main background */
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(99,102,241,.08), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(168,85,247,.07), transparent 28%),
        #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1e293b 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] .stRadio label {
    border-radius: 10px;
    padding: 5px 8px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.08);
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #334155 0%, #4f46e5 52%, #7c3aed 100%);
    padding: 38px 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 12px 30px rgba(51,65,85,.18);
}
.hero h1 {
    color: white;
    margin: 0 0 8px 0;
    font-size: 2.15rem;
    font-weight: 750;
}
.hero p {
    color: rgba(255,255,255,.90);
    font-size: 1.02rem;
    margin: 0;
}

/* Cards */
.card {
    background: rgba(255,255,255,.92);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 22px;
    min-height: 185px;
    box-shadow: 0 5px 18px rgba(15,23,42,.06);
    transition: transform .18s ease, box-shadow .18s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 9px 24px rgba(15,23,42,.10);
}
.card h3 {
    margin-top: 0;
    font-size: 1.12rem;
    color: #1e293b;
}
.card p {
    margin-bottom: 0;
    color: #64748b;
}

/* KPI cards */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.94);
    border: 1px solid #e2e8f0;
    padding: 14px 16px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(15,23,42,.05);
}
div[data-testid="stMetricLabel"] {
    color: #64748b !important;
}
div[data-testid="stMetricValue"] {
    color: #1e293b !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #6366f1;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-weight: 650;
    min-height: 42px;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #4338ca;
    box-shadow: 0 6px 16px rgba(79,70,229,.22);
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
    border-radius: 10px !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px #6366f1 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 650;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4f46e5 !important;
}

/* Chips */
.chip {
    display: inline-block;
    padding: 4px 11px;
    margin: 3px 4px 3px 0;
    border-radius: 999px;
    font-size: .82rem;
    background: #eef2ff;
    color: #4338ca;
    border: 1px solid #c7d2fe;
}

/* Info / success boxes */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Tables */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

/* Section text */
.section-note {
    color: #64748b;
    font-size: .85rem;
}

/* Dividers */
hr {
    border-color: #e2e8f0;
}
</style>
"""


def banner(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{html.escape(title)}</h1>'
        f"<p>{html.escape(subtitle)}</p></div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# VERSION-SAFE STREAMLIT WRAPPERS
# ------------------------------------------------------------------
def show_chart(chart) -> None:
    for kwargs in ({"use_container_width": True}, {}):
        try:
            st.altair_chart(chart, **kwargs)
            return
        except TypeError:
            continue


def show_table(data: pd.DataFrame, height: int | None = None, column_config=None) -> None:
    extra = {}
    if height:
        extra["height"] = height
    if column_config:
        extra["column_config"] = column_config
    for kwargs in ({"use_container_width": True}, {}):
        try:
            st.dataframe(data, hide_index=True, **extra, **kwargs)
            return
        except TypeError:
            continue


# ------------------------------------------------------------------
# DATA CLEANING
# ------------------------------------------------------------------
def parse_locations(raw: str) -> tuple[list[str], str]:
    """Return (list of clean cities, work mode)."""
    text = str(raw or "").strip()
    low = text.lower()
    is_remote = bool(re.search(r"remote|work from home|wfh", low))
    is_hybrid = "hybrid" in low
    mode = "Remote" if is_remote else ("Hybrid" if is_hybrid else "On-site")

    text = re.sub(r"\(.*?\)", "", text)  # drop "(Sector 63)", "(All Areas)" ...
    text = re.sub(
        r"^\s*(hybrid|remote|work from home|wfh)\s*[-:–]*\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"delhi\s*/\s*ncr", "Delhi NCR", text, flags=re.IGNORECASE)

    cities: list[str] = []
    for part in re.split(r"[,;|]", text):
        name = part.strip(" -–")
        if not name:
            continue
        name = CITY_ALIASES.get(name.lower(), name)
        if name.lower() in {"remote", "work from home", "wfh"}:
            name = "Remote"
        if name not in cities:
            cities.append(name)
    if not cities:
        cities = ["Remote"] if is_remote else ["Unknown"]
    return cities, mode


def clean_description(value: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", str(value or ""), flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def parse_posted_days(value: str) -> float:
    low = str(value or "").lower()
    if re.search(r"today|just now|hour|minute|few", low):
        return 0.0
    match = re.search(r"(\d+)", low)
    return float(match.group(1)) if match else np.nan


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean the CSV and add helper columns used by every page."""
    df = raw.copy()

    text_cols = [
        "title", "companyName", "tagsAndSkills", "experience", "salary",
        "location", "jobUploaded", "jobDescription", "currency",
    ]
    num_cols = [
        "jobId", "companyId", "ReviewsCount", "AggregateRating",
        "minimumSalary", "maximumSalary", "minimumExperience",
        "maximumExperience", "average_salary",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip() if col in df else ""
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce") if col in df else np.nan

    df["title"] = df["title"].replace("", "Untitled")
    df["companyName"] = df["companyName"].replace("", "Unknown")
    df["currency"] = df["currency"].str.upper().replace("", "INR")
    df = df.reset_index(drop=True)

    # --- salary (INR only, in lakhs per annum) ---
    avg = df["average_salary"].fillna((df["minimumSalary"] + df["maximumSalary"]) / 2)
    df["salary_lpa"] = np.where((df["currency"] == "INR") & (avg > 0), avg / 1e5, np.nan)

    # --- experience ---
    parsed = df["experience"].str.extract(r"(\d+)\s*-\s*(\d+)").astype(float)
    df["exp_min"] = df["minimumExperience"].fillna(parsed[0])
    df["exp_max"] = df["maximumExperience"].fillna(parsed[1]).fillna(df["exp_min"])
    df["exp_level"] = (
        pd.cut(df["exp_min"], bins=EXP_BINS, labels=EXP_ORDER)
        .astype(object)
        .where(df["exp_min"].notna(), "Other")
    )

    # --- location ---
    parsed_loc = df["location"].apply(parse_locations)
    df["cities"] = parsed_loc.apply(lambda x: x[0])
    df["work_mode"] = parsed_loc.apply(lambda x: x[1])
    df["primary_city"] = df["cities"].apply(lambda x: x[0])

    # --- skills (merge different capitalisations of the same skill) ---
    token_lists = df["tagsAndSkills"].apply(
        lambda s: [t.strip() for t in re.split(r"[,|;]", s) if 1 < len(t.strip()) <= 40]
    )
    forms: dict[str, Counter] = {}
    for tokens in token_lists:
        for tok in tokens:
            forms.setdefault(tok.lower(), Counter())[tok] += 1
    canonical = {k: v.most_common(1)[0][0] for k, v in forms.items()}

    def canon_list(tokens: list[str]) -> list[str]:
        seen: list[str] = []
        for tok in tokens:
            name = canonical[tok.lower()]
            if name not in seen:
                seen.append(name)
        return seen

    df["skills"] = token_lists.apply(canon_list)

    # --- misc ---
    df["posted_days"] = df["jobUploaded"].apply(parse_posted_days)
    df["desc_clean"] = df["jobDescription"].apply(clean_description)
    return df


@st.cache_data(show_spinner="Loading data...")
def load_data(path: str) -> pd.DataFrame:
    return prepare(pd.read_csv(path))


def get_data() -> pd.DataFrame:
    here = Path(__file__).resolve().parent
    for candidate in (here / CSV_NAME, Path.cwd() / CSV_NAME):
        if candidate.exists():
            return load_data(str(candidate))

    st.error(f"`{CSV_NAME}` was not found next to app.py. Upload it below.")
    uploaded = st.file_uploader("Upload the CSV file", type="csv")
    if uploaded is None:
        st.stop()
    return prepare(pd.read_csv(uploaded))


def build_meta(df: pd.DataFrame) -> dict:
    sal = df["salary_lpa"].dropna()
    q99 = float(sal.quantile(0.99)) if len(sal) else 10.0
    sal_cap = float(max(10, math.ceil(q99 / 5) * 5))

    cities = df["cities"].explode().dropna()
    cities = cities[~cities.isin(NON_CITY)]
    skills = df["skills"].explode().dropna()
    return {
        "sal_cap": sal_cap,
        "city_options": cities.value_counts().head(60).index.tolist(),
        "skill_options": skills.value_counts().head(100).index.tolist(),
    }


# ------------------------------------------------------------------
# FILTERS (shared by Dashboard + Job Explorer)
# ------------------------------------------------------------------
def default_filters(meta: dict) -> dict:
    return {
        "f_kw": "",
        "f_company": "",
        "f_cities": [],
        "f_skills": [],
        "f_exp": (0, EXP_CAP),
        "f_sal": (0.0, meta["sal_cap"]),
        "f_posted": "Any time",
        "f_mode": [],
        "f_rating": 0.0,
    }


def apply_filters(df: pd.DataFrame, f: dict, sal_cap: float) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    kw = str(f["f_kw"]).strip()
    if kw:
        mask &= (
            df["title"].str.contains(kw, case=False, regex=False)
            | df["companyName"].str.contains(kw, case=False, regex=False)
            | df["tagsAndSkills"].str.contains(kw, case=False, regex=False)
        )
    company = str(f["f_company"]).strip()
    if company:
        mask &= df["companyName"].str.contains(company, case=False, regex=False)

    if f["f_cities"]:
        wanted = set(f["f_cities"])
        mask &= df["cities"].apply(lambda lst: not wanted.isdisjoint(lst))
    if f["f_skills"]:
        wanted = set(f["f_skills"])
        mask &= df["skills"].apply(lambda lst: not wanted.isdisjoint(lst))

    lo, hi = f["f_exp"]
    if lo > 0:
        mask &= df["exp_max"] >= lo
    if hi < EXP_CAP:
        mask &= df["exp_min"] <= hi

    lo, hi = f["f_sal"]
    if lo > 0:
        mask &= df["salary_lpa"] >= lo
    if hi < sal_cap:
        mask &= df["salary_lpa"] <= hi

    if f["f_posted"] != "Any time":
        days = int(re.search(r"\d+", f["f_posted"]).group())
        mask &= df["posted_days"] <= days
    if f["f_mode"]:
        mask &= df["work_mode"].isin(f["f_mode"])
    if f["f_rating"] and f["f_rating"] > 0:
        mask &= df["AggregateRating"] >= f["f_rating"]
    return df[mask]


def keep_filters_alive(meta: dict) -> None:
    """Streamlit forgets widget values on pages that don't render them."""
    for key in default_filters(meta):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def render_filters(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    defaults = default_filters(meta)
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    def reset() -> None:
        for k, v in default_filters(meta).items():
            st.session_state[k] = v

    sb = st.sidebar
    sb.divider()
    sb.subheader("🔍 Filters")
    sb.text_input("Keyword (title / skill / company)", key="f_kw", placeholder="e.g. python, C++, TCS")
    sb.multiselect("📍 City", meta["city_options"], key="f_cities", placeholder="All cities")
    sb.multiselect("🧠 Skills (any of)", meta["skill_options"], key="f_skills", placeholder="All skills")
    sb.slider(f"💼 Experience (years, {EXP_CAP} = {EXP_CAP}+)", 0, EXP_CAP, key="f_exp")
    sb.slider(
        f"💰 Salary (LPA, {meta['sal_cap']:g} = no limit)",
        0.0, float(meta["sal_cap"]), step=0.5, key="f_sal",
    )
    sb.multiselect("🏠 Work mode", WORK_MODES, key="f_mode", placeholder="All")
    sb.selectbox("🕒 Posted", POSTED_OPTIONS, key="f_posted")
    sb.text_input("🏢 Company contains", key="f_company")
    sb.slider("⭐ Min company rating", 0.0, 5.0, step=0.5, key="f_rating")
    sb.button("↺ Reset filters", on_click=reset)

    values = {key: st.session_state[key] for key in defaults}
    out = apply_filters(df, values, meta["sal_cap"])
    sb.caption(f"Showing **{len(out):,}** of {len(df):,} jobs")
    return out


# ------------------------------------------------------------------
# SMALL HELPERS + CHARTS
# ------------------------------------------------------------------
def lpa(x) -> str:
    return "—" if x is None or pd.isna(x) else f"₹{x:,.1f} LPA"


def counts_df(series: pd.Series, label: str, top: int = 10) -> pd.DataFrame:
    vc = series.dropna().value_counts().head(top)
    return pd.DataFrame({label: vc.index.astype(str), "Jobs": vc.values})


def hbar(data: pd.DataFrame, cat: str, val: str, fmt: str = ",.0f", color: str = BRAND) -> None:
    if data.empty:
        st.info("Not enough data for the current filters.")
        return
    d = data[[cat, val]].copy()
    d[cat] = d[cat].astype(str)
    if not HAS_ALTAIR:
        st.bar_chart(d.set_index(cat)[val])
        return
    chart = (
        alt.Chart(d)
        .mark_bar(color=color, cornerRadiusEnd=3)
        .encode(
            x=alt.X(f"{val}:Q", title=val),
            y=alt.Y(f"{cat}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
            tooltip=[alt.Tooltip(f"{cat}:N"), alt.Tooltip(f"{val}:Q", format=fmt)],
        )
        .properties(height=max(200, 30 * len(d) + 40))
    )
    show_chart(chart)


def vbar(data: pd.DataFrame, cat: str, val: str, order: list[str] | None = None,
         fmt: str = ",.0f", color: str = BRAND) -> None:
    if data.empty:
        st.info("Not enough data for the current filters.")
        return
    d = data[[cat, val]].copy()
    d[cat] = d[cat].astype(str)
    if not HAS_ALTAIR:
        st.bar_chart(d.set_index(cat)[val])
        return
    chart = (
        alt.Chart(d)
        .mark_bar(color=color, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(f"{cat}:N", sort=order if order else "-y", title=None,
                    axis=alt.Axis(labelAngle=0, labelLimit=140)),
            y=alt.Y(f"{val}:Q", title=val),
            tooltip=[alt.Tooltip(f"{cat}:N"), alt.Tooltip(f"{val}:Q", format=fmt)],
        )
        .properties(height=300)
    )
    show_chart(chart)


def donut(data: pd.DataFrame, cat: str, val: str) -> None:
    if data.empty:
        st.info("Not enough data for the current filters.")
        return
    d = data[[cat, val]].copy()
    d[cat] = d[cat].astype(str)
    if not HAS_ALTAIR:
        st.bar_chart(d.set_index(cat)[val])
        return
    chart = (
        alt.Chart(d)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta(f"{val}:Q"),
            color=alt.Color(f"{cat}:N", title=None),
            tooltip=[alt.Tooltip(f"{cat}:N"), alt.Tooltip(f"{val}:Q", format=",.0f")],
        )
        .properties(height=300)
    )
    show_chart(chart)


def salary_hist(series: pd.Series, bins: int = 30) -> int:
    """Histogram of salaries up to the 99th percentile. Returns #outliers hidden."""
    s = series.dropna()
    if s.empty:
        st.info("No salary data for the current filters.")
        return 0
    cap = float(s.quantile(0.99))
    inside = s[s <= cap]
    counts, edges = np.histogram(inside, bins=bins)
    d = pd.DataFrame({"start": edges[:-1], "end": edges[1:], "Jobs": counts})
    if not HAS_ALTAIR:
        st.bar_chart(d.assign(Salary=d["start"].round(1)).set_index("Salary")["Jobs"])
    else:
        chart = (
            alt.Chart(d)
            .mark_bar(color=BRAND)
            .encode(
                x=alt.X("start:Q", title="Salary (LPA)"),
                x2="end:Q",
                y=alt.Y("Jobs:Q", title="Number of jobs"),
                tooltip=[
                    alt.Tooltip("start:Q", title="From (LPA)", format=".1f"),
                    alt.Tooltip("end:Q", title="To (LPA)", format=".1f"),
                    alt.Tooltip("Jobs:Q"),
                ],
            )
            .properties(height=300)
        )
        show_chart(chart)
    return int(len(s) - len(inside))


def salary_scatter(d: pd.DataFrame) -> None:
    s = d.dropna(subset=["salary_lpa", "exp_min"])
    if s.empty:
        st.info("Not enough data for the current filters.")
        return
    s = s[s["salary_lpa"] <= s["salary_lpa"].quantile(0.99)]
    if len(s) > 2500:
        s = s.sample(2500, random_state=1)
    s = s[["title", "companyName", "exp_min", "salary_lpa"]].copy()
    if not HAS_ALTAIR:
        st.scatter_chart(s, x="exp_min", y="salary_lpa") if hasattr(st, "scatter_chart") else None
        return
    chart = (
        alt.Chart(s)
        .mark_circle(size=45, opacity=0.45, color=BRAND)
        .encode(
            x=alt.X("exp_min:Q", title="Minimum experience (years)"),
            y=alt.Y("salary_lpa:Q", title="Salary (LPA)"),
            tooltip=[
                alt.Tooltip("title:N", title="Role"),
                alt.Tooltip("companyName:N", title="Company"),
                alt.Tooltip("exp_min:Q", title="Min exp (yrs)"),
                alt.Tooltip("salary_lpa:Q", title="Salary (LPA)", format=".1f"),
            ],
        )
        .properties(height=320)
    )
    show_chart(chart)


def chips(items: list[str]) -> str:
    return "".join(f'<span class="chip">{html.escape(str(i))}</span>' for i in items)


def table_columns(d: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "Job Title": d["title"],
            "Company": d["companyName"],
            "Location": d["location"],
            "Experience": d["experience"],
            "Salary": d["salary"],
            "Avg Salary (LPA)": d["salary_lpa"].round(1),
            "Rating": d["AggregateRating"],
            "Posted": d["jobUploaded"],
        }
    )
    return out


TABLE_CONFIG = None
if hasattr(st, "column_config"):
    TABLE_CONFIG = {
        "Avg Salary (LPA)": st.column_config.NumberColumn(format="%.1f"),
        "Rating": st.column_config.NumberColumn(format="%.1f"),
    }


# ------------------------------------------------------------------
# PAGE: HOME
# ------------------------------------------------------------------
def page_home(df: pd.DataFrame) -> None:
    banner(
        "💼 Indian Job Market Analysis",
        "Explore jobs, companies, salaries, skills and career trends in the Indian job market.",
    )

    cities = df["cities"].explode().dropna()
    cities = cities[~cities.isin(NON_CITY)]
    skills = df["skills"].explode().dropna()
    median_sal = df["salary_lpa"].median()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💼 Total Jobs", f"{len(df):,}")
    c2.metric("🏢 Companies", f"{df['companyName'].nunique():,}")
    c3.metric("📍 Cities", f"{cities.nunique():,}")
    c4.metric("💰 Median Salary", lpa(median_sal))

    st.divider()
    st.subheader("📌 Market Snapshot")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Top Hiring City", cities.value_counts().index[0] if len(cities) else "—")
    s2.metric("Top Skill", skills.value_counts().index[0] if len(skills) else "—")
    remote_share = (df["work_mode"] != "On-site").mean() * 100
    s3.metric("Remote / Hybrid Jobs", f"{remote_share:.0f}%")
    lvl = (
        df.dropna(subset=["salary_lpa"]).groupby("exp_level")["salary_lpa"].median()
        .reindex(EXP_ORDER).dropna()
    )
    s4.metric("Best-Paid Level", lvl.idxmax().split(" (")[0] if len(lvl) else "—")

    st.divider()
    st.subheader("🚀 Explore the Platform")
    cards = [
        ("📊 Dashboard", "Interactive charts for companies, cities, experience levels, "
                         "salaries and skills - with powerful sidebar filters."),
        ("🔎 Job Explorer", "Search, sort and page through every job. Open a job to see "
                            "skills and the full description, and download results as CSV."),
        ("🎯 Career Insights", "Enter your role, skill, city and experience to see the salary "
                               "range people get - plus the skills to learn next."),
        ("🧠 Skills Discovery", "Find the most in-demand skills and which skills pay the most "
                                "(Dashboard → Skills tab)."),
        ("🤖 Smart Career Tools", "Get job recommendations, identify skill gaps and estimate salary from the dataset."),
    ]
    cols = st.columns(len(cards))
    for col, (title, text) in zip(cols, cards):
        col.markdown(
            f'<div class="card"><h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>',
            unsafe_allow_html=True,
        )
    st.info("👈 Use the sidebar to open the Dashboard, Job Explorer or Career Insights.")


# ------------------------------------------------------------------
# PAGE: DASHBOARD
# ------------------------------------------------------------------
def page_dashboard(d: pd.DataFrame, full: pd.DataFrame) -> None:
    banner("📊 Job Market Dashboard",
           "Companies, locations, salaries, skills and experience trends")

    if d.empty:
        st.warning("No jobs match the current filters. Try widening them or click **Reset filters**.")
        return

    avg_exp = ((d["exp_min"] + d["exp_max"]) / 2).mean()
    rating = d["AggregateRating"].mean()
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💼 Jobs", f"{len(d):,}", help=f"{len(d) / len(full):.0%} of all {len(full):,} jobs")
    k2.metric("🏢 Companies", f"{d['companyName'].nunique():,}")
    k3.metric("💰 Median Salary", lpa(d["salary_lpa"].median()))
    k4.metric("🎓 Avg Experience", "—" if pd.isna(avg_exp) else f"{avg_exp:.1f} yrs")
    k5.metric("⭐ Avg Rating", "—" if pd.isna(rating) else f"{rating:.1f} / 5",
              help="Only jobs whose company has a rating")
    st.write("")

    t_over, t_sal, t_skill, t_comp, t_data = st.tabs(
        ["📈 Overview", "💰 Salary", "🧠 Skills", "🏢 Companies & Cities", "📋 Data"]
    )

    # ---------------- Overview ----------------
    with t_over:
        a, b = st.columns(2)
        with a:
            st.subheader("📍 Top 10 Cities")
            cities = d["cities"].explode().dropna()
            cities = cities[~cities.isin(NON_CITY)]
            hbar(counts_df(cities, "City"), "City", "Jobs")
            st.caption("Jobs listing several cities count towards each city.")
        with b:
            st.subheader("🏢 Top 10 Hiring Companies")
            hbar(counts_df(d["companyName"], "Company"), "Company", "Jobs")

        a, b = st.columns(2)
        with a:
            st.subheader("💼 Jobs by Experience Level")
            lvl = counts_df(d["exp_level"], "Level", top=10)
            vbar(lvl, "Level", "Jobs", order=EXP_ORDER + ["Other"])
        with b:
            st.subheader("🏠 Work Mode")
            donut(counts_df(d["work_mode"], "Mode"), "Mode", "Jobs")

        st.subheader("🕒 When Were Jobs Posted?")
        posted = d["posted_days"].dropna().astype(int).value_counts().sort_index()
        pdf = pd.DataFrame({"Days ago": [f"{i}d" for i in posted.index], "Jobs": posted.values})
        vbar(pdf, "Days ago", "Jobs", order=pdf["Days ago"].tolist())

    # ---------------- Salary ----------------
    with t_sal:
        sal = d.dropna(subset=["salary_lpa"])
        if sal.empty:
            st.info("No INR salary data for the current filters.")
        else:
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Median", lpa(sal["salary_lpa"].median()))
            s2.metric("Average", lpa(sal["salary_lpa"].mean()))
            s3.metric("Lowest", lpa(sal["salary_lpa"].min()))
            s4.metric("Highest", lpa(sal["salary_lpa"].max()))
            st.caption("Salaries are shown in lakhs per annum (LPA, INR jobs only). "
                       "Non-INR jobs are excluded from salary statistics.")

            a, b = st.columns(2)
            with a:
                st.subheader("📊 Salary Distribution")
                hidden = salary_hist(sal["salary_lpa"])
                if hidden:
                    st.caption(f"{hidden} very high salaries (top 1%) hidden for readability.")
            with b:
                st.subheader("💰 Salary by Experience Level")
                g = (
                    sal.groupby("exp_level")["salary_lpa"].median()
                    .reindex(EXP_ORDER).dropna().rename("Median LPA")
                    .rename_axis("Level").reset_index()
                )
                vbar(g, "Level", "Median LPA", order=EXP_ORDER, fmt=".1f", color=ACCENT)

            st.subheader("🎯 Salary vs Experience")
            salary_scatter(sal)

            st.subheader("📍 Best-Paying Cities (median)")
            min_jobs = st.slider("Minimum jobs per city", 3, 50, 10, key="d_min_city")
            c = sal[~sal["primary_city"].isin(NON_CITY)]
            agg = c.groupby("primary_city")["salary_lpa"].agg(["median", "count"])
            agg = agg[agg["count"] >= min_jobs].sort_values("median", ascending=False).head(10)
            agg = agg.rename(columns={"median": "Median LPA"}).rename_axis("City").reset_index()
            hbar(agg, "City", "Median LPA", fmt=".1f", color=ACCENT)

            st.subheader("🏆 Top 10 Highest-Paying Jobs")
            top = sal.nlargest(10, "salary_lpa")
            show_table(table_columns(top).drop(columns=["Posted"]), column_config=TABLE_CONFIG)

    # ---------------- Skills ----------------
    with t_skill:
        skills = d["skills"].explode().dropna()
        a, b = st.columns(2)
        with a:
            st.subheader("🧠 Most In-Demand Skills")
            hbar(counts_df(skills, "Skill", top=15), "Skill", "Jobs")
        with b:
            st.subheader("💎 Highest-Paying Skills (median)")
            min_skill = st.slider("Minimum jobs per skill", 3, 50, 10, key="d_min_skill")
            e = d.dropna(subset=["salary_lpa"])[["skills", "salary_lpa"]].explode("skills")
            e = e.dropna(subset=["skills"])
            agg = e.groupby("skills")["salary_lpa"].agg(["median", "count"])
            agg = agg[agg["count"] >= min_skill].sort_values("median", ascending=False).head(15)
            agg = agg.rename(columns={"median": "Median LPA"}).rename_axis("Skill").reset_index()
            hbar(agg, "Skill", "Median LPA", fmt=".1f", color=ACCENT)

    # ---------------- Companies & cities ----------------
    with t_comp:
        a, b = st.columns(2)
        with a:
            st.subheader("⭐ Best-Rated Companies")
            r = d.dropna(subset=["AggregateRating"])
            r = r[r["ReviewsCount"].fillna(0) >= 100]
            if r.empty:
                st.info("No rated companies (100+ reviews) for the current filters.")
            else:
                g = r.groupby("companyName").agg(
                    Rating=("AggregateRating", "max"),
                    Reviews=("ReviewsCount", "max"),
                    Jobs=("jobId", "count"),
                ).sort_values(["Rating", "Reviews"], ascending=False).head(10).reset_index()
                g = g.rename(columns={"companyName": "Company"})
                show_table(g, column_config=TABLE_CONFIG)
        with b:
            st.subheader("📍 City Summary")
            c = d[~d["primary_city"].isin(NON_CITY)]
            if c.empty:
                st.info("No city data for the current filters.")
            else:
                g = c.groupby("primary_city").agg(
                    Jobs=("jobId", "count"),
                    Median_LPA=("salary_lpa", "median"),
                    Companies=("companyName", "nunique"),
                ).sort_values("Jobs", ascending=False).head(10).reset_index()
                g = g.rename(columns={"primary_city": "City", "Median_LPA": "Median LPA"})
                g["Median LPA"] = g["Median LPA"].round(1)
                show_table(g)

    # ---------------- Data ----------------
    with t_data:
        st.subheader("📋 Job Data")
        show_table(table_columns(d).head(200), height=420, column_config=TABLE_CONFIG)
        st.caption(f"Showing the first {min(200, len(d))} of {len(d):,} matching jobs. "
                   "Use the Job Explorer for full search and paging.")
        st.download_button(
            "⬇️ Download filtered data (CSV)",
            data=table_columns(d).to_csv(index=False).encode("utf-8"),
            file_name="filtered_jobs.csv",
            mime="text/csv",
        )


# ------------------------------------------------------------------
# PAGE: JOB EXPLORER
# ------------------------------------------------------------------
SORTS = {
    "Newest first": ("posted_days", True),
    "Highest salary": ("salary_lpa", False),
    "Lowest salary": ("salary_lpa", True),
    "Lowest experience": ("exp_min", True),
    "Highest experience": ("exp_min", False),
    "Best company rating": ("AggregateRating", False),
}


def page_explorer(d: pd.DataFrame) -> None:
    banner("🔎 Job Explorer", "Search, sort and explore job opportunities")

    if d.empty:
        st.warning("No jobs match the current filters. Try widening them or click **Reset filters**.")
        return

    c1, c2, c3 = st.columns([2, 1, 1])
    sort_name = c1.selectbox("Sort by", list(SORTS.keys()))
    page_size = c2.selectbox("Jobs per page", [25, 50, 100], index=1)
    col, asc = SORTS[sort_name]
    d = d.sort_values(col, ascending=asc, na_position="last", kind="mergesort")

    pages = max(1, math.ceil(len(d) / page_size))
    if pages > 1:
        if st.session_state.get("exp_page", 1) > pages:
            st.session_state["exp_page"] = pages
        page = int(c3.number_input("Page", min_value=1, max_value=pages, step=1, key="exp_page"))
    else:
        page = 1
        c3.markdown("**Page** 1 / 1")

    start = (page - 1) * page_size
    chunk = d.iloc[start:start + page_size]

    st.subheader(f"Available Jobs ({len(d):,})")
    show_table(table_columns(chunk), height=480, column_config=TABLE_CONFIG)
    st.caption(f"Page {page} of {pages} · rows {start + 1:,}-{start + len(chunk):,} of {len(d):,}")

    st.download_button(
        "⬇️ Download all matching jobs (CSV)",
        data=table_columns(d).to_csv(index=False).encode("utf-8"),
        file_name="job_search_results.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("📄 Job Details")
    labels = {
        idx: f"{row['title'][:70]} - {row['companyName'][:40]}"
        for idx, row in chunk.iterrows()
    }
    pick = st.selectbox(
        "Select a job from this page", list(labels.keys()), format_func=lambda k: labels[k]
    )
    job = chunk.loc[pick]

    st.markdown(f"### {job['title']}")
    st.markdown(f"**{job['companyName']}**")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Salary", job["salary"] or "—")
    m2.metric("💼 Experience", job["experience"] or "—")
    m3.metric("📍 Location", job["primary_city"])
    m4.metric("⭐ Rating", "—" if pd.isna(job["AggregateRating"]) else f"{job['AggregateRating']:.1f}")
    st.caption(f"Posted: {job['jobUploaded'] or '—'}  ·  Work mode: {job['work_mode']}  ·  "
               f"Full location: {job['location']}")
    if job["skills"]:
        st.markdown("**Skills**")
        st.markdown(chips(job["skills"]), unsafe_allow_html=True)
    with st.expander("Job description", expanded=True):
        text = job["desc_clean"] or "No description available."
        st.markdown(
            f"<div style='white-space:pre-wrap'>{html.escape(text)}</div>",
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# PAGE: CAREER INSIGHTS
# ------------------------------------------------------------------
def page_career(df: pd.DataFrame, meta: dict) -> None:
    banner("🎯 Career Insights",
           "See what similar jobs pay and which skills to add next")

    c1, c2, c3, c4 = st.columns(4)
    role = c1.text_input("Job role contains", placeholder="e.g. data analyst", key="ci_role")
    skill = c2.selectbox("Skill", ["Any"] + meta["skill_options"], key="ci_skill")
    city = c3.selectbox("City", ["Any"] + meta["city_options"][:30], key="ci_city")
    years = c4.slider("Your experience (years)", 0, EXP_CAP, 3, key="ci_years")

    m = df.dropna(subset=["salary_lpa"])
    if role.strip():
        m = m[m["title"].str.contains(role.strip(), case=False, regex=False)]
    if skill != "Any":
        m = m[m["skills"].apply(lambda lst: skill in lst)]
    if city != "Any":
        m = m[m["cities"].apply(lambda lst: city in lst)]
    m = m[(m["exp_min"] <= years) & (m["exp_max"] >= years)]

    if m.empty:
        st.warning("No matching jobs. Try removing the role keyword, skill or city.")
        return
    if len(m) < 10:
        st.info(f"Only {len(m)} matching jobs - treat the numbers below as a rough guide.")

    st.subheader(f"💰 Expected Salary - {len(m):,} matching jobs")
    q1, med, q3 = m["salary_lpa"].quantile([0.25, 0.5, 0.75])
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Lower range (25%)", lpa(q1))
    k2.metric("Typical (median)", lpa(med))
    k3.metric("Upper range (75%)", lpa(q3))
    k4.metric("Matching jobs", f"{len(m):,}")
    st.caption("Half of the matching jobs pay between the lower and upper range.")

    a, b = st.columns(2)
    with a:
        st.subheader("📊 Salary Spread")
        salary_hist(m["salary_lpa"], bins=20)
    with b:
        st.subheader("🏢 Companies Hiring")
        hbar(counts_df(m["companyName"], "Company"), "Company", "Jobs")

    st.subheader("🧠 Skills to Learn Next")
    skills = m["skills"].explode().dropna()
    if skill != "Any":
        skills = skills[skills != skill]
    hbar(counts_df(skills, "Skill", top=12), "Skill", "Jobs", color=ACCENT)
    st.caption("Skills most often requested together in the matching jobs.")

    st.subheader("📋 Top Matching Jobs")
    show_table(table_columns(m.nlargest(15, "salary_lpa")), height=420, column_config=TABLE_CONFIG)


# ------------------------------------------------------------------
# PAGE: SMART CAREER TOOLS (no sklearn / no extra ML package required)
# ------------------------------------------------------------------
def _normal_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Z0-9+#.]+", str(text).lower()) if len(w) > 1}


def _skill_match(a: str, b: str) -> float:
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


def smart_recommend_jobs(df: pd.DataFrame, profile: str, top_n: int = 10) -> pd.DataFrame:
    """Lightweight job recommender using word overlap + skill overlap."""
    query_words = _normal_words(profile)
    if not query_words:
        return pd.DataFrame()

    rows = []
    for idx, row in df.iterrows():
        title_words = _normal_words(row.get("title", ""))
        skill_text = " ".join(row.get("skills", []) if isinstance(row.get("skills", []), list) else [])
        desc_words = _normal_words(row.get("desc_clean", ""))
        company_words = _normal_words(row.get("companyName", ""))
        text_words = title_words | _normal_words(skill_text) | desc_words | company_words
        overlap = len(query_words & text_words) / max(1, len(query_words))
        title_overlap = len(query_words & title_words) / max(1, len(query_words))
        skill_overlap = len(query_words & _normal_words(skill_text)) / max(1, len(query_words))
        score = 100 * (0.55 * title_overlap + 0.30 * skill_overlap + 0.15 * overlap)
        if score > 0:
            rows.append((idx, score))

    if not rows:
        return pd.DataFrame()
    scores = pd.DataFrame(rows, columns=["_idx", "Match Score"])
    scores = scores.sort_values("Match Score", ascending=False).head(top_n)
    out = df.loc[scores["_idx"].tolist()].copy()
    out["Match Score (%)"] = scores["Match Score"].round(1).to_numpy()
    return out


def smart_skill_gap(df: pd.DataFrame, role: str, user_skills_text: str, top_n: int = 30):
    """Compare user's skills with skills frequently requested for a target role."""
    role = role.strip()
    user_skills = [x.strip().lower() for x in re.split(r"[,;|]", user_skills_text) if x.strip()]
    m = df.copy()
    if role:
        m = m[m["title"].str.contains(role, case=False, regex=False, na=False)]
    if m.empty:
        return pd.DataFrame(), []

    counts = Counter()
    for skills in m["skills"]:
        for s in skills:
            counts[str(s)] += 1

    common = counts.most_common(top_n)
    result = []
    for skill, count in common:
        matched = any(_skill_match(skill, us) >= 0.86 for us in user_skills)
        result.append({
            "Skill": skill,
            "Jobs Requiring It": count,
            "Status": "Already have" if matched else "Skill gap",
        })
    table = pd.DataFrame(result)
    missing = table[table["Status"] == "Skill gap"]["Skill"].tolist() if not table.empty else []
    return table, missing


def smart_salary_estimate(df: pd.DataFrame, role: str, city: str, years: int, mode: str):
    """Estimate salary from comparable jobs using median + simple market adjustments."""
    m = df.dropna(subset=["salary_lpa"]).copy()
    if role.strip():
        role_m = m[m["title"].str.contains(role.strip(), case=False, regex=False, na=False)]
        if len(role_m) >= 5:
            m = role_m
    if city != "Any":
        city_m = m[m["cities"].apply(lambda x: city in x)]
        if len(city_m) >= 5:
            m = city_m
    if mode != "Any":
        mode_m = m[m["work_mode"] == mode]
        if len(mode_m) >= 5:
            m = mode_m
    if m.empty:
        return None, None, None, 0

    # Prefer jobs whose experience band contains the user's experience.
    exp_m = m[(m["exp_min"] <= years) & (m["exp_max"] >= years)]
    if len(exp_m) >= 5:
        m = exp_m

    median = float(m["salary_lpa"].median())
    q1 = float(m["salary_lpa"].quantile(0.25))
    q3 = float(m["salary_lpa"].quantile(0.75))
    return median, q1, q3, len(m)


def page_smart_tools(df: pd.DataFrame, meta: dict) -> None:
    banner("🤖 Smart Career Tools", "Job recommendations, skill-gap analysis and salary estimation — powered by your job-market data.")
    st.info("These tools work directly on your CSV data. No API or machine-learning package is required.")

    t1, t2, t3 = st.tabs(["🎯 Job Recommendation", "🧩 Skill Gap Analyzer", "💰 Salary Estimator"])

    with t1:
        st.subheader("🎯 Find jobs that match your profile")
        profile = st.text_area(
            "Enter your skills / profile",
            placeholder="Example: Python, SQL, Power BI, Excel, data analysis",
            height=100,
            key="smart_profile",
        )
        n = st.slider("Number of recommendations", 5, 20, 10, key="smart_rec_n")
        if st.button("🔎 Recommend Jobs", key="smart_rec_btn"):
            recs = smart_recommend_jobs(df, profile, n)
            if recs.empty:
                st.warning("No close matches found. Try adding more skills or a job role.")
            else:
                st.success(f"Found {len(recs)} matching jobs.")
                show_table(table_columns(recs), column_config=TABLE_CONFIG)
                st.download_button(
                    "⬇️ Download recommendations",
                    data=table_columns(recs).to_csv(index=False).encode("utf-8"),
                    file_name="job_recommendations.csv",
                    mime="text/csv",
                    key="smart_rec_download",
                )

    with t2:
        st.subheader("🧩 See which skills you should learn next")
        c1, c2 = st.columns(2)
        role = c1.text_input("Target role", placeholder="e.g. Data Analyst", key="smart_gap_role")
        user_skills = c2.text_input("Your current skills", placeholder="Python, Excel, SQL", key="smart_gap_skills")
        if st.button("🧠 Analyze Skill Gap", key="smart_gap_btn"):
            table, missing = smart_skill_gap(df, role, user_skills)
            if table.empty:
                st.warning("No jobs found for this role. Try a broader role name.")
            else:
                have = int((table["Status"] == "Already have").sum())
                gaps = int((table["Status"] == "Skill gap").sum())
                a, b, c = st.columns(3)
                a.metric("Skills found", len(table))
                b.metric("You already have", have)
                c.metric("Skill gaps", gaps)
                st.dataframe(table, hide_index=True, use_container_width=True)
                if missing:
                    st.success("Recommended skills to learn: " + ", ".join(missing[:10]))

    with t3:
        st.subheader("💰 Estimate a realistic salary range")
        c1, c2, c3, c4 = st.columns(4)
        role = c1.text_input("Job role", placeholder="e.g. Data Analyst", key="smart_sal_role")
        city = c2.selectbox("City", ["Any"] + meta["city_options"][:40], key="smart_sal_city")
        years = c3.slider("Experience", 0, EXP_CAP, 2, key="smart_sal_years")
        mode = c4.selectbox("Work mode", ["Any"] + WORK_MODES, key="smart_sal_mode")
        if st.button("💰 Estimate Salary", key="smart_sal_btn"):
            med, q1, q3, count = smart_salary_estimate(df, role, city, years, mode)
            if med is None:
                st.warning("Not enough salary data for these choices. Try removing the city or role filter.")
            else:
                a, b, c, d = st.columns(4)
                a.metric("Estimated salary", lpa(med))
                b.metric("Lower range", lpa(q1))
                c.metric("Upper range", lpa(q3))
                d.metric("Comparable jobs", f"{count:,}")
                st.success("This estimate is based on the median and quartiles of comparable jobs in your dataset.")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main() -> None:
    version = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
    if version < (1, 30):
        st.error(f"Streamlit {st.__version__} is too old. Run:  pip install --upgrade streamlit")
        st.stop()

    st.markdown(CSS, unsafe_allow_html=True)
    df = get_data()
    meta = build_meta(df)

    st.sidebar.title("💼 Job Market")
    page = st.sidebar.radio("Navigate", PAGES, key="nav")

    if page in (P_DASH, P_EXPL):
        filtered = render_filters(df, meta)
    else:
        keep_filters_alive(meta)
        filtered = df

    if page == P_HOME:
        page_home(df)
    elif page == P_DASH:
        page_dashboard(filtered, df)
    elif page == P_EXPL:
        page_explorer(filtered)
    elif page == P_CAREER:
        page_career(df, meta)
    else:
        page_smart_tools(df, meta)


if __name__ == "__main__":
    main()