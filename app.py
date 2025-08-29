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

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file with URLs", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Check if the CSV has at least one column
        if df.shape[1] == 0:
            st.error("CSV file is empty.")
        else:
            urls = df.iloc[:, 0].dropna().tolist()

            st.write(f"Found **{len(urls)}** URLs to check.")
            st.write("Checking... please wait ⏳")

            # Run concurrent checks
            results = []
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(url_response, urls))

            # Show results in table
            results_df = pd.DataFrame(results, columns=["URL", "Status"])
            #  Convert Status to string to avoid ArrowTypeError
            results_df["Status"] = results_df["Status"].astype(str)
            st.dataframe(results_df)

            # Option to download results
            csv_results = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_results,
                file_name="url_check_results.csv",
                mime="text/csv",
            )
    except Exception as e:
        st.error(f"Error reading file: {e}")
