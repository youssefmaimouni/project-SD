import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

# Initialize the WebDriver (use the driver of your choice, e.g., ChromeDriver)
driver = webdriver.Chrome()

# Open the target news website
driver.get('https://www.aljazeera.net/news/')  # Replace with your target URL

# Wait until the page loads (adjust the timeout if necessary)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gc__title")))

# Function to read existing links from a CSV file
def read_existing_links(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            return {row[0] for row in reader}  # Return as a set of links for quick lookup
    return set()

# Read links from both first_half.csv and article_links.csv
first_half_links = read_existing_links('first_half.csv')
existing_links = read_existing_links('article_links.csv')

# Combine both sets to ensure no duplicates
all_existing_links = first_half_links.union(existing_links)

# Open the CSV file for appending links
with open('article_links.csv', 'a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # If the file is empty, write the header
    if file.tell() == 0:
        writer.writerow(["Article Link"])

    try:
        while True:
            # Find all articles by locating the <a> tags inside <h3 class="gc__title">
            titles = driver.find_elements(By.CSS_SELECTOR, 'h3.gc__title a.u-clickable-card__link')

            # Extract and store all href attributes (links)
            for title in titles:
                link = title.get_attribute('href')
                if link not in all_existing_links:  # Only append if not already in the CSV
                    writer.writerow([link])  # Write each new link directly to the CSV file
                    all_existing_links.add(link)  # Add to the set of existing links
                    print(f"Added new link: {link}")

            # Debugging: Print out the number of links found
            print(f"Found {len(titles)} articles.")

            # Check for the "Show More" button with both class and data-testid attribute
            show_more_button = driver.find_elements(By.CSS_SELECTOR, '.show-more-button.big-margin[data-testid="show-more-button"]')
            print(f"Found {len(show_more_button)} 'Show More' button(s).")  # Debugging output

            if show_more_button:
                try:
                    # Ensure the button is clickable
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(show_more_button[0]))

                    # Scroll down the page to load more content
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    print("Scrolled down to the bottom of the page.")

                    # Sleep for a few seconds to allow content to load
                    time.sleep(2)  # Adjust the sleep time if necessary

                    # Check again for the button after scrolling and waiting
                    show_more_button = driver.find_elements(By.CSS_SELECTOR, '.show-more-button.big-margin[data-testid="show-more-button"]')

                    # Scroll to the 'Show More' button before clicking it
                    if show_more_button:
                        actions = ActionChains(driver)
                        actions.move_to_element(show_more_button[0]).perform()  # Scroll to the button
                        print("Scrolled to the 'Show More' button.")

                        # Now, click the button
                        show_more_button[0].click()
                        print("Clicked the 'Show More' button.")
                        
                        # Wait for the page to load more content (this time we wait explicitly for the new content)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3.gc__title a.u-clickable-card__link')))
                        print("Waiting for more content to load...")

                except Exception as e:
                    print(f"Error while clicking 'Show More' button: {e}")
                    break  # Exit the loop if the button is not clickable


    except Exception as e:
        print(f"Error occurred: {e}")

# Close the driver after scraping
driver.quit()

print("Scraping completed!")
