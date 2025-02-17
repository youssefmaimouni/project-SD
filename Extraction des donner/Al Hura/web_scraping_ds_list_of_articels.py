import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape an individual article page
def scrape_article(article_url):
    # Fetch the article page
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the title
    title = soup.find("h1", class_="page-header__title").text.strip()

    # Extract the content
    content = "\n".join([p.text.strip() for p in soup.find("div", class_="article__body").find_all("p")])

    # Extract the date
    date = soup.find("div", class_="page-header__meta-item").text.strip()

    # Extract the author
    author = soup.find("div", class_="page-header__meta-item").find_next_sibling("div").text.strip()

    # Extract the image URL
    image_url = soup.find("img", class_="media__element")["src"]

    # Extract the tags/category
    tags = soup.find("span", class_="page-header__eyebrow").text.strip()

    # Return the extracted data as a dictionary
    return {
        "title": title,
        "content": content,
        "date": date,
        "author": author,
        "image_url": image_url,
        "tags": tags,
        "url": article_url
    }

# Function to scrape the main page and get article links
def scrape_main_page(main_url):
    # Fetch the main page
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract article links
    articles = []
    for article in soup.find_all("div", class_="teaser teaser--small"):
        link = article.find("a")["href"]
        full_link = f"https://www.alhurra.com{link}"  # Construct full URL
        articles.append(full_link)

    return articles

# Main function to run the scraper
def main():
    # URL of the main page
    main_url = "https://www.alhurra.com/latest"

    # Scrape the main page to get article links
    article_links = scrape_main_page(main_url)

    # Scrape each article and store the data
    all_articles = []
    for link in article_links:
        print(f"Scraping article: {link}")
        article_data = scrape_article(link)
        all_articles.append(article_data)

    # Save the data to a CSV file
    df = pd.DataFrame(all_articles)
    df.to_csv("al_hurra_articles.csv", index=False)
    print("Scraping completed! Data saved to al_hurra_articles.csv.")

# Run the scraper
if __name__ == "__main__":
    main()