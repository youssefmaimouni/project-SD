import requests
import csv
import time
from datetime import datetime

# List of JSON endpoints (add all your URLs here)
JSON_ENDPOINTS = [
    "https://api.skynewsarabia.com//rest/v2/latest.json?category=section&nextPageToken=1740116001000&pageSize=20&types=ARTICLE,IMAGE_GALLERY,LIVE_STORY",
    "https://api.skynewsarabia.com//rest/v2/latest.json?category=section&nextPageToken=1740094515000&pageSize=20&types=ARTICLE,IMAGE_GALLERY,LIVE_STORY",
    "https://api.skynewsarabia.com//rest/v2/latest.json?category=section&nextPageToken=1740071769000&pageSize=20&types=ARTICLE,IMAGE_GALLERY,LIVE_STORY",
    "https://api.skynewsarabia.com//rest/v2/latest.json?category=section&nextPageToken=1740055125000&pageSize=20&types=ARTICLE,IMAGE_GALLERY,LIVE_STORY"
]


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

        print(f"Processed {len(data.get('contentItems', []))} articles from {url}")
        return True

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False


def main():
    with open("skynews_articles.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["source", "title", "description", "url", "image_url", "published_at", "tags"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, url in enumerate(JSON_ENDPOINTS, 1):
            print(f"Processing URL {idx}/{len(JSON_ENDPOINTS)}")
            success = process_endpoint(url, writer)

            # Add delay after every 5 requests
            if idx % 5 == 0 and success:
                print("Waiting 30 seconds to avoid blocking...")
                time.sleep(30)

            # Small delay between requests
            time.sleep(2)


if __name__ == "__main__":
    main()