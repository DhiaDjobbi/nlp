import streamlit as st
import sys
import os
import time
import datetime
from io import StringIO
import contextlib
from mypipeline import run_full_pipeline  # Import your pipeline function

import pandas as pd
import plotly.express as px

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
if st.button("Run Pipeline"):
    if site_to_scrap:
        # Display the "Running pipeline" message with a spinner
        with st.spinner(f"Running pipeline for site: {site_to_scrap}..."):
            st.subheader("Pipeline Logs")
            logs_placeholder = st.empty()  # Placeholder for logs

            logs = []  # Store logs

            def update_logs(new_log):
                logs.append(new_log)
                logs_placeholder.text_area("Logs", "\n".join(logs), height=300)

            # Run the pipeline
            run_pipeline(site_to_scrap, update_logs)

            # Wait for the pipeline to finish and check for the pie chart data file
            pie_chart_data_path = "streamlit_folder/pie_chart_data.csv"
            bar_chart_data_path = "streamlit_folder/bar_chart_data.csv"
            st.write("Waiting for pipeline to finish...")
            while not (os.path.exists(pie_chart_data_path) and os.path.exists(bar_chart_data_path)):
                time.sleep(1)  # Wait for 1 second before checking again

            # Once the files exist, load and display the pie chart
            st.write("Pipeline finished. Loading charts...")
            
            # Load and display the pie chart
            pie_chart_data = pd.read_csv(pie_chart_data_path)

            # Define custom colors for the pie chart
            color_map = {
                "NEGATIVE": "#FF6B6B",  # Soft red
                "NEUTRAL": "#FFD166",   # Soft yellow/orange
                "POSITIVE": "#4CAF50"   # Soft green
            }

            # Create a pie chart using Plotly with custom colors
            fig_pie = px.pie(
                pie_chart_data, 
                values="Percentage", 
                names="Sentiment", 
                title="Sentiment Distribution",
                color="Sentiment",  # Use the 'Sentiment' column for coloring
                color_discrete_map=color_map  # Apply the custom color map
            )

            # Update layout for a cleaner look
            fig_pie.update_traces(
                textposition="inside", 
                textinfo="percent+label",  # Show percentage and label inside slices
                hole=0.3  # Add a hole in the middle for a donut chart effect
            )
            fig_pie.update_layout(
                showlegend=True,  # Show legend
                legend_title_text="Sentiment",  # Legend title
                font=dict(size=14)  # Increase font size for better readability
            )

            # Display the pie chart in Streamlit
            st.plotly_chart(fig_pie)

            # Load and display the bar chart
            bar_chart_data = pd.read_csv(bar_chart_data_path)

            # Create a bar chart using Plotly
            fig_bar = px.bar(
                bar_chart_data, 
                x="Theme", 
                y="Count", 
                title="Theme Distribution",
                labels={"Count": "Number of Occurrences", "Theme": "Themes"},
                color="Theme",  # Use the 'Theme' column for coloring
                color_discrete_sequence=px.colors.qualitative.Pastel  # Use a professional color palette
            )

            # Update layout for a cleaner look
            fig_bar.update_layout(
                xaxis_title="Themes",
                yaxis_title="Number of Occurrences",
                showlegend=False,  # Hide legend for simplicity
                font=dict(size=14)  # Increase font size for better readability
            )

            # Display the bar chart in Streamlit
            st.plotly_chart(fig_bar)
    else:
        st.warning("Please enter a site to review.")


# monthes with lowest reviews
# monsthes with highest review