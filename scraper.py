import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

max_depth = 2
max_pages = 50

async def fetch(session, url):
    try:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
            response.raise_for_status()  # Проверка на успешный статус ответа
            return await response.text()
    except Exception as e:
        print(f"Ошибка при запросе {url}: {e}")
        return ""

async def scrape_page(session, current_url, depth, visited, pages_data):
    if depth > max_depth or len(visited) >= max_pages:
        return

    visited.add(current_url)
    html = await fetch(session, current_url)

    if html:
        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)
        page_title = soup.title.string if soup.title else current_url

        pages_data.append({
            'url': current_url,
            'title': page_title,
            'content': page_text
        })

        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(current_url, link['href'])
            if urlparse(absolute_url).netloc == urlparse(current_url).netloc and absolute_url not in visited:
                await scrape_page(session, absolute_url, depth + 1, visited, pages_data)
                await asyncio.sleep(1)  # Задержка между запросами

async def scrape_site(url, max_depth=2, max_pages=50):
    visited = set()
    pages_data = []
    
    async with aiohttp.ClientSession() as session:
        await scrape_page(session, url, 0, visited, pages_data)
    
    return pages_data  # Возврат всех собранных страниц для использования

def main(url):
    loop = asyncio.get_event_loop()
    pages = loop.run_until_complete(scrape_site(url, max_depth, max_pages))
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Пример запуска
    main('https://example.com')  # Замените на нужный URL
