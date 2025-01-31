import streamlit as st
import sys
import os
import time
import datetime
from io import StringIO
import contextlib
from mypipeline import run_full_pipeline

import pandas as pd
import plotly.express as px

from dashboard.pie_chart import render_pie_chart
from dashboard.bar_chart import render_bar_chart

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
st.set_page_config(layout="wide")  # Set the page layout to wide

st.title("NLP Pipeline with Streamlit")

# Input field for the site to review
site_to_scrap = st.text_input("Enter the site to review (e.g., sendle.com):")

# Button to trigger the pipeline
if st.button("Run Pipeline"):
    if site_to_scrap:
        # Display the "Running pipeline" message with a spinner
        with st.spinner(f"Running pipeline for site: {site_to_scrap}..."):
            st.subheader("Pipeline Logs")
            logs_placeholder = st.empty()  # Placeholder for logs

            logs = []  # Store logs

            def update_logs(new_log):
                logs.append(new_log)
                st.markdown(
                    """
                    <style>
                    .stTextArea textarea {
                        background-color: black !important;
                        color: white !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                logs_placeholder.text_area("Logs", "\n".join(logs), height=300)

            # Run the pipeline
            run_pipeline(site_to_scrap, update_logs)

            # Wait for the pipeline to finish and get the result DataFrame
            waiting_message = st.empty()
            waiting_message.write("Waiting for pipeline to finish...")
            result_file = None
            while result_file is None:
                time.sleep(1)  # Wait for 1 second before checking again
                try:
                    result_file = run_full_pipeline(site_to_scrap)  # Replace with your actual pipeline output
                except Exception as e:
                    st.warning(f"Pipeline not finished yet: {e}")

            # Once the pipeline finishes, load the result DataFrame
            waiting_message.empty()
            st.write("Pipeline finished. Loading results...")
            df = pd.read_csv(result_file)  # Assuming the pipeline saves results to a CSV file

            # Render the charts in real-time
            fig_pie = render_pie_chart(df)
            fig_bar = render_bar_chart(df)

            if fig_pie and fig_bar:
                col1, col2 = st.columns([0.6, 0.4])
                with col1:
                    st.plotly_chart(fig_bar, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Please enter a site to review.")

# monthes with lowest reviews
# monsthes with highest review
