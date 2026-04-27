import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
RAW_PATH = PROJECT_DIR / "Data_after_Cleaning.csv"
OUT_PATH = PROJECT_DIR / "Data_after_Cleaning_fixed.csv"


def main():
    df = pd.read_csv(RAW_PATH)

    # Drop obvious non-feature columns (index/id-like)
    drop_cols = [c for c in ["Unnamed: 0", "subject_id"] if c in df.columns]

    # Drop constant columns (no information)
    nunique = df.nunique(dropna=False)
    drop_cols += [c for c in nunique[nunique <= 1].index.tolist() if c not in ["hospital_expire_flag"]]

    df = df.drop(columns=sorted(set(drop_cols)), errors="ignore")

    # Convert bool -> int for compatibility with some tooling
    for c in df.columns:
        if df[c].dtype == "bool":
            df[c] = df[c].astype("int64")

    # Basic sanity: ensure target exists and is 0/1
    if "hospital_expire_flag" not in df.columns:
        raise ValueError("Expected target column 'hospital_expire_flag' not found.")
    if not set(df["hospital_expire_flag"].unique()).issubset({0, 1, True, False}):
        raise ValueError("Unexpected values in 'hospital_expire_flag'. Expected binary 0/1.")
    df["hospital_expire_flag"] = df["hospital_expire_flag"].astype("int64")

    # Keep column order stable (target last)
    cols = [c for c in df.columns if c != "hospital_expire_flag"] + ["hospital_expire_flag"]
    df = df[cols]

    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote: {OUT_PATH}")
    print("shape:", df.shape)
    print("dtypes:", df.dtypes.value_counts().to_dict())


if __name__ == "__main__":
    main()

