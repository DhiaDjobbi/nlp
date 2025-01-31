import pandas as pd
import os
from transformers import pipeline

def analyze_sentiment(input_csv):
    output_csv = input_csv.replace(".csv", "_with_sentiment.csv")
    pie_chart_data_path = os.path.join("streamlit_folder", "pie_chart_data.csv")
    
    # Create the streamlit_folder if it doesn't exist
    os.makedirs("streamlit_folder", exist_ok=True)
    
    if os.path.exists(output_csv):
        print(f"{output_csv} already exists. Skipping sentiment analysis.")
        return output_csv

    df = pd.read_csv(input_csv)
    
    # Drop rows where 'processed_text' is NaN
    df = df.dropna(subset=["processed_text"])
    
    # Initialize the sentiment analyzer
    sentiment_analyzer = pipeline(
        "sentiment-analysis", 
        model="cardiffnlp/twitter-roberta-base-sentiment"
    )
    
    # Map model labels to human-readable labels
    label_map = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}
    
    def get_sentiment(text):
        try:
            result = sentiment_analyzer(text[:512])[0]  # Truncate to 512 tokens
            return label_map.get(result["label"], "UNKNOWN")
        except Exception as e:
            # Suppress the error message
            return None  # Return None for failed analyses
    
    print("Analyzing sentiment...")
    df["sentiment"] = df["processed_text"].apply(get_sentiment)
    
    # Drop rows where sentiment analysis failed (None values)
    df = df.dropna(subset=["sentiment"])
    
    # Save the sentiment analysis results
    df.to_csv(output_csv, index=False)
    print(f"Sentiment analysis saved to {output_csv}")
    
    return output_csv
