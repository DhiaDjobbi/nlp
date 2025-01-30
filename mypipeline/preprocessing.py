import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import os

nltk.download(['punkt', 'stopwords', 'punkt_tab', 'wordnet'], quiet=True)

def preprocess_text(text):
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    
    words = word_tokenize(str(text).lower())
    processed_words = [
        lemmatizer.lemmatize(word) for word in words
        if word.isalnum() and word not in stop_words
    ]
    return " ".join(processed_words)

def preprocess_reviews(input_csv):
    output_csv = input_csv.replace(".csv", "_processed.csv")
    
    # Check if the output file already exists
    if os.path.exists(output_csv):
        print(f"Processed file {output_csv} already exists. Skipping processing.")
        return output_csv
    
    df = pd.read_csv(input_csv)
    
    if "text" not in df.columns:
        raise ValueError("CSV must contain 'text' column")
    
    print("Preprocessing reviews...")
    df["processed_text"] = df["text"].apply(preprocess_text)
    
    df.to_csv(output_csv, index=False)
    print(f"Preprocessed data saved to {output_csv}")
    return output_csv