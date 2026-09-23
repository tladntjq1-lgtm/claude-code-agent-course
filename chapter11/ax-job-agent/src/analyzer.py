def analyze_jobs(df_clean, new_jobs):
    return {
        "total_count": len(df_clean),
        "new_count": len(new_jobs),
        "top_companies": df_clean["company_name"].value_counts().head(5),
        "top_locations": df_clean["location"].value_counts().head(5),
        "career_distribution": df_clean["career"].value_counts(),
    }
