import pandas as pd
import os
from transformers import pipeline

def analyze_sentiment(input_csv):
    output_csv = input_csv.replace(".csv", "_with_sentiment.csv")
    
    if os.path.exists(output_csv):
        print(f"{output_csv} already exists. Skipping sentiment analysis.")
        return output_csv

    df = pd.read_csv(input_csv)
    
    # Drop rows where 'processed_text' is NaN
    df = df.dropna(subset=["processed_text"])
    
    sentiment_analyzer = pipeline(
        "sentiment-analysis", 
        model="cardiffnlp/twitter-roberta-base-sentiment"
    )
    
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
    
    df.to_csv(output_csv, index=False)
    print(f"Sentiment analysis saved to {output_csv}")
    return output_csv
