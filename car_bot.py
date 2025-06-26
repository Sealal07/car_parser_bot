
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}


def get_cars(brand=""):
    url = f"https://www.avito.ru/moskva/avtomobili{'?q=' + brand if brand else ''}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        cars_elements = soup.find_all('div', {'data-marker': 'item'})
        cars = []

        for car in cars_elements[:10]:  # Берем первые 10 объявлений
            try:
                car_data = parse_car(car)
                if car_data:
                    cars.append(car_data)
            except Exception as e:
                print(f"Ошибка при обработке объявления: {str(e)}")
                continue

        return cars

    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
        return []


def parse_car(car):
    car_data = {}

    # 1. Название
    title_elem = (car.find(attrs={"data-marker": "item-title"}) or
                  car.find(itemprop="name") or
                  car.find('h3', class_=lambda x: x and 'title' in x.lower()) or
                  car.find('h3'))
    car_data['title'] = title_elem.text.strip() if title_elem else "Название не найдено"

    # 2. Цена
    price_elem = (car.find('meta', itemprop='price') or
                  car.find(attrs={"data-marker": "item-price"}))
    if price_elem:
        car_data['price'] = price_elem.get('content', price_elem.text.strip())
    else:
        car_data['price'] = "Цена не указана"

    # 3. Параметры
    params_elem = (car.find(attrs={"data-marker": "item-specific-params"}) or
                   car.find('div', class_=lambda x: x and 'params' in x.lower()))
    car_data['params'] = params_elem.text.strip() if params_elem else "Параметры не указаны"

    # 4. Ссылка
    link_elem = car.find('a', itemprop='url') or car.find('a', href=True)
    if link_elem:
        car_data['link'] = "https://www.avito.ru" + link_elem.get('href', '')
    else:
        car_data['link'] = "Ссылка не найдена"

    return car_data