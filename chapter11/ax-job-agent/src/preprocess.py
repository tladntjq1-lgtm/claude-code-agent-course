import os

import pandas as pd


def clean_jobs(df):
    df_clean = df.drop_duplicates(subset=["job_url"]).copy()
    df_clean["career"] = df_clean["career"].fillna("정보없음")
    return df_clean


def find_new_jobs(df_clean, history_path="data/processed/jobs_history.csv"):
    if os.path.exists(history_path):
        history_df = pd.read_csv(history_path)
        known_urls = set(history_df["job_url"])
    else:
        history_df = pd.DataFrame(columns=df_clean.columns)
        known_urls = set()

    is_new = ~df_clean["job_url"].isin(known_urls)
    new_jobs = df_clean[is_new].copy()

    updated_history = pd.concat([history_df, df_clean], ignore_index=True)
    updated_history = updated_history.drop_duplicates(subset=["job_url"])
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    updated_history.to_csv(history_path, index=False)

    return new_jobs
