```markdown
# 📰 France24 Arabic News Scraper

## 📌 Project Description
This project is designed to scrape news articles from the **France24 Arabic** website. It utilizes **Selenium** and **BeautifulSoup** to automate web scraping, extract data, and store it in structured formats like CSV.

## 🛠️ Technologies & Libraries Used
- `selenium` - For web automation and page interaction
- `webdriver-manager` - To automatically manage ChromeDriver
- `BeautifulSoup` - For HTML parsing and data extraction
- `requests` - To handle HTTP requests
- `csv` - For saving extracted data
- `pandas` - For data processing and merging
- `os` - For file management
- `time` - To control execution delays


## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/youssefmaimouni/project-SD/tree/main/Extraction%20des%20donner/France24
cd France24
```

### 2️⃣ Install Dependencies
```bash
pip install selenium webdriver-manager beautifulsoup4 pandas requests
```

### 3️⃣ Setup ChromeDriver (Automatically managed by `webdriver-manager`)

## 📝 Usage

### 📌 Scrape a Single Page
Run the `scraping_one_page.ipynb` notebook to extract news articles from a single page.

### 📌 Automate Multi-Page Scraping
Run `scrapping_automation.ipynb` to scrape multiple pages from the website.

### 📌 Merge and Clean Data
Run `data_fusionne.ipynb` to process and merge scraped datasets into a structured format.

## 🔥 Example Code Snippet
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--headless")  # Run in the background
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection

driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="133.0.6943.99").install()), options=options)
driver.get("https://www.france24.com/ar/%D8%A3%D8%B1%D8%B4%D9%8A%D9%81/2024/")

html = driver.page_source
time.sleep
driver.quit()
# Parse the page source with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
soup
```

## 🔮 Future Improvements
✅ Extract additional details like publication date and article category  
✅ Store scraped data in a database instead of CSV files  

---

📩 **For Issues & Contributions**  
Feel free to open an issue or contribute to this project! 🚀  
Happy Scraping! 🎯  
```
