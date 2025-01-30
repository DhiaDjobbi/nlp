# mypipeline/pipeline.py
from .scrapper import scrape_trustpilot_reviews
from .preprocessing import preprocess_reviews
from .sentiment_analysis import analyze_sentiment
from .theme_detection import detect_themes

def run_full_pipeline(site_to_review):
    print("Starting scraping...")
    raw_csv = scrape_trustpilot_reviews(site_to_review)
    
    print("\nStarting preprocessing...")
    processed_csv = preprocess_reviews(raw_csv)
    
    print("\nAnalyzing sentiment...")
    sentiment_csv = analyze_sentiment(processed_csv)
    
    print("\nDetecting themes...")
    final_csv = detect_themes(sentiment_csv)
    
    print("\nPipeline complete!")
    return final_csv