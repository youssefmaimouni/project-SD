import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

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

ARABIC_MONTHS = {
    'يناير': '01', 'فبراير': '02', 'مارس': '03', 'أبريل': '04',
    'مايو': '05', 'يونيو': '06', 'يوليو': '07', 'أغسطس': '08',
    'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
}


async def parse_date(date_str):
    try:
        day, month_ar, year = date_str.split()
        month = ARABIC_MONTHS.get(month_ar, '01')
        return datetime.strptime(f'{day}-{month}-{year}', '%d-%m-%Y')
    except:
        return None


async def fetch_article(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            content_div = soup.find('div', class_='article__body')
            content = ' '.join([p.text.strip() for p in content_div.find_all('p')]) if content_div else ''

            author_div = soup.find('div', class_='page-header__meta-item')
            author = author_div.text.split(':')[-1].strip() if author_div else None

            return {'content': content, 'author': author}
    except Exception as e:
        print(f"Error fetching article: {e}")
        return {'content': '', 'author': None}


async def process_page(session, page_num, sem):
    async with sem:
        params = {
            "search_api_fulltext": "",
            "type": "2",
            "sort_by": "publication_time",
            "changed": "All",
            "_wrapper_format": "html",
            "page": page_num
        }

        try:
            async with session.get("https://www.alhurra.com/search", params=params) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                articles = soup.find_all('div', class_='teaser teaser--dated')
                return articles
        except:
            return []


async def process_article(session, article):
    title_element = article.find('h2', class_='teaser__title')
    if not title_element:
        return None

    title = title_element.text.strip()
    if not any(tag.lower() in title.lower() for tag in TAGS):
        return None

    link = article.find('a', class_='teaser__title-link')['href']
    full_url = f"https://www.alhurra.com{link}"

    date_element = article.find('div', class_='teaser__date')
    if not date_element:
        return None

    pub_date = await parse_date(date_element.text.strip())
    if not pub_date:
        return None

    desc_element = article.find('div', class_='teaser__text')
    description = desc_element.text.strip() if desc_element else ''

    img_element = article.find('img', class_='media__element')
    image_url = img_element['src'] if img_element else ''

    article_data = await fetch_article(session, full_url)

    return {
        'source': 'Al Hurra',
        'author': article_data['author'],
        'title': title,
        'content': article_data['content'],
        'description': description,
        'url': full_url,
        'image_url': image_url,
        'published_at': pub_date.strftime('%Y-%m-%d'),
        'tags': [tag for tag in TAGS if tag.lower() in title.lower()]
    }


async def main():
    connector = aiohttp.TCPConnector(limit=50)
    sem = asyncio.Semaphore(20)  # Concurrent page requests
    articles = []
    page_num = 0
    MAX_ARTICLES = 10400

    async with aiohttp.ClientSession(connector=connector) as session:
        while len(articles) < MAX_ARTICLES:
            page_articles = await process_page(session, page_num, sem)
            if not page_articles:
                break

            tasks = [process_article(session, article) for article in page_articles]
            results = await asyncio.gather(*tasks)

            for result in results:
                if result and len(articles) < MAX_ARTICLES:
                    articles.append(result)
                    print(f"Collected: {len(articles)}/{MAX_ARTICLES}")

            page_num += 1

    df = pd.DataFrame(articles)
    df.to_csv('alhurra_async.csv', index=False)
    print("Scraping completed successfully!")


if __name__ == '__main__':
    asyncio.run(main())