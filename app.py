import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import os
from pathlib import Path
import json
import random
import base64

st.set_page_config(
    layout="wide",
    page_title="SepsisCare AI",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Professional UI styling + Background Image
# -----------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    @keyframes pan {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
    @keyframes zoom {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
    @keyframes drift {{ 0% {{ transform: translate(0,0); }} 50% {{ transform: translate(20px, 15px); }} 100% {{ transform: translate(0,0); }} }}
    @keyframes pulse-bg {{ 0% {{ filter: brightness(1); }} 50% {{ filter: brightness(1.1); }} 100% {{ filter: brightness(1); }} }}
    @keyframes tilt {{ 0% {{ transform: perspective(1000px) rotateX(0deg); }} 50% {{ transform: perspective(1000px) rotateX(1deg); }} 100% {{ transform: perspective(1000px) rotateX(0deg); }} }}
    @keyframes shift {{ 0% {{ background-position: 10% 10%; }} 50% {{ background-position: 90% 90%; }} 100% {{ background-position: 10% 10%; }} }}

    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-attachment: fixed;
        background-size: cover;
        animation: pan 30s ease-in-out infinite; /* DEFAULT: Always moving on login & everywhere */
    }}
    .anim-pan {{ animation: pan 25s ease-in-out infinite !important; background-size: 130% 130% !important; }}
    .anim-zoom {{ animation: zoom 20s ease-in-out infinite !important; }}
    .anim-drift {{ animation: drift 15s ease-in-out infinite !important; }}
    .anim-pulse {{ animation: pulse-bg 10s ease-in-out infinite !important; }}
    .anim-tilt {{ animation: tilt 12s ease-in-out infinite !important; }}
    .anim-shift {{ animation: shift 30s ease-in-out infinite !important; background-size: 150% 150% !important; }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Try to set background image if exists
bg_img_path = PROJECT_DIR / "background.png" if 'PROJECT_DIR' in locals() else Path("background.png")
if bg_img_path.exists():
    set_png_as_page_bg(str(bg_img_path))

st.markdown(
    """
<style>
.stApp {
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(5px);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #f6f8ff 100%);
  border-right: 1px solid rgba(15, 23, 42, 0.08);
}
.card {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(15px);
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.08);
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
  border-bottom: 2px solid rgba(59, 130, 246, 0.2);
  padding-bottom: 5px;
}
.muted { color: #475569; font-size: 14px; }
.section-h { display:flex; align-items:center; justify-content:space-between; gap:12px; margin: 20px 0; }
.section-h h2 { font-weight: 800; color: #0f172a; margin: 0; }

@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
.anim-in { animation: fadeSlideIn 0.5s ease-out; }

/* Metrics styling */
[data-testid="stMetricValue"] {
  font-weight: 800 !important;
  color: #2563eb !important;
}
[data-testid="stMetricDelta"] {
  font-weight: 600 !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: rgba(255, 255, 255, 0.95) !important;
  border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] { 
    border-radius: 16px; 
    border: 1px solid rgba(255, 255, 255, 0.3); 
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

/* Button enhancement */
.stButton > button {
  border: none !important;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
  transition: all 0.3s ease !important;
}
.stButton > button:hover {
  filter: brightness(1.1);
  transform: scale(1.02);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3) !important;
}
@keyframes softPulse {
  0% { transform: scale(1); box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06); }
  50% { transform: scale(1.01); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.10); }
  100% { transform: scale(1); box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06); }
}
.pulse { animation: softPulse 1.8s ease-in-out infinite; }
.risk-banner { border-radius: 14px; padding: 14px 16px; color: white; border: 1px solid rgba(255,255,255,0.35); box-shadow: 0 12px 30px rgba(2, 6, 23, 0.18); }
.risk-high { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); }
.risk-med  { background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); }
.risk-low  { background: linear-gradient(135deg, #22c55e 0%, #15803d 100%); }
div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid rgba(15, 23, 42, 0.08); }

/* Colorful controls */
.stButton > button {
  border-radius: 12px !important;
  border: 1px solid rgba(15, 23, 42, 0.10) !important;
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 55%, #10b981 100%) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 22px rgba(2, 6, 23, 0.10) !important;
}
.stButton > button:hover { filter: brightness(1.04); transform: translateY(-1px); }

div[data-baseweb="tab-list"] button {
  border-radius: 12px !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
  background: linear-gradient(135deg, rgba(59,130,246,0.18) 0%, rgba(124,58,237,0.18) 100%) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Data + model helpers
# -----------------------------
PROJECT_DIR = Path(__file__).resolve().parent

MODEL_CANDIDATES = [
    PROJECT_DIR / "final_xgboost_sepsis_model_v2.pkl",
    PROJECT_DIR / "final_xgboost_sepsis_model.pkl",
    PROJECT_DIR / "final_sepsis_model.pkl",
    PROJECT_DIR / "final_sepsis_model.joblib",
]


@st.cache_resource(show_spinner=False)
def load_model():
    for p in MODEL_CANDIDATES:
        if p.exists():
            return joblib.load(p)
    raise FileNotFoundError(
        "Model file not found. Expected one of: "
        + ", ".join([c.name for c in MODEL_CANDIDATES])
    )


@st.cache_data(show_spinner=False)
def load_dataset():
    # Prefer the fixed/production-ready dataset if available
    fixed = PROJECT_DIR / "Data_after_Cleaning_fixed.csv"
    src = fixed if fixed.exists() else (PROJECT_DIR / "Data_after_Cleaning.csv")
    df = pd.read_csv(src)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    if "subject_id" in df.columns:
        # avoid showing raw identifiers in UI tables
        df = df.drop(columns=["subject_id"])
    # NOTE: Do not drop model features here (e.g., race columns).
    # We keep the full feature set for prediction, and clean columns only for display tables.
    # Streamlit/Arrow compatibility: ensure no bool/object sneaks into tables
    for c in df.columns:
        if df[c].dtype == "bool":
            df[c] = df[c].astype("int64")
    
    return df


def ensure_csv(path: Path, columns: list[str]):
    if not path.exists():
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def risk_label(prob: float) -> str:
    if prob > 0.7:
        return "High"
    if prob > 0.4:
        return "Medium"
    return "Low"


def risk_banner_html(risk: str) -> str:
    cls = "risk-low" if risk == "Low" else "risk-med" if risk == "Medium" else "risk-high"
    icon = "🟢" if risk == "Low" else "🟡" if risk == "Medium" else "🔴"
    title = f"{icon} {risk.upper()} MORTALITY RISK"
    subtitle = (
        "Patient appears stable; continue routine monitoring."
        if risk == "Low"
        else "Some indicators are unstable; increase monitoring frequency."
        if risk == "Medium"
        else "Multiple abnormal indicators; escalate care and review immediately."
    )
    return f"""
    <div class="risk-banner {cls} anim-in pulse">
      <div style="font-size:18px;font-weight:750;letter-spacing:0.2px">{title}</div>
      <div style="opacity:0.95;margin-top:4px">{subtitle}</div>
    </div>
    """


def card(title: str, body_html: str):
    st.markdown(
        f"""
<div class="card anim-in">
  <div class="card-title">{title}</div>
  <div class="muted">{body_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def get_patient_display_id(patient_index: int) -> str:
    return f"PT-{patient_index:05d}"


RISK_COLOR_MAP = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}


def apply_module_theme(active_menu: str):
    themes = {
        "Patient Records": ("#eaf2ff", "#f3ecff", "#f7f9ff", "anim-pan"),
        "Doctor Dashboard (ICU)": ("#ffe9e9", "#fff7ed", "#f8fafc", "anim-zoom"),
        "Outpatient Records (Past Patients)": ("#eaf2ff", "#e6fffb", "#f8fafc", "anim-drift"),
        "Inpatient Summary (IPD)": ("#f3ecff", "#eaf2ff", "#f8fafc", "anim-pulse"),
        "Single Patient": ("#e8fff4", "#eaf2ff", "#f8fafc", "anim-tilt"),
        "Batch Dashboard": ("#ffe9e9", "#fff7ed", "#f8fafc", "anim-shift"),
        "ICU Specialization Analysis": ("#eaf2ff", "#e6fffb", "#f8fafc", "anim-pan"),
        "Prediction History": ("#f1f5f9", "#eaf2ff", "#f8fafc", "anim-zoom"),
        "AI Explanation": ("#f3ecff", "#eaf2ff", "#f8fafc", "anim-drift"),
        "Model Info": ("#f1f5f9", "#f3ecff", "#f8fafc", "anim-pulse"),
        "Patient Case History": ("#f3ecff", "#eaf2ff", "#f8fafc", "anim-tilt"),
        "Prescriptions": ("#e6fffb", "#e8fff4", "#f8fafc", "anim-shift"),
    }
    c1, c2, c3, anim_class = themes.get(active_menu, ("#eaf2ff", "#f3ecff", "#f8fafc", "anim-pan"))
    st.markdown(
        f"""
<style>
.stApp {{
  background: radial-gradient(1200px 800px at 20% 10%, {c1} 0%, rgba(234,242,255,0) 55%),
              radial-gradient(1000px 700px at 85% 0%, {c2} 0%, rgba(243,236,255,0) 55%),
              linear-gradient(180deg, {c3} 0%, #f5f7fb 45%, #f8fafc 100%);
}}

/* CSS Override for Module-Specific Animation */
.stApp {{
    animation: inherit; /* Reset default */
}}
.stApp {{
    animation-name: {anim_class.replace('anim-', '')} !important;
    animation-duration: inherit !important;
    animation-iteration-count: infinite !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def load_model_report() -> dict | None:
    p = PROJECT_DIR / "model_report_v2.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def jitter(value: float, pct: float, low: float | None = None, high: float | None = None) -> float:
    if value is None or not np.isfinite(value):
        return float("nan")
    v = float(value)
    delta = abs(v) * pct
    out = v + random.uniform(-delta, delta)
    if low is not None:
        out = max(low, out)
    if high is not None:
        out = min(high, out)
    return out


def get_model_feature_names(model_obj) -> list[str] | None:
    """
    Robustly extract feature names for XGBoost/sklearn models.
    Returns None if unavailable.
    """
    try:
        if hasattr(model_obj, "get_booster"):
            booster = model_obj.get_booster()
            names = getattr(booster, "feature_names", None)
            if isinstance(names, (list, tuple)) and len(names) > 0:
                return list(names)
    except Exception:
        pass

    names = getattr(model_obj, "feature_names_in_", None)
    if isinstance(names, (list, tuple, np.ndarray)) and len(names) > 0:
        return [str(x) for x in list(names)]

    return None


def drop_all_zero_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggressively remove columns that contain only zeros, nulls, or empty strings.
    """
    if df.empty:
        return df
    
    cols_to_keep = []
    for col in df.columns:
        # Check if the column has any non-zero, non-null value
        series = df[col]
        
        # For numeric columns
        if np.issubdtype(series.dtype, np.number):
            if not ((series == 0) | series.isna()).all():
                cols_to_keep.append(col)
        # For object/string columns
        else:
            if not (series.astype(str).isin(['0', '0.0', 'None', 'nan', '']) | series.isna()).all():
                cols_to_keep.append(col)
                
    return df[cols_to_keep]


def add_gender_column(df: pd.DataFrame) -> pd.DataFrame:
    if "gender_F" in df.columns or "gender_M" in df.columns:
        f = df["gender_F"] if "gender_F" in df.columns else 0
        m = df["gender_M"] if "gender_M" in df.columns else 0
        gender = np.where(f.astype(float) >= 0.5, "Female", np.where(m.astype(float) >= 0.5, "Male", "Unknown"))
        df = df.copy()
        df["Gender"] = gender
        df = df.drop(columns=[c for c in ["gender_F", "gender_M"] if c in df.columns])
    return df
# Login session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

model = load_model()
# ================= LOGIN PAGE =================

if not st.session_state.logged_in:

    st.markdown(
        """
<style>
/* Login hero */
.login-wrap {
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.18) 0%, rgba(124, 58, 237, 0.16) 55%, rgba(16, 185, 129, 0.14) 100%),
              linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.78) 100%);
  box-shadow: 0 18px 50px rgba(2, 6, 23, 0.10);
  padding: 26px 22px;
}
.login-title {
  font-size: 34px;
  font-weight: 820;
  letter-spacing: 0.2px;
  color: #0b1220;
  margin: 0;
}
.login-sub {
  margin-top: 6px;
  color: rgba(15, 23, 42, 0.72);
  font-size: 16px;
}
.pill-row { margin-top: 14px; display:flex; gap:10px; flex-wrap: wrap; }
.pill {
  padding: 8px 12px;
  border-radius: 999px;
  font-weight: 650;
  font-size: 13px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.70);
}
.pill strong { color: #0f172a; }
.blob {
  position:absolute;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  filter: blur(26px);
  opacity: 0.55;
  animation: floaty 8s ease-in-out infinite;
}
.b1 { background: #22c55e; top: -110px; left: -90px; animation-delay: 0.2s; }
.b2 { background: #3b82f6; bottom: -130px; right: -90px; animation-delay: 0.8s; }
.b3 { background: #a855f7; top: -120px; right: 60px; width: 220px; height: 220px; animation-delay: 1.4s; }
@keyframes floaty {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(12px, 18px) scale(1.05); }
  100% { transform: translate(0, 0) scale(1); }
}
</style>
<div class="login-wrap anim-in">
  <div class="blob b1"></div>
  <div class="blob b2"></div>
  <div class="blob b3"></div>
  <div style="position:relative; z-index:2;">
    <div class="login-title">SepsisCare AI</div>
    <div class="login-sub">Real-time ICU triage console • Sepsis mortality risk • Patient workflow</div>
    <div class="pill-row">
      <div class="pill">Status: <strong>Online</strong></div>
      <div class="pill">Model: <strong>XGBoost</strong></div>
      <div class="pill">Mode: <strong>Clinical Demo</strong></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.info("Login to open the Sepsis ICU console.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):

        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid username or password")

    st.stop()

raw_data = load_dataset().head(250)

# Display-only view (hide noisy columns, show Gender as Male/Female)
raw_display = add_gender_column(raw_data)

# FEATURE: Rename 'aids' to 'hiv' for display
if "aids" in raw_display.columns:
    raw_display = raw_display.rename(columns={"aids": "hiv"})

# FEATURE: Remove all-zero columns for display
raw_display = drop_all_zero_columns(raw_display)

# Optionally hide race one-hot columns from UI tables (keep in raw_data for model)
race_cols = [
    "race_Black or African American",
    "race_Hispanic or Latin",
    "race_White",
    "race_Others race",
]
raw_display = raw_display.drop(columns=[c for c in race_cols if c in raw_display.columns], errors="ignore")

PRED_HISTORY_PATH = PROJECT_DIR / "prediction_history.csv"
CASE_HISTORY_PATH = PROJECT_DIR / "patient_cases.csv"
PRESCRIPTIONS_PATH = PROJECT_DIR / "prescriptions.csv"

ensure_csv(PRED_HISTORY_PATH, ["Patient_ID", "Risk", "Probability", "Date"])
ensure_csv(
    CASE_HISTORY_PATH,
    [
        "Patient_ID",
        "Created_At",
        "Chief_Complaint",
        "History_of_Present_Illness",
        "Past_Medical_History",
        "Allergies",
        "Vitals",
        "Labs",
        "Assessment_Notes",
    ],
)
ensure_csv(
    PRESCRIPTIONS_PATH,
    [
        "Patient_ID",
        "Created_At",
        "Medication",
        "Dose",
        "Route",
        "Frequency",
        "Duration",
        "Indication",
        "Prescriber",
        "Notes",
    ],
)

# ================= FIX FEATURE MISMATCH (model-aligned matrix) =================
_report = load_model_report()
model_features = None
if _report and isinstance(_report, dict):
    feats = _report.get("features", None)
    if isinstance(feats, list) and len(feats) > 0:
        model_features = [str(x) for x in feats]

if not model_features:
    model_features = get_model_feature_names(model)

if not model_features:
    # Safe fallback: use all numeric columns available for prediction
    model_features = raw_data.select_dtypes(include=[np.number]).columns.tolist()

X = raw_data.copy()
for col in model_features:
    if col not in X.columns:
        X[col] = 0
X = X[model_features]

st.sidebar.markdown("## 🏥 Hospital ICU Dashboard")
st.sidebar.markdown("AI Clinical Decision Support")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Patient Records",
        "Doctor Dashboard (ICU)",
        "Outpatient Records (Past Patients)",
        "Inpatient Summary (IPD)",
        "Patient Case History",
        "Prescriptions",
        "Single Patient",
        "Batch Dashboard",
        "Prediction History",
        "ICU Specialization Analysis",
        "AI Explanation",
        "Model Info"
    ]
)

apply_module_theme(menu)
if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.rerun()

with st.sidebar:
    st.markdown("---")
    try:
        probs_sidebar = model.predict_proba(X)[:, 1]
        risk_sidebar = pd.Series(probs_sidebar).apply(risk_label)
    except Exception as e:
        st.error(f"Model prediction error: {e}")
        probs_sidebar = np.zeros(len(raw_data))
        risk_sidebar = pd.Series(["Low"] * len(raw_data))
    st.markdown("### ICU Snapshot")
    c1, c2 = st.columns(2)
    c1.metric("Patients", len(raw_data))
    c2.metric("High Risk", int((risk_sidebar == "High").sum()))
    st.caption(f"Last refresh: {now_str()}")

st.markdown(
    """
<div class="section-h">
  <h2>🩺 SepsisCare AI</h2>
  <div class="muted">ICU Clinical Decision Support • Mortality Risk Prediction</div>
</div>
""",
    unsafe_allow_html=True,
)
card(
    "What this system does",
    "It analyzes ICU patient data using a trained ML model to estimate sepsis mortality risk, "
    "and provides workflow modules for <b>case history</b> and <b>prescriptions</b> to make the app feel like a real product.",
)

# Top-of-page “Sepsis panel” KPIs
probs_top = model.predict_proba(X)[:, 1]
df_kpi = pd.DataFrame({"prob": probs_top})
df_kpi["risk"] = df_kpi["prob"].apply(risk_label)
hi_n = int((df_kpi["risk"] == "High").sum())
med_n = int((df_kpi["risk"] == "Medium").sum())
low_n = int((df_kpi["risk"] == "Low").sum())

k1, k2, k3, k4 = st.columns([0.22, 0.22, 0.22, 0.34], gap="large")
k1.metric("🔴 High", hi_n)
k2.metric("🟡 Medium", med_n)
k3.metric("🟢 Low", low_n)
report = load_model_report()
if report and isinstance(report, dict) and "test" in report:
    test = report.get("test", {}) or {}
    acc = test.get("accuracy", None)
    auc = test.get("roc_auc", None)
    k4.markdown(
        f"""<div class="card anim-in"><div class="card-title">Console</div>
<div class="muted">Live triage view • {now_str()}<br/>
Model (validated): Accuracy <b>{acc:.3f}</b> • ROC-AUC <b>{auc:.3f}</b>
</div></div>""",
        unsafe_allow_html=True,
    )
else:
    k4.markdown(
        f"""<div class="card anim-in"><div class="card-title">Console</div><div class="muted">Live triage view • {now_str()}</div></div>""",
        unsafe_allow_html=True,
    )
# ================= PATIENT RECORDS =================

if menu == "Patient Records":

    st.header("Hospital Patient Records")

    st.write("Total Patients:", len(raw_data))

    display_df = drop_all_zero_columns(raw_display)
    st.dataframe(display_df)

    st.download_button(
        label="Download Patient Dataset",
        data=display_df.to_csv(index=False),
        file_name="hospital_patient_records.csv",
        mime="text/csv"
    )

# ================= DOCTOR DASHBOARD (ICU) =================

if menu == "Doctor Dashboard (ICU)":
    st.header("Doctor Dashboard (ICU)")
    st.caption("ICU doctor roster and patient assignment view (demo).")

    DOCTORS_PATH = PROJECT_DIR / "icu_doctors.csv"
    ASSIGN_PATH = PROJECT_DIR / "icu_assignments.csv"

    ensure_csv(
        DOCTORS_PATH,
        ["Doctor_ID", "Doctor_Name", "Speciality", "Shift"],
    )
    ensure_csv(
        ASSIGN_PATH,
        ["Doctor_ID", "Patient_ID", "Patient_Name", "Age", "Diagnosis", "Status", "Risk", "Risk_Prob"],
    )

    doctors = pd.read_csv(DOCTORS_PATH)
    if doctors.empty:
        doctors = pd.DataFrame(
            [
                {"Doctor_ID": "D-001", "Doctor_Name": "Dr. A. Sharma", "Speciality": "Critical Care", "Shift": "Day"},
                {"Doctor_ID": "D-002", "Doctor_Name": "Dr. M. Khan", "Speciality": "Intensivist", "Shift": "Night"},
                {"Doctor_ID": "D-003", "Doctor_Name": "Dr. R. Patel", "Speciality": "Pulmonology", "Shift": "Day"},
                {"Doctor_ID": "D-004", "Doctor_Name": "Dr. S. Iyer", "Speciality": "Nephrology", "Shift": "Evening"},
                {"Doctor_ID": "D-005", "Doctor_Name": "Dr. N. Das", "Speciality": "Infectious Disease", "Shift": "On-call"},
            ]
        )
        doctors.to_csv(DOCTORS_PATH, index=False)

    # Build/refresh assignments if missing or wrong size
    probs = model.predict_proba(X)[:, 1]
    risk = pd.Series(probs).apply(risk_label).values

    # derive "names" deterministically (demo)
    first_names = ["Aarav", "Diya", "Kabir", "Anaya", "Vivaan", "Isha", "Arjun", "Meera", "Reyansh", "Sara"]
    last_names = ["Singh", "Kumar", "Patel", "Sharma", "Das", "Gupta", "Nair", "Reddy", "Khan", "Iyer"]

    def patient_name(i: int) -> str:
        return f"{first_names[i % len(first_names)]} {last_names[(i * 3) % len(last_names)]}"

    # diagnosis/status derived from available vitals/labs (fallbacks)
    def diagnosis_for_row(row: pd.Series, risk_level: str) -> str:
        sofa = row.get("sofa_score", np.nan)
        lact = row.get("glucose_average", np.nan)
        if np.isfinite(sofa) and sofa >= 8:
            return "Sepsis with multi-organ dysfunction"
        if risk_level == "High":
            return "Septic shock (suspected)"
        if risk_level == "Medium":
            return "Sepsis (monitor closely)"
        return "Sepsis (stable)"

    def status_from_risk(risk_level: str) -> str:
        return "Critical" if risk_level == "High" else "Under Observation" if risk_level == "Medium" else "Stable"

    assign_df = pd.read_csv(ASSIGN_PATH)
    if assign_df.empty or len(assign_df) != len(raw_data):
        rows = []
        doc_ids = doctors["Doctor_ID"].tolist()
        for i in range(len(raw_data)):
            doc_id = doc_ids[i % len(doc_ids)]
            pid = get_patient_display_id(i)
            age = int(raw_data.iloc[i].get("max_age", 0)) if "max_age" in raw_data.columns else None
            r = str(risk[i])
            diag = diagnosis_for_row(raw_data.iloc[i], r)
            rows.append(
                {
                    "Doctor_ID": doc_id,
                    "Patient_ID": pid,
                    "Patient_Name": patient_name(i),
                    "Age": age,
                    "Diagnosis": diag,
                    "Status": status_from_risk(r),
                    "Risk": r,
                    "Risk_Prob": float(probs[i]),
                }
            )
        assign_df = pd.DataFrame(rows)
        assign_df.to_csv(ASSIGN_PATH, index=False)

    # UI
    st.subheader("ICU Doctors")
    st.dataframe(doctors)

    st.subheader("Assignments")
    selected_doc = st.selectbox("Select doctor", doctors["Doctor_Name"].tolist())
    selected_id = doctors.loc[doctors["Doctor_Name"] == selected_doc, "Doctor_ID"].iloc[0]

    doc_patients = assign_df[assign_df["Doctor_ID"] == selected_id].copy()
    doc_patients = doc_patients.sort_values("Risk_Prob", ascending=False)

    # Show summary cards
    s1, s2, s3 = st.columns(3)
    s1.metric("Assigned patients", len(doc_patients))
    s2.metric("High risk", int((doc_patients["Risk"] == "High").sum()))
    s3.metric("Critical", int((doc_patients["Status"] == "Critical").sum()))

    st.dataframe(
        doc_patients[
            ["Patient_ID", "Patient_Name", "Age", "Diagnosis", "Status", "Risk", "Risk_Prob"]
        ]
    )

# ================= OUTPATIENT RECORDS (PAST PATIENTS) =================

if menu == "Outpatient Records (Past Patients)":
    st.header("Outpatient Records (Past Patients)")
    st.caption("Complete OPD history module (demo storage in CSV).")

    OPD_PATH = PROJECT_DIR / "outpatient_records.csv"
    ensure_csv(
        OPD_PATH,
        [
            "Patient_ID",
            "Patient_Name",
            "Age",
            "Gender",
            "Contact",
            "Visit_Date",
            "Reason_For_Visit",
            "Diagnosis",
            "Treatment_Provided",
            "Prescribed_Medicines",
            "Lab_Test_Results",
            "Doctor_Consulted",
            "Discharge_Final_Diagnosis",
            "Discharge_Treatment_Summary",
            "Discharge_Advice",
            "Follow_Up_Details",
            "Created_At",
        ],
    )
    opd = pd.read_csv(OPD_PATH)

    left, right = st.columns([0.55, 0.45], gap="large")

    with left:
        st.subheader("Add OPD Visit Record")
        pid = st.text_input("Patient ID", value="OPD-00001")
        pname = st.text_input("Name", value="")
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        contact = st.text_input("Contact", placeholder="Phone / email")

        visit_date = st.date_input("Visit date")
        reason = st.text_area("Reason for visit", height=70, placeholder="Symptoms / complaint")
        diagnosis = st.text_area("Diagnosis details", height=70)
        treatment = st.text_area("Treatment provided", height=70)
        meds = st.text_area("Prescribed medicines", height=70, placeholder="Drug • Dose • Frequency • Duration")
        labs = st.text_area("Lab test results (if any)", height=70)
        doc = st.text_input("Doctor consulted", placeholder="e.g., Dr. A. Sharma")

        st.markdown("#### Discharge Summary")
        d_final = st.text_area("Final diagnosis", height=60)
        d_summary = st.text_area("Treatment summary", height=60)
        d_advice = st.text_area("Advice", height=60)
        d_follow = st.text_area("Follow-up details", height=60)

        if st.button("Save OPD Record", type="primary"):
            new_row = {
                "Patient_ID": pid,
                "Patient_Name": pname,
                "Age": int(age),
                "Gender": gender,
                "Contact": contact,
                "Visit_Date": str(visit_date),
                "Reason_For_Visit": reason,
                "Diagnosis": diagnosis,
                "Treatment_Provided": treatment,
                "Prescribed_Medicines": meds,
                "Lab_Test_Results": labs,
                "Doctor_Consulted": doc,
                "Discharge_Final_Diagnosis": d_final,
                "Discharge_Treatment_Summary": d_summary,
                "Discharge_Advice": d_advice,
                "Follow_Up_Details": d_follow,
                "Created_At": now_str(),
            }
            opd = pd.concat([opd, pd.DataFrame([new_row])], ignore_index=True)
            opd.to_csv(OPD_PATH, index=False)
            st.success("Saved OPD record.")

    with right:
        st.subheader("Search / View Past Records")
        q = st.text_input("Search by Patient ID or Name")
        view = opd.copy()
        if q.strip():
            qq = q.strip().lower()
            view = view[
                view["Patient_ID"].astype(str).str.lower().str.contains(qq)
                | view["Patient_Name"].astype(str).str.lower().str.contains(qq)
            ]
        if view.empty:
            card("No results", "Add an OPD visit from the left panel or change the search query.")
        else:
            st.dataframe(view.sort_values("Created_At", ascending=False))

# ================= INPATIENT SUMMARY (IPD) =================

if menu == "Inpatient Summary (IPD)":
    st.header("Inpatient Summary (IPD)")
    st.caption("Admission summary + ongoing treatment + daily progress notes (demo storage in CSV).")

    IPD_ADM_PATH = PROJECT_DIR / "ipd_admissions.csv"
    IPD_MEDS_PATH = PROJECT_DIR / "ipd_medications.csv"
    IPD_NOTES_PATH = PROJECT_DIR / "ipd_progress_notes.csv"

    ensure_csv(
        IPD_ADM_PATH,
        [
            "Patient_ID",
            "Patient_Name",
            "Age",
            "Gender",
            "Assigned_Doctor_ID",
            "Assigned_Doctor_Name",
            "Diagnosis",
            "Admission_Date",
            "Current_Status",
            "Created_At",
        ],
    )
    ensure_csv(
        IPD_MEDS_PATH,
        [
            "Patient_ID",
            "Created_At",
            "Medication",
            "Dose",
            "Route",
            "Frequency",
            "Indication",
            "Prescriber",
            "Notes",
        ],
    )
    ensure_csv(
        IPD_NOTES_PATH,
        [
            "Patient_ID",
            "Created_At",
            "Observation_Date",
            "Progress_Notes",
            "Vitals_Summary",
            "Condition_Status",
            "Doctor",
        ],
    )

    admissions = pd.read_csv(IPD_ADM_PATH)
    meds = pd.read_csv(IPD_MEDS_PATH)
    notes = pd.read_csv(IPD_NOTES_PATH)

    # Use ICU doctors/assignments if available
    DOCTORS_PATH = PROJECT_DIR / "icu_doctors.csv"
    ASSIGN_PATH = PROJECT_DIR / "icu_assignments.csv"
    doctors = pd.read_csv(DOCTORS_PATH) if DOCTORS_PATH.exists() else pd.DataFrame()
    assign_df = pd.read_csv(ASSIGN_PATH) if ASSIGN_PATH.exists() else pd.DataFrame()

    st.subheader("Create / Update Admission Summary")
    left, right = st.columns([0.55, 0.45], gap="large")

    with left:
        if not assign_df.empty:
            pick = st.selectbox("Select ICU patient", assign_df["Patient_ID"].unique().tolist())
            row = assign_df[assign_df["Patient_ID"] == pick].iloc[0].to_dict()
            pid = row.get("Patient_ID", "")
            pname = row.get("Patient_Name", "")
            age = int(row.get("Age", 0) or 0)
        else:
            pid = st.text_input("Patient ID", value="IPD-00001")
            pname = st.text_input("Name", value="")
            age = st.number_input("Age", min_value=0, max_value=120, value=40)

        gender = st.selectbox("Gender", ["Male", "Female"], key="ipd_gender")

        if not doctors.empty:
            doc_name = st.selectbox("Assigned doctor", doctors["Doctor_Name"].tolist())
            doc_id = doctors.loc[doctors["Doctor_Name"] == doc_name, "Doctor_ID"].iloc[0]
        else:
            doc_name = st.text_input("Assigned doctor", value="")
            doc_id = st.text_input("Doctor ID", value="")

        diagnosis = st.text_area("Diagnosis", height=70, placeholder="Primary diagnosis / sepsis source…")
        adm_date = st.date_input("Admission date", key="ipd_adm_date")
        status = st.selectbox("Current status", ["Stable", "Under Observation", "Critical", "Improving", "Deteriorating"])

        if st.button("Save IPD Summary", type="primary"):
            admissions = admissions[admissions["Patient_ID"] != pid]
            new_row = {
                "Patient_ID": pid,
                "Patient_Name": pname,
                "Age": int(age),
                "Gender": gender,
                "Assigned_Doctor_ID": doc_id,
                "Assigned_Doctor_Name": doc_name,
                "Diagnosis": diagnosis,
                "Admission_Date": str(adm_date),
                "Current_Status": status,
                "Created_At": now_str(),
            }
            admissions = pd.concat([admissions, pd.DataFrame([new_row])], ignore_index=True)
            admissions.to_csv(IPD_ADM_PATH, index=False)
            st.success("Saved IPD summary.")

    with right:
        st.subheader("View Admission")
        if admissions.empty:
            card("No admissions yet", "Create an IPD summary from the left panel.")
        else:
            pid_view = st.selectbox("Select admitted patient", admissions["Patient_ID"].tolist(), key="ipd_view_pid")
            adm = admissions[admissions["Patient_ID"] == pid_view].iloc[0].to_dict()
            card(
                f"{adm.get('Patient_ID','')} • {adm.get('Patient_Name','')}",
                f"""
<b>Age:</b> {adm.get('Age','')} • <b>Gender:</b> {adm.get('Gender','')}<br/>
<b>Doctor:</b> {adm.get('Assigned_Doctor_Name','')} ({adm.get('Assigned_Doctor_ID','')})<br/>
<b>Diagnosis:</b> {adm.get('Diagnosis','')}<br/>
<b>Admission date:</b> {adm.get('Admission_Date','')}<br/>
<b>Status:</b> {adm.get('Current_Status','')}
""",
            )

            st.markdown("### Ongoing Medications")
            pm = meds[meds["Patient_ID"] == pid_view].sort_values("Created_At", ascending=False)
            if pm.empty:
                card("No medications", "Add an IPD medication order below.")
            else:
                st.dataframe(pm)

            st.markdown("### Daily Progress Notes")
            pn = notes[notes["Patient_ID"] == pid_view].sort_values("Created_At", ascending=False)
            if pn.empty:
                card("No progress notes", "Add a daily note below.")
            else:
                st.dataframe(pn)

            with st.expander("Add medication / progress note", expanded=True):
                st.markdown("#### Add medication")
                m1, m2 = st.columns(2)
                med_name = m1.text_input("Medication", key="ipd_med_name")
                med_dose = m2.text_input("Dose", key="ipd_med_dose")
                m3, m4, m5 = st.columns(3)
                med_route = m3.selectbox("Route", ["IV", "PO", "IM", "SC", "Other"], key="ipd_med_route")
                med_freq = m4.text_input("Frequency", key="ipd_med_freq", placeholder="e.g., q8h")
                med_ind = m5.text_input("Indication", key="ipd_med_ind")
                med_pres = st.text_input("Prescriber", key="ipd_med_pres", value=adm.get("Assigned_Doctor_Name", ""))
                med_notes = st.text_area("Medication notes", key="ipd_med_notes", height=70)
                if st.button("Save Medication", key="ipd_save_med"):
                    new_m = {
                        "Patient_ID": pid_view,
                        "Created_At": now_str(),
                        "Medication": med_name,
                        "Dose": med_dose,
                        "Route": med_route,
                        "Frequency": med_freq,
                        "Indication": med_ind,
                        "Prescriber": med_pres,
                        "Notes": med_notes,
                    }
                    meds = pd.concat([meds, pd.DataFrame([new_m])], ignore_index=True)
                    meds.to_csv(IPD_MEDS_PATH, index=False)
                    st.success("Saved medication.")

                st.markdown("#### Add daily note")
                obs_date = st.date_input("Observation date", key="ipd_obs_date")
                vitals = st.text_input("Vitals summary", key="ipd_vitals", placeholder="HR, BP, RR, SpO₂…")
                cond = st.selectbox(
                    "Condition",
                    ["Stable", "Under Observation", "Critical", "Improving", "Deteriorating"],
                    key="ipd_cond",
                )
                prog = st.text_area("Progress notes", key="ipd_prog", height=110)
                docn = st.text_input("Doctor", key="ipd_docn", value=adm.get("Assigned_Doctor_Name", ""))
                if st.button("Save Progress Note", key="ipd_save_note"):
                    new_n = {
                        "Patient_ID": pid_view,
                        "Created_At": now_str(),
                        "Observation_Date": str(obs_date),
                        "Progress_Notes": prog,
                        "Vitals_Summary": vitals,
                        "Condition_Status": cond,
                        "Doctor": docn,
                    }
                    notes = pd.concat([notes, pd.DataFrame([new_n])], ignore_index=True)
                    notes.to_csv(IPD_NOTES_PATH, index=False)
                    st.success("Saved progress note.")

# ================= PATIENT CASE HISTORY =================

if menu == "Patient Case History":
    st.header("Patient Case History")

    left, right = st.columns([0.55, 0.45], gap="large")

    with left:
        st.subheader("Create / Update Case History")
        patient_index = st.number_input(
            "Patient Index",
            min_value=0,
            max_value=len(raw_data) - 1,
            step=1,
            help="Use the same index you use in Single Patient predictions.",
        )
        patient_display_id = get_patient_display_id(int(patient_index))
        st.caption(f"Patient ID: **{patient_display_id}**")

        chief = st.text_input("Chief complaint", placeholder="e.g., fever, hypotension, confusion")
        hpi = st.text_area(
            "History of present illness (HPI)",
            placeholder="Timeline of symptoms, onset, progression, recent antibiotics, source suspicion…",
            height=120,
        )
        pmh = st.text_area("Past medical history", placeholder="Comorbidities, surgeries, chronic conditions…", height=90)
        allergies = st.text_input("Allergies", placeholder="e.g., Penicillin (rash)")

        v1, v2, v3 = st.columns(3)
        hr = v1.number_input("HR (bpm)", min_value=0, max_value=250, value=90)
        sbp = v2.number_input("SBP (mmHg)", min_value=0, max_value=300, value=110)
        spo2 = v3.number_input("SpO₂ (%)", min_value=0, max_value=100, value=95)

        l1, l2, l3 = st.columns(3)
        lactate = l1.number_input("Lactate (mmol/L)", min_value=0.0, max_value=30.0, value=1.8, step=0.1)
        wbc = l2.number_input("WBC (×10⁹/L)", min_value=0.0, max_value=100.0, value=9.5, step=0.1)
        creat = l3.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=25.0, value=1.0, step=0.1)

        assessment = st.text_area(
            "Assessment & plan notes",
            placeholder="Working diagnosis, suspected source, planned cultures, fluids, vasopressors, antibiotics, ICU plan…",
            height=120,
        )

        if st.button("Save Case History", type="primary"):
            cases = pd.read_csv(CASE_HISTORY_PATH)
            vitals = f"HR={hr}, SBP={sbp}, SpO2={spo2}"
            labs = f"Lactate={lactate}, WBC={wbc}, Creatinine={creat}"
            new_row = {
                "Patient_ID": patient_display_id,
                "Created_At": now_str(),
                "Chief_Complaint": chief,
                "History_of_Present_Illness": hpi,
                "Past_Medical_History": pmh,
                "Allergies": allergies,
                "Vitals": vitals,
                "Labs": labs,
                "Assessment_Notes": assessment,
            }
            cases = pd.concat([cases, pd.DataFrame([new_row])], ignore_index=True)
            cases.to_csv(CASE_HISTORY_PATH, index=False)
            st.success("Case history saved.")

    with right:
        st.subheader("Latest Case History")
        cases = pd.read_csv(CASE_HISTORY_PATH)
        patient_index2 = st.number_input(
            "Lookup Patient Index",
            min_value=0,
            max_value=len(raw_data) - 1,
            step=1,
            key="case_lookup_index",
        )
        pid2 = get_patient_display_id(int(patient_index2))
        subset = cases[cases["Patient_ID"] == pid2]
        if subset.empty:
            card("No case history yet", "Create one from the left panel. Saved entries will appear here.")
        else:
            last = subset.tail(1).iloc[0].to_dict()
            card(
                f"{pid2} • {last.get('Created_At','')}",
                f"""
<b>Chief complaint:</b> {last.get('Chief_Complaint','')}<br/>
<b>Allergies:</b> {last.get('Allergies','')}<br/><br/>
<b>Vitals:</b> {last.get('Vitals','')}<br/>
<b>Labs:</b> {last.get('Labs','')}<br/><br/>
<b>HPI:</b> {last.get('History_of_Present_Illness','')}<br/><br/>
<b>PMH:</b> {last.get('Past_Medical_History','')}<br/><br/>
<b>Assessment:</b> {last.get('Assessment_Notes','')}
""",
            )
            with st.expander("View all entries for this patient"):
                st.dataframe(subset.sort_values("Created_At", ascending=False))

# ================= PRESCRIPTIONS =================

if menu == "Prescriptions":
    st.header("Prescriptions")

    left, right = st.columns([0.55, 0.45], gap="large")

    with left:
        st.subheader("Write a Prescription")
        patient_index = st.number_input(
            "Patient Index",
            min_value=0,
            max_value=len(raw_data) - 1,
            step=1,
            key="rx_patient_index",
        )
        patient_display_id = get_patient_display_id(int(patient_index))
        st.caption(f"Patient ID: **{patient_display_id}**")

        c1, c2 = st.columns(2)
        medication = c1.text_input("Medication", placeholder="e.g., Piperacillin/Tazobactam")
        dose = c2.text_input("Dose", placeholder="e.g., 4.5 g")

        c3, c4, c5 = st.columns(3)
        route = c3.selectbox("Route", ["IV", "PO", "IM", "SC", "Other"])
        frequency = c4.text_input("Frequency", placeholder="e.g., q6h")
        duration = c5.text_input("Duration", placeholder="e.g., 7 days")

        indication = st.text_input("Indication", placeholder="e.g., suspected septic shock - source unknown")
        prescriber = st.text_input("Prescriber", placeholder="e.g., Dr. A. Kumar")
        notes = st.text_area("Notes", placeholder="Renal dosing, culture follow-up, monitor LFTs…", height=100)

        if st.button("Save Prescription", type="primary"):
            rx = pd.read_csv(PRESCRIPTIONS_PATH)
            new_row = {
                "Patient_ID": patient_display_id,
                "Created_At": now_str(),
                "Medication": medication,
                "Dose": dose,
                "Route": route,
                "Frequency": frequency,
                "Duration": duration,
                "Indication": indication,
                "Prescriber": prescriber,
                "Notes": notes,
            }
            rx = pd.concat([rx, pd.DataFrame([new_row])], ignore_index=True)
            rx.to_csv(PRESCRIPTIONS_PATH, index=False)
            st.success("Prescription saved.")

    with right:
        st.subheader("Medication List")
        rx = pd.read_csv(PRESCRIPTIONS_PATH)
        patient_index2 = st.number_input(
            "Lookup Patient Index",
            min_value=0,
            max_value=len(raw_data) - 1,
            step=1,
            key="rx_lookup_index",
        )
        pid2 = get_patient_display_id(int(patient_index2))
        subset = rx[rx["Patient_ID"] == pid2]
        if subset.empty:
            card("No prescriptions yet", "Write a prescription from the left panel. Saved orders will appear here.")
        else:
            st.dataframe(subset.sort_values("Created_At", ascending=False))
            last = subset.sort_values("Created_At", ascending=False).head(1).iloc[0].to_dict()
            card(
                f"Latest order • {pid2}",
                f"""
<b>{last.get('Medication','')}</b> — {last.get('Dose','')} {last.get('Route','')}<br/>
<b>Frequency:</b> {last.get('Frequency','')} • <b>Duration:</b> {last.get('Duration','')}<br/>
<b>Indication:</b> {last.get('Indication','')}<br/>
<b>Prescriber:</b> {last.get('Prescriber','')}<br/>
<b>Notes:</b> {last.get('Notes','')}
""",
            )

# ================= SINGLE PATIENT =================

if menu == "Single Patient":

    st.header("Single Patient Prediction")
    st.subheader("Select Patient")

    live_mode = st.toggle("Live vitals (simulated)", value=True, help="Simulates real-time bedside monitor drift.")

    patient_id = st.number_input(
        "Enter Patient Index",
        min_value=0,
        max_value=len(X)-1,
        step=1
    )

    # Show patient data
    if st.button("Load Patient Data"):
        patient_row = raw_display.iloc[int(patient_id)]
        st.write(patient_row)

    gender = st.selectbox("Gender", ["Male", "Female"])

    # Predict button
    if st.button("Predict Risk"):

        x_row = X.iloc[[int(patient_id)]]
        prob = float(model.predict_proba(x_row)[0][1])
        risk_level = risk_label(prob)

        st.subheader("Patient Clinical Summary")

        c1, c2, c3 = st.columns(3)

        c1.metric("Patient ID", get_patient_display_id(int(patient_id)))
        age_val = float(x_row["max_age"].values[0]) if "max_age" in x_row.columns else np.nan
        sofa_val = float(x_row["sofa_score"].values[0]) if "sofa_score" in x_row.columns else np.nan
        c2.metric("Age", int(age_val) if np.isfinite(age_val) else "—")
        c3.metric("SOFA Score", round(sofa_val, 2) if np.isfinite(sofa_val) else "—")

        c4, c5, c6 = st.columns(3)

        spo2_val = float(x_row["spo2_mean"].values[0]) if "spo2_mean" in x_row.columns else np.nan
        hr_val = float(x_row["heart_rate_mean"].values[0]) if "heart_rate_mean" in x_row.columns else np.nan
        alb_val = float(x_row["albumin"].values[0]) if "albumin" in x_row.columns else np.nan

        if live_mode:
            spo2_val = jitter(spo2_val, pct=0.02, low=70, high=100)
            hr_val = jitter(hr_val, pct=0.06, low=30, high=220)
            alb_val = jitter(alb_val, pct=0.03, low=0, high=6)

        c4.metric("SpO₂", round(spo2_val, 2) if np.isfinite(spo2_val) else "—")
        c5.metric("Heart Rate", round(hr_val, 2) if np.isfinite(hr_val) else "—")
        c6.metric("Albumin", round(alb_val, 2) if np.isfinite(alb_val) else "—")

        st.markdown(risk_banner_html(risk_level), unsafe_allow_html=True)

        st.write("Probability:", round(prob,3))

        # Save prediction history
        history = pd.read_csv(PRED_HISTORY_PATH)

        new_row = {
            "Patient_ID": get_patient_display_id(int(patient_id)),
            "Risk": risk_level,
            "Probability": round(prob,3),
            "Date": now_str()
        }

        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
        history.to_csv(PRED_HISTORY_PATH, index=False)

        with st.expander("Patient Case History + Prescriptions (workflow view)", expanded=True):
            pid = get_patient_display_id(int(patient_id))
            cases = pd.read_csv(CASE_HISTORY_PATH)
            rx = pd.read_csv(PRESCRIPTIONS_PATH)
            ctab, rtab = st.tabs(["Case History", "Prescriptions"])
            with ctab:
                subset = cases[cases["Patient_ID"] == pid]
                if subset.empty:
                    card("No case history found", "Open the **Patient Case History** module to create it.")
                else:
                    st.dataframe(subset.sort_values("Created_At", ascending=False))
            with rtab:
                subset = rx[rx["Patient_ID"] == pid]
                if subset.empty:
                    card("No prescriptions found", "Open the **Prescriptions** module to add medication orders.")
                else:
                    st.dataframe(subset.sort_values("Created_At", ascending=False))
# ================= BATCH DASHBOARD =================

if menu == "Batch Dashboard":

    st.markdown(
        """<div class="card anim-in"><div class="card-title">Hospital Patient Risk Dashboard (250 Patients)</div><div class="muted">Population-level view for ICU triage.</div></div>""",
        unsafe_allow_html=True,
    )

    probs = model.predict_proba(X)[:, 1]

    df = raw_data.copy()
    df["Risk_Prob"] = probs
    df["Risk_Level"] = df["Risk_Prob"].apply(risk_label)

    high = df[df["Risk_Level"] == "High"]
    med = df[df["Risk_Level"] == "Medium"]
    low = df[df["Risk_Level"] == "Low"]

    # ICU Alert System
    if len(high) > 0:
        st.error(f"🚨 ALERT: {len(high)} High-Risk Sepsis Patients Detected in ICU")
    else:
        st.success("✅ No Critical Sepsis Patients Detected")

    # Metrics
    c1,c2,c3 = st.columns(3)
    c1.metric("High Risk", len(high))
    c2.metric("Medium Risk", len(med))
    c3.metric("Low Risk", len(low))

    # Charts (professional)
    chart_df = (
        df["Risk_Level"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
        .rename_axis("Risk")
        .reset_index(name="Patients")
    )

    ch1, ch2 = st.columns([0.42, 0.58], gap="large")
    with ch1:
        fig_donut = px.pie(
            chart_df,
            names="Risk",
            values="Patients",
            hole=0.55,
            color="Risk",
            color_discrete_map=RISK_COLOR_MAP,
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="rgba(255,255,255,0.85)", width=2)),
        )
        fig_donut.update_layout(
            title="Risk mix",
            legend_title_text="",
            margin=dict(l=10, r=10, t=45, b=10),
            height=320,
            template="plotly_white",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with ch2:
        fig_bar = px.bar(
            chart_df,
            x="Risk",
            y="Patients",
            color="Risk",
            color_discrete_map=RISK_COLOR_MAP,
            text="Patients",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            title="Patients by risk",
            showlegend=False,
            margin=dict(l=10, r=10, t=45, b=10),
            height=320,
            xaxis_title="",
            yaxis_title="Patients",
            template="plotly_white",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 🔥 RISK FILTER (INSIDE BLOCK)
    risk_choice = st.multiselect(
        "Select Risk Level to Display",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )

    filtered_df = df[df["Risk_Level"].isin(risk_choice)]

    st.subheader("Patient Details (Selected Risk Levels)")
    st.dataframe(filtered_df.sort_values("Risk_Prob", ascending=False))
    st.subheader("🚨 Top 10 Critical ICU Patients")

    critical = df.sort_values("Risk_Prob", ascending=False).head(10)

    st.dataframe(critical)









# ================= ICU SPECIALIZATION ANALYSIS =================

if menu == "ICU Specialization Analysis":

    st.markdown(
        """<div class="card anim-in"><div class="card-title">ICU Organ Failure Specialization Analysis</div><div class="muted">Risk distribution views based on key organ-related indicators.</div></div>""",
        unsafe_allow_html=True,
    )

    probs = model.predict_proba(X)[:, 1]
    df = raw_data.copy()
    df["Risk_Prob"] = probs
    df["Risk_Level"] = df["Risk_Prob"].apply(risk_label)

    missing_for_organs = [
        c
        for c in ["heart_rate_mean", "spo2_mean", "sofa_score", "albumin"]
        if c not in df.columns
    ]
    if missing_for_organs:
        st.warning(
            "Some required columns are missing for organ analysis: "
            + ", ".join(missing_for_organs)
        )
        st.stop()

    df["Heart_Risk"] = pd.cut(
        df["heart_rate_mean"], bins=[0, 80, 110, 200], labels=["Low", "Medium", "High"]
    )

    df["Lung_Risk"] = pd.cut(
        df["spo2_mean"], bins=[0, 90, 95, 100], labels=["High", "Medium", "Low"]
    )

    df["Kidney_Risk"] = pd.cut(
        df["sofa_score"], bins=[0, 5, 10, 25], labels=["Low", "Medium", "High"]
    )

    df["Liver_Risk"] = pd.cut(
        df["albumin"], bins=[0, 2.5, 3.5, 5], labels=["High", "Medium", "Low"]
    )


    organ = st.selectbox(
        "Select Organ Failure Analysis",
        ["Heart", "Lung", "Kidney", "Liver"]
    )


    if organ == "Heart":
        col = "Heart_Risk"

    elif organ == "Lung":
        col = "Lung_Risk"

    elif organ == "Kidney":
        col = "Kidney_Risk"

    else:
        col = "Liver_Risk"


    risk_counts = df[col].value_counts()

    st.subheader(f"{organ} Failure Risk Distribution")

    organ_df = (
        risk_counts.reindex(["High", "Medium", "Low"])
        .dropna()
        .rename_axis("Risk")
        .reset_index(name="Patients")
        .sort_values("Patients", ascending=False)
    )

    o1, o2 = st.columns([0.42, 0.58], gap="large")
    with o1:
        fig_o_donut = px.pie(
            organ_df,
            names="Risk",
            values="Patients",
            hole=0.55,
            color="Risk",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
        )
        fig_o_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="rgba(255,255,255,0.85)", width=2)),
        )
        fig_o_donut.update_layout(
            title=f"{organ} distribution",
            legend_title_text="",
            margin=dict(l=10, r=10, t=45, b=10),
            height=320,
            template="plotly_white",
        )
        st.plotly_chart(fig_o_donut, use_container_width=True)

    with o2:
        fig_o_bar = px.bar(
            organ_df,
            x="Risk",
            y="Patients",
            color="Risk",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
            text="Patients",
        )
        fig_o_bar.update_traces(textposition="outside")
        fig_o_bar.update_layout(
            title="Patients by risk (organ)",
            showlegend=False,
            margin=dict(l=10, r=10, t=45, b=10),
            height=320,
            xaxis_title="",
            yaxis_title="Patients",
            template="plotly_white",
        )
        st.plotly_chart(fig_o_bar, use_container_width=True)

    st.subheader("Risk Data Summary")
    st.dataframe(risk_counts.reset_index().rename(columns={"index":"Risk Level", col:"Patients"}))


    # 🔹 Risk Filter (like batch dashboard)

    risk_choice = st.multiselect(
        "Select Risk Level to Display Patients",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )

    filtered_df = df[df[col].isin(risk_choice)]

    st.subheader(f"{organ} Risk Patients Details")

    st.dataframe(filtered_df)
# ================= PREDICTION HISTORY =================

if menu == "Prediction History":

    st.header("Prediction History")

    history = pd.read_csv(PRED_HISTORY_PATH)

    st.write("Total Predictions:", len(history))

    st.dataframe(history)

    st.download_button(
        label="Download Prediction History",
        data=history.to_csv(index=False),
        file_name="prediction_history.csv",
        mime="text/csv"
    )
# ================= AI EXPLANATION =================
# Prepare dataframe for AI explanation
df = X.copy()
df["Risk_Prob"] = model.predict_proba(X)[:, 1]
df["Risk_Level"] = df["Risk_Prob"].apply(risk_label)

if menu == "AI Explanation":

    st.header("Mini AI Explanation (Demo)")

    idx = st.number_input("Enter patient index", min_value=0, max_value=len(df)-1)

    if st.button("Explain Risk"):

        risk = df.iloc[idx]["Risk_Level"]
        prob = df.iloc[idx]["Risk_Prob"]

        st.write(f"### Patient Risk Level: {risk}")
        st.write(f"### Risk Probability: {prob:.2f}")

        patient = df.iloc[idx]

        reasons = []

        if patient["sofa_score"] > 8:
            reasons.append("High SOFA score indicating organ dysfunction")

        if patient["heart_rate_mean"] > 110:
            reasons.append("Elevated heart rate indicating physiological stress")

        if patient["spo2_mean"] < 92:
            reasons.append("Low oxygen saturation affecting respiratory stability")

        if patient["albumin"] < 3:
            reasons.append("Low albumin levels indicating poor clinical condition")

        if patient["max_age"] > 70:
            reasons.append("Advanced age increasing sepsis vulnerability")

        st.subheader("Clinical Factors Influencing Risk")

        if len(reasons) == 0:
            st.write("No major abnormal indicators detected.")
        else:
            for r in reasons:
                st.write("•", r)

        # Final interpretation

        if risk == "High":
            st.error("Overall Interpretation: Multiple abnormal clinical indicators suggest severe sepsis and high mortality risk.")

        elif risk == "Medium":
            st.warning("Overall Interpretation: Some physiological indicators are unstable, requiring close monitoring.")

        else:
            st.success("Overall Interpretation: Patient vitals appear stable with low indicators of severe sepsis.")

        # Feature Importance Section
        st.subheader("Model Feature Importance")

    importance = model.get_booster().get_score(importance_type="weight")

    imp_df = pd.DataFrame({
        "Feature": list(importance.keys()),
        "Importance": list(importance.values())
    })

    imp_df = imp_df.sort_values("Importance", ascending=False)

    st.dataframe(imp_df)

    fig, ax = plt.subplots(figsize=(6,4))
    ax.barh(imp_df["Feature"][:10], imp_df["Importance"][:10])
    ax.invert_yaxis()

    st.pyplot(fig)


# ================= MODEL INFO =================

if menu == "Model Info":

    st.subheader("System Overview")

    st.info("""
    Model: XGBoost Classifier
    Application: Sepsis Mortality Prediction
    Purpose: ICU Risk Monitoring and Early Clinical Decision Support
    """)

    st.header("Model Information")

    st.write("""
    • Algorithm: XGBoost  
    • Dataset Size: 250 ICU Patients  
    • Accuracy: ~84%  
    • Purpose: Early Sepsis Mortality Detection  
    • Output: High / Medium / Low Risk  

    This system assists doctors in prioritizing critical patients.
    """)

