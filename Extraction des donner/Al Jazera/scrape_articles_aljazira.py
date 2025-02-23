import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Initialize the WebDriver
driver = webdriver.Chrome()

# Function to scrape title and content from a given URL
def scrape_article(url):
    driver.get(url)
    time.sleep(2)  # Allow page to load fully

    # Check for and click the 'Read More' button if it exists
    try:
        read_more_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "article-content-read-more"))
        )
        read_more_button.click()
        print("Clicked 'Read More' button.")
        time.sleep(1)  # Allow time for content to expand
    except:
        print("No 'Read More' button found.")

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract title from <h1>
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

    # Extract content from <div class="wysiwyg wysiwyg--all-content">
    content_div = soup.find('div', class_='wysiwyg wysiwyg--all-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join(p.get_text(strip=True) for p in paragraphs)
    else:
        content = "No Content Found"

    return title, content

# Read URLs from 'second_half.csv', starting from line 0
urls = []
with open('article_links.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        if row:  # Ensure the row is not empty
            urls.append(row[0])

print(f"Total URLs to scrape: {len(urls)}")

# Prepare CSV file to store scraped data (append mode)
with open('new_articles.csv', 'a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
    if file.tell() == 0:
        writer.writerow(['Title', 'Content'])  # Write header if file is empty

    for idx, url in enumerate(urls):
        try:
            print(f"Scraping ({idx+1}/{len(urls)}): {url}")
            title, content = scrape_article(url)

            # Write the scraped data to CSV immediately
            writer.writerow([title, content])
            print(f"Successfully scraped: {title}\n")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

# Close the WebDriver
driver.quit()
print("Scraping completed. Data saved to 'new_articles.csv'.")
