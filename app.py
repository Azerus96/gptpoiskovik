from flask import Flask, request, render_template
import os
import json
import asyncio
import aiohttp

app = Flask(__name__)

# Путь к папке для кэширования
CACHE_DIR = 'cache'

# Проверяем, существует ли папка для кэша, если нет — создаём
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Функция для загрузки данных из файла
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def scrape_site(url):
    visited = set()
    pages_data = []

    async def fetch(session, url):
        try:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
                response.raise_for_status()  # Проверка на успешный статус ответа
                return await response.text()
        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")
            return ""

    async def scrape_page(session, current_url, depth):
        if depth > 2 or len(visited) >= 50:
            return

        visited.add(current_url)
        html = await fetch(session, current_url)

        if html:
            soup = BeautifulSoup(html, 'html.parser')
            page_title = soup.title.string if soup.title else current_url
            page_text = soup.get_text(separator=' ', strip=True)
            
            pages_data.append({
                'url': current_url,
                'title': page_title,
                'content': page_text
            })

            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(current_url, link['href'])
                if urlparse(absolute_url).netloc == urlparse(url).netloc and absolute_url not in visited:
                    await scrape_page(session, absolute_url, depth + 1)
                    await asyncio.sleep(1)  # Задержка между запросами

    async with aiohttp.ClientSession() as session:
        await scrape_page(session, url, 0)

    return pages_data

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        url = request.form['url']
        query = request.form['query']

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pages_data = loop.run_until_complete(scrape_site(url))

        # Поиск фразы в загруженных данных
        for page in pages_data:
            title = page['title']
            content = page['content']
            page_url = page['url']
            count = content.lower().count(query.lower())  # Подсчитываем количество вхождений искомого слова

            if count > 0:
                results.append({
                    'title': title,
                    'url': page_url,
                    'context': extract_context(content, query),
                    'count': count
                })

        # Сортировка результатов по частоте вхождения
        results.sort(key=lambda x: x['count'], reverse=True)

    return render_template('index.html', results=results)

def extract_context(text, query):
    start = text.lower().find(query.lower())
    if start == -1:
        return text
    start_index = max(start - 30, 0)
    end_index = min(start + len(query) + 30, len(text))
    return text[start_index:end_index].replace(query, f"<span style='color:red;'>{query}</span>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
