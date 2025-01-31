import streamlit as st
import plotly.express as px

def render_bar_chart(df):
    """
    Renders a bar chart for theme distribution using Plotly.

    Args:
        df (pd.DataFrame): The DataFrame containing theme data.

    Returns:
        plotly.graph_objs._figure.Figure: The Plotly figure object for the bar chart.
    """
    if df is not None and "theme" in df.columns:
        # Calculate theme counts
        theme_counts = df["theme"].value_counts().reset_index()
        theme_counts.columns = ["Theme", "Count"]

        # Create a bar chart using Plotly
        fig_bar = px.bar(
            theme_counts, 
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

        return fig_bar
    else:
        st.warning("No theme data found to render the bar chart.")
        return None