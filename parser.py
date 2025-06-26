import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}

url = "https://www.avito.ru/moskva/avtomobili?q=Toyota"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

cars = soup.find_all('div', {'data-marker': 'item'})

for car in cars[:5]:
    try:
        # 1. Название (основные варианты поиска)
        title = None

        # Вариант 1: По data-marker
        title_elem = car.find(attrs={"data-marker": "item-title"})
        if title_elem:
            title = title_elem.text.strip()

        # Вариант 2: По itemprop
        if not title:
            title_elem = car.find(itemprop="name")
            if title_elem:
                title = title_elem.text.strip()

        # Вариант 3: По классу заголовка
        if not title:
            title_elem = car.find('h3', class_=lambda x: x and 'title' in x.lower())
            if title_elem:
                title = title_elem.text.strip()

        # Вариант 4: Крайний случай - ищем любой h3
        if not title:
            title_elem = car.find('h3')
            if title_elem:
                title = title_elem.text.strip()

        title = title or "Название не найдено"

        # 2. Цена
        price = car.find('meta', itemprop='price')
        price = price['content'] if price else \
            car.find(attrs={"data-marker": "item-price"}).text.strip() if car.find(
                attrs={"data-marker": "item-price"}) else \
                "Цена не указана"

        # 3. Параметры
        params = car.find(attrs={"data-marker": "item-specific-params"})
        params = params.text.strip() if params else \
            car.find('div', class_=lambda x: x and 'params' in x.lower()).text.strip() if car.find('div', class_=lambda
                x: x and 'params' in x.lower()) else \
                "Параметры не указаны"

        # 4. Ссылка
        link = car.find('a', itemprop='url')
        link = "https://www.avito.ru" + link['href'] if link else \
            "https://www.avito.ru" + car.find('a', href=True)['href'] if car.find('a', href=True) else \
                "Ссылка не найдена"

        print(f" {title}\n Цена: {price} ₽\n {params}\n {link}\n{'=' * 50}\n")

    except Exception as e:
        print(f"Ошибка при обработке объявления: {str(e)}")
        continue