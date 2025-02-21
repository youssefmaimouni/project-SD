import requests
import csv
import time
import os
from datetime import datetime

JSON_ENDPOINTS = [
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


            time.sleep(2)


if __name__ == "__main__":
    main()