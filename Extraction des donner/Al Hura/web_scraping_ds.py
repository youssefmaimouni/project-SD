import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the main page and get article details
def scrape_main_page(main_url):
    # Fetch the main page
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract article details
    articles = []
    for article in soup.find_all("div", class_="teaser teaser--small"):
        # Extract the title
        title = article.find("h3", class_="teaser__title").text.strip()

        # Extract the link
        link = article.find("a")["href"]
        full_link = f"https://www.alhurra.com{link}"  # Construct full URL

        # Extract the image URL
        image_url = article.find("img")["src"]

        # Extract the category/tags
        tags = article.find("div", class_="story-card__label").text.strip()

        # Append the article data to the list
        articles.append({
            "title": title,
            "link": full_link,
            "image_url": image_url,
            "tags": tags
        })

    return articles

# Main function to run the scraper
def main():
    # URL of the main page
    main_url = "https://www.alhurra.com/latest"

    # Scrape the main page to get article details
    articles = scrape_main_page(main_url)

    # Save the data to a CSV file
    df = pd.DataFrame(articles)
    df.to_csv("al_hurra_articles_list.csv", index=False)
    print("Scraping completed! Data saved to al_hurra_articles_list.csv.")

# Run the scraper
if __name__ == "__main__":
    main()