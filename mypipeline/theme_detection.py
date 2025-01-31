import pandas as pd
import os
import re

# Define the static themes and their keywords
THEME_KEYWORDS = {
    "Delivery Issues": [
        "not picked", "missed", "failed", "lost", "late", "delayed", "undelivered", "error", 
        "rescheduled", "problem", "loss", "stolen", "never arrived", "never received", 
        "no pick up", "re-schedule", "never showed", "missed pickup", "missed delivery",
        "failed delivery", "lost parcel", "late delivery", "delayed delivery", "undelivered parcel",
        "parcel pickup", "pickup delay", "pickup failed", "not picked up",
        "address wrong", "wrong address", "wrong location", "wrong recipient", "wrong recipient",
        "disappeared", "disappearance", "vanished", "vanishing", "gone", "missing", "missing parcel", "disspear"
    ],
    "Poor Customer Service": [
        "poor", "no response", "unhelpful", "rude", "bad", "terrible", "support", "ignored", 
        "unresponsive", "frustrating", "lack", "disappointing", "no manager","won't respond"
        "manager never called", "follow up", "continuous problems", "zero contact",
        "no customer service", "no customer support", "no customer care", "no customer help","no help"
        "unhelpful response", "refuse to tell", "vague response", "poor service","useless","customer service is worse","no sign"
    ],
    "Unreliable Service": [
        "unreliable", "failed", "chaotic", "inconsistent", "unpredictable", "untrustworthy", 
        "unstable", "erratic", "spotty", "hit", "miss", "undependable", "unreliability",
        "unreliable service", "unreliable company", "unreliable delivery", "unreliable courier",
        "ripoff", "failed to deliver", "not shipped", "never arrived", "delayed delivery"
    ],
    "Lack of Communication": [
        "no updates", "no response", "no info", "lack", "silent", "uncommunicative", "no feedback", 
        "no follow", "no status", "no clarity", "no notification", "no confirmation", "no tracking",
        "no communication", "no contact", "no call", "no email", "no message", "no text", "no reply",
        "unresponsive", "ignored", "unhelpful", "unreliable", "unprofessional", "untrustworthy",
        "poor communication", "poor response", "poor feedback", "poor follow", "poor status","no indication"
    ],
    "Driver Problems": [
        "driver", "rude", "late", "no show", "unprofessional", "lost", "careless", "aggressive", 
        "negligent", "confused", "error", "incompetent", "reckless", "unreliable", 
        "never shows", "no show driver", "did not show up", "failed pick up",
        "driver never arrived", "driver never showed", "driver never came", "driver never picked up",
        "swearing", "swore", "sworn", "swear", "cursing", "cursed", "curse", "cussing", "cussed",
        "crash", "crashed", "crashing", "accident", "accidental", "accidentally", "collision","No one came","never attempted"
    ],
    "Parcel Handling Problems": [
        "lost", "destroyed", "returned", "damaged", "missing", "broken", "opened", "stolen","right place"
        "misplaced", "mishandled", "crushed", "wet", "torn", "tampered", "ruined", "spoiled",
        "mangled", "smashed", "dented", "cracked", "scratched", "shattered", "crumpled", "soaked",
        "smash", "crush", "crumple", "soak", "soaked", "smashed", "crushed", "crumpled", "soaked",
        "thrown", "throw", "toss", "tossed", "throwing", "tossing", "throw away", "toss away","bent"
        "throwing away", "tossing away", "throw out", "toss out", "throwing out", "tossing out","curbside"
    ],
    "Cost and Value Concerns": [
        "affordable", "expensive", "overpriced", "costly", "pricey", "cheap", "unreasonable", 
        "value", "fees", "hidden", "charges", "expensive", "money", "waste", "budget", "pricing","price was right"
        "reasonable", "inexpensive", "cost-effective", "cost-efficient", "cost-saving", "charge","half the price","Over priced"
    ],
    "Convenience and Ease": [
        "easy", "convenient", "simple", "smooth", "quick", "efficient", "accessible", 
        "flexible", "intuitive", "hassle", "user-friendly", "straightforward", "seamless","Ease"
        "friendly interface"
    ],
    "Timeliness and Speed": [
        "delayed", "late", "slow", "fast", "timely", "prompt", "speedy", "on time","promptly"
        "expedited", "rush", "quick", "efficient", "time-sensitive", "punctual", "swift","days after delivery date"
        "timeframe", "time", "time-consuming", "time-wasting", "time-management", "time-saving",
        "time-efficient", "time-critical", "time-sensitive", "time-consuming", "time-wasting","early"
        "wait", "waiting", "waiting time", "waiting period", "waiting list", "waiting room","early","fastest"
        "waiting area", "waiting line", "waiting game", "waiting period", "waiting time","after","takes days","days","how quickly","earlier","fastest"
    ],
    "Service Variability": [
        "varies", "inconsistent", "unpredictable", "spotty", "mixed", "hit", "miss", 
        "dependent", "disparity", "uneven", "fluctuating", "varying", "inconclusive", "inconclusive"
    ],
    "Frustration and Stress": [
        "frustrating", "stressful", "annoying", "irritating", "infuriating", "maddening", 
        "exasperating", "disappointing", "upsetting", "aggravating",
        "stress", "frustration", "disappointment","worst", "bad", "terrible", "horrible", "awful",
        "hate", "dislike", "displeased", "unhappy", "regret", "regretful",
        "angry", "anger", "mad", "madness", "irritated", "irritation", "annoyed", "annoyance",
        "shocking","Dont use","ridiculous","No word","never shop","t use","joke","fooled"
    ],
    "Shipping Issues": [
        "picked up", "dropped off", "pickup", "drop off", "pickup failed", "parcel", "not picked", 
        "pick-up error", "late pickup", "missing pickup", "not picked up", "drop off issue", 
        "high volume", "pick-up delay", "never picked up","outsourced my packages","haven't received","delivered never","never got scanned"
    ],
    "Positive Experiences": [
        "amazing", "great", "fantastic", "wonderful", "satisfying", "pleasant","pleasantly surprised","came in"
        "impressive", "awesome", "top-notch", "smooth", "outstanding", "worth", "happy", "pleased","Fasting"
        "excellent", "love", "recommend", "recommendation", "recommendable","quickly","up to date"
        "joy", "joyful", "satisfied", "satisfaction", "happy", "happiness", "pleased", "pleasure","very comfortable"
        "impressed", "impressive", "awesome", "awesomeness", "top-notch", "outstanding", "worth","that's all I need","Nice job"
        "excellent", "is good", "love", "recommend", "recommendation", "recommendable","quickly","helped","perfect","as ordered","Thank you","good price"
        "worked hard", "help resolve issues", "is helpful", "helpful staff", "helpful team","Good","wont use any other","fair price","sweet","perfect","Easier to use","was then able"
    ],
    "Positive Feedback": [
        "amazing", "great", "fantastic", "wonderful", "satisfying", "pleased", "impressive","perfect condition","thank you","BRAVO","perfect"
        "awesome", "top-notch", "outstanding", "happy", "worth", "excellent", "is good", "best", "love","incredible","Reliable","friendly ","well","Darling","Accurate","important"
        "helpful","Accurate","HAPPIER","perfectly","better","amazed","beautiful","safely","rock","quite well","super","Perfect","preferred"
    ],
    "Negative Experiences": [
        "frustrating", "infuriating", "upsetting", "terrible", "awful", "horrible", "worst", "dislike", 
        "hate", "displeased", "unhappy", "disappointment", "stress", "maddening", "irritating", 
        "annoying", "exasperating","scam","not recommended","AVOID","upset","lying"
    ]
}


def detect_themes(input_csv):
    output_csv = input_csv.replace(".csv", "_with_themes.csv")
    bar_chart_data_path = os.path.join("streamlit_folder", "bar_chart_data.csv")
    
    # Create the streamlit_folder if it doesn't exist
    os.makedirs("streamlit_folder", exist_ok=True)
    
    if os.path.exists(output_csv):
        print(f"{output_csv} already exists. Skipping theme detection.")
        return output_csv

    df = pd.read_csv(input_csv)
    df["combined_text"] = df["text"].fillna("") + " " + df.get("title", "").fillna("")
    
    detected_themes = []
    for text in df["combined_text"]:
        theme = "No Theme Detected"
        for category, keywords in THEME_KEYWORDS.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text, flags=re.I) for kw in keywords):
                theme = category
                break
        detected_themes.append(theme)
    
    df["theme"] = detected_themes
    
    # Remove rows with "No Theme Detected"
    df = df[df["theme"] != "No Theme Detected"]
    
    # Save the theme detection results
    df.to_csv(output_csv, index=False)
    print(f"Theme detection saved to {output_csv}")
    
    # Prepare data for the bar chart
    theme_counts = df["theme"].value_counts().reset_index()
    theme_counts.columns = ["Theme", "Count"]
    
    # Save the bar chart data to a CSV file
    theme_counts.to_csv(bar_chart_data_path, index=False)
    print(f"Bar chart data saved to {bar_chart_data_path}")
    
    return output_csv
