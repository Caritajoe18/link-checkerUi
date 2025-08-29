import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

def url_response(url):
    """Send a HEAD request and return the status."""
    try:
        status = requests.head(url, allow_redirects=True, timeout=10).status_code
        return url, status
    except requests.RequestException:
        return url, "Not found"

st.title("🔗 Bulk URL Checker")

# --- Input section ---
st.subheader("1️Provide URLs")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file with URLs", type=["csv"])

# Text area for copy-paste
pasted_urls = st.text_area(
    "Or paste URLs here (one per line)",
    placeholder="https://example.com\nhttps://openai.com"
)

# --- Submit button ---
if st.button("Check"):
    urls = []

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.shape[1] == 0:
                st.error("CSV file is empty.")
            else:
                urls.extend(df.iloc[:, 0].dropna().tolist())
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if pasted_urls.strip():
        urls.extend([u.strip() for u in pasted_urls.splitlines() if u.strip()])

    if not urls:
        st.warning("Please upload a CSV or paste some URLs.")
    else:
        st.write(f"Found **{len(urls)}** URLs to check.")
        st.write("Checking... please wait")

        # Run concurrent checks
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(url_response, urls))

        # Show results
        results_df = pd.DataFrame(results, columns=["URL", "Status"])
        results_df["Status"] = results_df["Status"].astype(str)
        st.dataframe(results_df)

        # Download option
        csv_results = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv_results,
            file_name="url_check_results.csv",
            mime="text/csv",
        )
