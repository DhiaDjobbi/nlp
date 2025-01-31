import requests
from bs4 import BeautifulSoup
import csv
import os
import dateparser

def scrape_trustpilot_reviews(site_to_review):
    base_url = f"https://www.trustpilot.com/review/{site_to_review}?page="
    csv_filename = os.path.join("data", site_to_review.replace('.', '_') + ".csv")  # Save in /data folder    

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def scrape_page(page_number):
        url = f"{base_url}{page_number}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        reviews = []

        review_sections = soup.find_all("section", class_="styles_reviewContentwrapper__W9Vqf")
        for review in review_sections:
            try:
                rating_tag = review.find("div", class_="star-rating_starRating__sdbkn")
                rating = int(rating_tag.img["alt"].split()[1]) if rating_tag and rating_tag.img else None

                title_tag = review.find("h2", class_="typography_heading-s__RxVny")
                title = title_tag.text.strip() if title_tag else None

                text_tag = review.find("p", class_="typography_body-l__v5JLj")
                text = text_tag.text.strip() if text_tag else None

                date_tag = review.find("time")
                date = date_tag.get("datetime") if date_tag else None

                country_tag = review.find_previous("div", class_="typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_detailsIcon__ch_FY")
                country = country_tag.find("span").text.strip() if country_tag else None

                if rating and title and text and date and country:
                    # Remove "Updated " from the text and parse dates
                    if "Updated " in date:
                        date = date.replace("Updated ", "")
                    parsed_date = dateparser.parse(date)
                    if parsed_date:
                        date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        
                    reviews.append({
                        "rating": rating,
                        "title": title,
                        "text": text,
                        "date": date,
                        "country": country
                    })
            except Exception as e:
                # print(f"Error extracting review: {e}")
                pass
        return reviews

    if os.path.exists(csv_filename):
        print(f"{csv_filename} already exists. Skipping scraping.")
        return csv_filename

    response = requests.get(base_url + "1", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    pagination_button = soup.find("a", {"name": "pagination-button-last"})
    last_page_number = int(pagination_button["aria-label"].split()[-1]) if pagination_button else 1

    all_reviews = []
    for page in range(1, last_page_number + 1):
        print(f"Scraping page {page}...")
        all_reviews.extend(scrape_page(page))

    with open(csv_filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rating", "title", "text", "date", "country"])
        writer.writeheader()
        writer.writerows(all_reviews)

    print(f"Scraped reviews and saved to {csv_filename}")
    return csv_filename
