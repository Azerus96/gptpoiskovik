import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Функция для скрапинга сайта с рекурсивным обходом ссылок
def scrape_site(url, max_depth=2, max_pages=50):
    visited = set()  # Множество для хранения посещённых страниц
    pages_text = []  # Список для хранения текста со всех страниц

    def scrape_page(current_url, depth):
        if depth > max_depth or len(visited) >= max_pages:
            return

        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                visited.add(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Извлекаем текст со страницы
                page_text = soup.get_text(separator=' ', strip=True)
                pages_text.append(page_text)

                # Находим все ссылки на странице
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(current_url, link['href'])
                    # Проверяем, что ссылка ведёт на тот же домен
                    if urlparse(absolute_url).netloc == urlparse(url).netloc and absolute_url not in visited:
                        scrape_page(absolute_url, depth + 1)

                # Задержка между запросами, чтобы не перегружать сайт
                time.sleep(1)
        except Exception as e:
            print(f"Ошибка при скрапинге {current_url}: {e}")

    # Начинаем скрапинг с главной страницы
    scrape_page(url, 0)

    # Возвращаем весь текст, собранный со всех страниц
    return ' '.join(pages_text)
