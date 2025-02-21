import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

ARABIC_MONTHS = {
    'يناير': '01', 'فبراير': '02', 'مارس': '03', 'أبريل': '04',
    'مايو': '05', 'يونيو': '06', 'يوليو': '07', 'أغسطس': '08',
    'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
}

STOP_DATE = datetime(2023, 10, 7)
MAX_ARTICLES = 50000


async def parse_date(date_str):
    try:
        day, month_ar, year = date_str.split()
        month = ARABIC_MONTHS.get(month_ar, '01')
        return datetime.strptime(f'{day}-{month}-{year}', '%d-%m-%Y')
    except:
        return None


async def fetch_article(session, url):
    try:
        async with session.get(url, timeout=30) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            content_div = soup.find('div', class_='article__body')
            content = ' '.join([p.text.strip() for p in content_div.find_all('p')]) if content_div else ''

            author_div = soup.find('div', class_='page-header__meta-item')
            author = author_div.text.split(':')[-1].strip() if author_div else None

            return {'content': content, 'author': author}
    except Exception as e:
        print(f"Article fetch error: {e}")
        return {'content': '', 'author': None}


async def process_page(session, page_num, sem):
    async with sem:
        try:
            params = {
                "search_api_fulltext": "",
                "type": "2",
                "sort_by": "publication_time",
                "changed": "All",
                "_wrapper_format": "html",
                "page": page_num
            }

            async with session.get("https://www.alhurra.com/search", params=params) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                return soup.find_all('div', class_='teaser teaser--dated')
        except Exception as e:
            print(f"Page error: {e}")
            return []


async def process_article(session, article):
    try:
        title = article.find('h2', class_='teaser__title').text.strip()
        link = f"https://www.alhurra.com{article.find('a', class_='teaser__title-link')['href']}"

        date_str = article.find('div', class_='teaser__date').text.strip()
        pub_date = await parse_date(date_str)

        if not pub_date or pub_date < STOP_DATE:
            return None

        desc_element = article.find('div', class_='teaser__text')
        description = desc_element.text.strip() if desc_element else ''

        img_element = article.find('img', class_='media__element')
        image_url = img_element['src'] if img_element else ''

        article_data = await fetch_article(session, link)

        return {
            'source': 'Al Hurra',
            'author': article_data['author'],
            'title': title,
            'content': article_data['content'],
            'description': description,
            'url': link,
            'image_url': image_url,
            'published_at': pub_date.strftime('%Y-%m-%d'),
            'tags': []
        }
    except Exception as e:
        print(f"Article processing error: {e}")
        return None


async def main():
    connector = aiohttp.TCPConnector(limit=200)
    sem = asyncio.Semaphore(100)  # High concurrency
    articles = []
    page_num = 0
    stop_flag = False

    async with aiohttp.ClientSession(connector=connector) as session:
        while len(articles) < MAX_ARTICLES and not stop_flag:
            print(f"Processing page {page_num}...")
            page_articles = await process_page(session, page_num, sem)

            if not page_articles:
                print("No more articles found")
                break

            tasks = [process_article(session, article) for article in page_articles]
            results = await asyncio.gather(*tasks)

            for result in results:
                if result:
                    articles.append(result)
                    current_date = datetime.strptime(result['published_at'], '%Y-%m-%d')

                    print(f"Collected: {len(articles)} | Date: {result['published_at']}")

                    if current_date <= STOP_DATE:
                        print("Reached stop date!")
                        stop_flag = True
                        break

                if len(articles) >= MAX_ARTICLES:
                    break

            if stop_flag:
                break

            page_num += 1

    df = pd.DataFrame(articles)
    df.to_csv('alhurra_full_collection_2.csv', index=False)
    print(f"Finished with {len(articles)} articles")


if __name__ == '__main__':
    asyncio.run(main())