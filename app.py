import streamlit as st

# Set the page layout to wide
st.set_page_config(layout="wide")

import sys
import os
import time
import datetime
from io import StringIO
import contextlib
from mypipeline import run_full_pipeline

import pandas as pd
import plotly.express as px
import pycountry
import scipy.stats as stats

from dashboard.pie_chart import render_pie_chart
from dashboard.bar_chart import render_bar_chart

# Apply custom CSS styling globally
st.markdown(
    """
    <style>
    .stTextArea textarea {
        background-color: black !important;
        color: white !important;
    }
    .stTextArea textarea::-webkit-scrollbar {
        width: 16px;  /* Increase the width of the scrollbar */
    }
    .stTextArea textarea::-webkit-scrollbar-thumb {
        background: #888;  /* Color of the scrollbar thumb */
    }
    .stTextArea textarea::-webkit-scrollbar-thumb:hover {
        background: #555;  /* Color of the scrollbar thumb on hover */
    }
    .stColumn {
        border: 1px solid gray !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        return result_file
    finally:
        sys.stdout = old_stdout

def render_rating_distribution_by_month(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['month'] = df['date'].dt.strftime('%B %Y')
    monthly_distribution = df.groupby('month')['rating'].count().reset_index()
    monthly_distribution.columns = ['Month', 'Rating Count']
    monthly_distribution['Month'] = pd.to_datetime(monthly_distribution['Month'])
    monthly_distribution = monthly_distribution.sort_values('Month')

    fig_month = px.bar(
        monthly_distribution,
        x='Month',
        y='Rating Count',
        title='Rating Distribution by Month',
        labels={'Month': 'Month', 'Rating Count': 'Number of Ratings'},
        color='Rating Count',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_month.update_layout(xaxis_title='Month', yaxis_title='Number of Ratings')
    return fig_month

def render_reviews_heatmap(df):
    # Convert country codes to country names
    df['country_name'] = df['country'].apply(lambda code: pycountry.countries.get(alpha_2=code).name if pycountry.countries.get(alpha_2=code) else code)
    country_distribution = df['country_name'].value_counts().reset_index()
    country_distribution.columns = ['Country', 'Review Count']

    fig_map = px.choropleth(
        country_distribution,
        locations='Country',
        locationmode='country names',
        color='Review Count',
        hover_name='Country',
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Reviews Heatmap by Country'
    )
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular',
            bgcolor='black'
        ),
        paper_bgcolor='#0e1117',  # Set the paper background color to match
    )
    return fig_map

def calculate_metrics(df):
    total_reviews = len(df)
    
    most_positive_country = df[df['rating'] == df['rating'].max()]['country'].mode()[0]
    most_negative_country = df[df['rating'] == df['rating'].min()]['country'].mode()[0]
    
    # Ensure most positive and most negative countries are not the same
    if most_positive_country == most_negative_country:
        second_most_negative_country = df[df['rating'] == df['rating'].min()]['country'].value_counts().index[1]
        most_negative_country = second_most_negative_country
    
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    peak_review_hours = df['hour'].mode()[0]
    peak_review_period = "AM" if peak_review_hours < 12 else "PM"
    peak_review_hours = peak_review_hours % 12 if peak_review_hours > 12 else peak_review_hours
    
    return total_reviews, most_positive_country, most_negative_country, peak_review_hours, peak_review_period

def get_country_flag_url(country_code):
    return f"https://flagsapi.com/{country_code}/flat/64.png"

# Streamlit UI
# st.set_page_config(layout="wide")  # Set the page layout to wide

st.markdown('<div class="center"><img src="https://i.imgur.com/eW1zzCH.png" width="200"/></div>', unsafe_allow_html=True)

st.title("DeliverMind: NLP Review Analysis Dashboard")

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
            result_file = run_pipeline(site_to_scrap, update_logs)

            # Once the pipeline finishes, load the result DataFrame
            st.write("Pipeline finished. Loading results...")
            df = pd.read_csv(result_file)  # Assuming the pipeline saves results to a CSV file

            # Calculate metrics
            total_reviews, most_positive_country, most_negative_country, peak_review_hours, peak_review_period = calculate_metrics(df)

            # Display metrics cards
            st.subheader("Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Reviews", total_reviews)
            
            positive_flag_url = get_country_flag_url(most_positive_country)
            negative_flag_url = get_country_flag_url(most_negative_country)
            
            col2.markdown(f"Most Positive Country: {most_positive_country} ![flag]({positive_flag_url})")
            col3.markdown(f"Most Negative Country: {most_negative_country} ![flag]({negative_flag_url})")
            col4.metric("Peak Review Hours", f"{peak_review_hours}:00 - {peak_review_hours + 1}:00 {peak_review_period}")

            # Render the charts in real-time
            fig_pie = render_pie_chart(df)
            fig_bar = render_bar_chart(df)
            fig_month = render_rating_distribution_by_month(df)
            fig_map = render_reviews_heatmap(df)

            if fig_pie and fig_bar:
                col1, col2 = st.columns([0.6, 0.4])
                with col1:
                    st.plotly_chart(fig_bar, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            st.plotly_chart(fig_month, use_container_width=True)
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Please enter a site to review.")
