import streamlit as st
import sys
import time
import datetime
from io import StringIO
import contextlib
from mypipeline import run_full_pipeline  # Import your pipeline function

# Function to capture logs in real-time
class RealTimeLogger(StringIO):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback

    def write(self, msg):
        if msg.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_msg = f"[{timestamp}] {msg}"
            super().write(formatted_msg)
            self.log_callback(formatted_msg)

# Function to run the pipeline and stream logs
def run_pipeline(site_to_scrap, log_callback):
    log_stream = RealTimeLogger(log_callback)
    old_stdout = sys.stdout
    sys.stdout = log_stream
    try:
        result_file = run_full_pipeline(site_to_scrap)
        print(f"Final results saved to: {result_file}")
    finally:
        sys.stdout = old_stdout

# Streamlit UI
st.title("NLP Pipeline with Streamlit")

# Input field for the site to review
site_to_scrap = st.text_input("Enter the site to review (e.g., sendle.com):")

# Button to trigger the pipeline
if st.button("Run Pipeline2"):
    if site_to_scrap:
        st.write(f"Running pipeline for site: {site_to_scrap}")
        st.subheader("Pipeline Logs")
        logs_placeholder = st.empty()  # Placeholder for logs

        logs = []  # Store logs

        def update_logs(new_log):
            logs.append(new_log)
            logs_placeholder.text_area("Logs", "\n".join(logs), height=300)

        run_pipeline(site_to_scrap, update_logs)
    else:
        st.warning("Please enter a site to review.")
