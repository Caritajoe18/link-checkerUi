import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

def url_response(url):
    """Send a HEAD request and return the status."""
    try:
        status = requests.head(url, allow_redirects=True, timeout=10).status_code
        return url.strip(), status
    except requests.RequestException:
        return url.strip(), "Not found"

st.title("🔗 Bulk URL Checker")

st.write("You can either **upload a CSV file** or **paste URLs manually** (one per line).")

# --- Option 1: File uploader ---
uploaded_file = st.file_uploader("Upload a CSV file with URLs", type=["csv"])

# --- Option 2: Textarea input ---
pasted_urls = st.text_area("Or paste URLs here (one per line)", height=150)

urls = []

# Handle uploaded CSV
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if df.shape[1] == 0:
            st.error("CSV file is empty.")
        else:
            urls = df.iloc[:, 0].dropna().tolist()
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Handle pasted URLs
if pasted_urls.strip():
    urls.extend([u.strip() for u in pasted_urls.splitlines() if u.strip()])

# Remove duplicates
urls = list(dict.fromkeys(urls))

# Run checks if we have URLs
if urls:
    st.write(f"Found **{len(urls)}** URLs to check.")
    st.write("Checking... please wait ⏳")

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(url_response, urls))

    results_df = pd.DataFrame(results, columns=["URL", "Status"])
    results_df["Status"] = results_df["Status"].astype(str)  # Fix mixed types

    st.dataframe(results_df)

    # Download option
    csv_results = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_results,
        file_name="url_check_results.csv",
        mime="text/csv",
    )
