import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.alhurra.com/latest"


def scrape_article_links():
    response = requests.get(BASE_URL)
    response.raise_for_status()  # Raise an error if request fails
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    # Find all articles in the list
    for item in soup.find_all("div", class_="col-1 vertical-list__item"):
        try:
            # Extract the article link
            link_tag = item.find("a", href=True)
            article_url = "https://www.alhurra.com" + link_tag["href"] if link_tag else ""

            # Extract the title
            title_tag = item.find("h3", class_="teaser__title")
            title = title_tag.text.strip() if title_tag else ""

            # Extract the image URL
            img_tag = item.find("img", class_="media__element")
            image_url = img_tag["src"] if img_tag else ""

            # Extract category (optional)
            category_tag = item.find("div", class_="story-card__label")
            category = category_tag.text.strip() if category_tag else ""

            if article_url:  # Only add valid articles
                articles.append({
                    "title": title,
                    "url": article_url,
                    "image_url": image_url,
                    "category": category
                })
        except Exception as e:
            print("Error extracting an article:", e)

    return articles


# Run and print results
article_data = scrape_article_links()
for article in article_data[:5]:  # Print first 5 articles
    print(article)


def scrape_article(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if request fails
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_tag = soup.find("h1", class_="page-header__title")
    title = title_tag.text.strip() if title_tag else "Unknown Title"

    # Extract author
    author_tag = soup.find("div", class_="page-header__meta-item")
    author = author_tag.text.strip() if author_tag else "Unknown Author"

    # Extract date (published_at)
    date_tag = soup.find_all("div", class_="page-header__meta-item")
    published_at = date_tag[1].text.strip() if len(date_tag) > 1 else "Unknown Date"

    # Extract category
    category_tag = soup.find("span", class_="page-header__eyebrow")
    category = category_tag.text.strip() if category_tag else "Unknown Category"

    # Extract main image URL
    img_tag = soup.find("div", class_="article__featured-media").find("img") if soup.find("div", class_="article__featured-media") else None
    image_url = img_tag["src"] if img_tag else "No Image"

    # Extract full article content
    content_tag = soup.find("div", class_="article__body")
    content = "\n".join([p.text.strip() for p in content_tag.find_all("p")]) if content_tag else "No Content"

    # Return data as dictionary
    return {
        "source": "Al Hurra",
        "author": author,
        "title": title,
        "content": content,
        "description": content[:150] + "...",  # First 150 characters as summary
        "url": url,
        "image_url": image_url,
        "published_at": published_at,
        "tags": category
    }

# Example Usage
article_url = "https://www.alhurra.com/israel-hamas-war/2025/02/16/..."
article_data = scrape_article(article_url)
print(article_data)
