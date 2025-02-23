import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Tags list (Arabic remains for content matching)
TAGS = [
    "حماس", "إسرائيل", "اسرائيل", "الفلسطينيين", "نتنياهو", "غزة", "أسرى",
    "الاحتلال", "فلسطينية", "الإسرائيلي", "استشهاد", "الجيش الإسرائيلي",
    "المقاومة", "المقاومة الإسلامية", "سرايا القدس", "القسام", "طوفان الأقصى",
    "الفلسطينية", "الإسرائيلية", "أبو عبيدة", "عبيدة", "مقاطعة", "المقاطعة",
    "سوريا", "بشار", "الأسد", "السوريين", "السورية",
    "دونالد", "ترامب", "أميركا", "الرئاسة الأميركية", "انتخابات", "الأميركية",
    "الانتخابات", "الولايات المتحدة", "ولاية ثانية", "الانتخابات الأميركية",
    "الأميركي", "الانتخابية", "الرئاسية", "التصويت", "المرشح", "الولاية", "الرئيس",
    "حرائق", "كاليفورنيا", "الغابات", "نيران", "اندلاع حرائق", "الحرائق",
    "لوس أنجلوس", "لوس", "أنجلوس", "للحرائق", "الخسائر", "للحرق", "الرياح القوية"
]

# Arabic month conversion
ARABIC_MONTHS = {
    'يناير': '01', 'فبراير': '02', 'مارس': '03', 'أبريل': '04',
    'مايو': '05', 'يونيو': '06', 'يوليو': '07', 'أغسطس': '08',
    'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
}


def parse_date(date_str):
    day, month_ar, year = date_str.split()
    month = ARABIC_MONTHS.get(month_ar, '01')
    return datetime.strptime(f'{day}-{month}-{year}', '%d-%m-%Y')


def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = soup.find('div', class_='article__body')
        content = ' '.join([p.text.strip() for p in content_div.find_all('p')]) if content_div else ''

        author_div = soup.find('div', class_='page-header__meta-item')
        author = author_div.text.split(':')[-1].strip() if author_div else None

        return {'content': content, 'author': author}
    except Exception as e:
        print(f"Error fetching article: {e}")
        return {'content': '', 'author': None}


def scrape_alhurra():
    BASE_URL = "https://www.alhurra.com/search"
    page = 0
    collected = 0
    MAX_ARTICLES = 10400

    articles = []

    while collected < MAX_ARTICLES:
        params = {
            "search_api_fulltext": "",
            "type": "2",
            "sort_by": "publication_time",
            "changed": "All",
            "_wrapper_format": "html",
            "page": page
        }

        try:
            response = requests.get(BASE_URL, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            articles_list = soup.find_all('div', class_='teaser teaser--dated')

            if not articles_list:
                break

            for article in articles_list:
                title_element = article.find('h2', class_='teaser__title')
                if not title_element:
                    continue
                title = title_element.text.strip()

                if not any(tag.lower() in title.lower() for tag in TAGS):
                    continue

                link = article.find('a', class_='teaser__title-link')['href']
                full_url = f"https://www.alhurra.com{link}"

                date_element = article.find('div', class_='teaser__date')
                if not date_element:
                    continue

                try:
                    pub_date = parse_date(date_element.text.strip())
                except:
                    continue

                desc_element = article.find('div', class_='teaser__text')
                description = desc_element.text.strip() if desc_element else ''

                img_element = article.find('img', class_='media__element')
                image_url = img_element['src'] if img_element else ''

                article_data = fetch_article_content(full_url)

                articles.append({
                    'source': 'Al Hurra',
                    'author': article_data['author'],
                    'title': title,
                    'content': article_data['content'],
                    'description': description,
                    'url': full_url,
                    'image_url': image_url,
                    'published_at': pub_date.strftime('%Y-%m-%d'),
                    'tags': [tag for tag in TAGS if tag.lower() in title.lower()]
                })

                collected += 1
                print(f"Collected: {collected}/{MAX_ARTICLES}")

                if collected >= MAX_ARTICLES:
                    break

            page += 1

        except Exception as e:
            print(f"Page error: {e}")
            break

    return pd.DataFrame(articles)


# Run and save
df = scrape_alhurra()
df.to_csv('alhurra_10k.csv', index=False)
print("Scraping completed successfully!")