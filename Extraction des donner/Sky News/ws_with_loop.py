import requests
import csv
import time
import os

# Configure these variables
URL_TEMPLATE = "https://api.skynewsarabia.com//rest/v2/search/text.json?deviceType=MOBILE&from=&offset={offset}&pageSize=12&q=%D8%AD%D9%85%D8%A7%D8%B3&showEpisodes=true&sort=RELEVANCE&supportsInfographic=true&to="
START_OFFSET = 120
MAX_OFFSET = 4000
FILENAME = "skynews_articles_3.csv"


def generate_urls():
    """Generate URLs by replacing {offset} placeholder"""
    offset = START_OFFSET
    while offset <= MAX_OFFSET:
        yield URL_TEMPLATE.format(offset=offset)
        offset += 12  # pageSize value


def extract_article_data(article):
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


def main():
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "source", "title", "description", "url",
            "image_url", "published_at", "tags"
        ])

        if not file_exists:
            writer.writeheader()

        for idx, url in enumerate(generate_urls(), 1):
            print(f"Processing offset {START_OFFSET + (idx - 1) * 12}")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get("contentItems"):
                    print("No more articles. Stopping.")
                    break

                for item in data["contentItems"]:
                    writer.writerow(extract_article_data(item))

                print(f"Added {len(data['contentItems'])} articles")

                # Rate limiting (10 requests)
                time.sleep(2)

            except Exception as e:
                print(f"Error: {str(e)}")
                continue


if __name__ == "__main__":
    main()