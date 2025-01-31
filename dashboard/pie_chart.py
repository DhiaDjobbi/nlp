import streamlit as st
import plotly.express as px

def render_pie_chart(df):
    """
    Renders a pie chart for sentiment distribution using Plotly.

    Args:
        df (pd.DataFrame): The DataFrame containing sentiment data.

    Returns:
        plotly.graph_objs._figure.Figure: The Plotly figure object for the pie chart.
    """
    if df is not None and "sentiment" in df.columns:
        # Calculate sentiment percentages
        sentiment_counts = df["sentiment"].value_counts(normalize=True) * 100
        pie_chart_data = sentiment_counts.reset_index()
        pie_chart_data.columns = ["Sentiment", "Percentage"]

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

        return fig_pie
    else:
        st.warning("No sentiment data found to render the pie chart.")
        return None