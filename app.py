from flask import Flask, request, render_template
from scraper import scrape_site
import os

app = Flask(__name__)

# Путь к папке для кэширования
CACHE_DIR = 'cache'

# Проверяем, существует ли папка для кэша, если нет — создаём
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        query = request.form['query']
        max_depth = int(request.form.get('max_depth', 2))  # Ограничение глубины
        max_pages = int(request.form.get('max_pages', 50))  # Ограничение количества страниц

        # Проверяем кэш
        cache_file = os.path.join(CACHE_DIR, f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.txt")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                site_text = f.read()
        else:
            # Если кэша нет, сканируем сайт
            site_text = scrape_site(url, max_depth, max_pages)
            if site_text:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(site_text)

        # Поиск фразы на сайте
        if query.lower() in site_text.lower():
            return f"Фраза '{query}' найдена на сайте {url}."
        else:
            return f"Фраза '{query}' не найдена на сайте {url}."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
