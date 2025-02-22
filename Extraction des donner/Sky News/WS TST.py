import requests
import csv
import time
import os
from datetime import datetime

JSON_ENDPOINTS = [
    "https://api.skynewsarabia.com//rest/v2/search/text.json?deviceType=MOBILE&from=&offset=108&pageSize=12&q=%D8%AD%D9%85%D8%A7%D8%B3&showEpisodes=true&sort=RELEVANCE&supportsInfographic=true&to="
]

FILENAME = "skynews_articles.csv"


def extract_article_data(article):
    """Extract data from a single article entry"""
    return {
        "source": "Sky News Arabic",
        "title": article.get("headline", ""),
        "description": article.get("summary", ""),
        "url": article.get("shareUrl", ""),
        "image_url": (article.get("mediaAsset", {}).get("imageUrl", "")
                      .replace("{width}", "800").replace("{height}", "450")),
        "published_at": article.get("date", ""),
        "tags": [article.get("topicTitle", "")] if article.get("topicTitle") else []
    }


def process_endpoint(url, writer):
    """Process a single JSON endpoint"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("contentItems", []):
            article_data = extract_article_data(item)
            writer.writerow(article_data)

        print(f"Added {len(data.get('contentItems', []))} articles from {url}")
        return True

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False


def main():
    # Check if file exists to determine write mode
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["source", "title", "description", "url", "image_url",
                      "published_at", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if file is empty/new
        if not file_exists or csvfile.tell() == 0:
            writer.writeheader()

        for idx, url in enumerate(JSON_ENDPOINTS, 1):
            print(f"Processing URL {idx}/{len(JSON_ENDPOINTS)}")
            success = process_endpoint(url, writer)

            # Add safety delays
            if idx % 5 == 0 and success:
                print("Waiting 30 seconds to avoid blocking...")
                time.sleep(30)

            time.sleep(2)


if __name__ == "__main__":
    main()