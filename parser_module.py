import csv  # Импорт пакета для работы с csv-файлами
import requests  # Импорт пакета для работы с HTTP-запросами
from bs4 import BeautifulSoup  # Импорт пакета для того, чтобы распарсить дерево

# Глобальные переменные
HEADERS_AUTORU = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.456',
    'accept': '*/*'
}
PATH_AUTORU = '../autoru.csv'
HEADERS_AVITO = {}
PATH_AVITO = '../avito.csv'


# Функция для получения web-страницы
def get_html(url, headers, params=None):
    r = requests.get(url, headers=headers, params=params)
    r.encoding = 'utf8'
    return r


# Функция для парсинга большого количества страниц Auto.Ru
# TODO Узнать также ли узнаётся количество страниц на Avito.ru
def get_pages_count_autoru(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='Button__text')  # Разбиваем стариницу по наименованию кнопок.
    # TODO Необходимо добавить обработку, если страниц меньше, чем 1.
    if pagination:
        for i in (0, len(pagination) - 1):
            print(str(i) + ' ' + str(pagination[i]))
            return int(pagination[-5].get_text())  # 31.10.2021 - Определение количества строк по индексу "-5"
        else:
            return 1


# Функция для получения контента из html
def get_content_autoru(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem')  # Находим все машины
    cars = []  # Массив для хранения данных по машинам
    i = 0
    for item in items:
        # Тут будут прописываться параметры объявления, информация с которых будет забираться
        cars.append({
            'name': item.find('a', class_='Link ListingItemTitle__link').get_text(strip=True),
            'price': item.find('div', class_='ListingItemPrice__content').get_text(strip=True),
            'link': item.find('a', class_='Link ListingItemTitle__link').get('href')
        })
        # Выводим данные, полученные с сайта
        print(str(i) +
              ' ' + cars[i].get('name') +
              ' ' + cars[i].get('price') +
              ' ' + cars[i].get('link'))
        i += 1
    return cars


# Функция для создания и сохранения в файле данных
def save_file(cars, path):
    # Эта функция будет необходима на данный момент для тестирования получения результатов
    with open(path, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Цена', 'Ссылка'])
        for car in cars:
            writer.writerow([car['name'], car['price'], car['link']])


# Генератор ссылок для auto.ru
def url_generator_autoru():
    car_brand = input('Введите марку:  ')
    car_model = input('Введите модель: ')
    url = str('https://auto.ru/sankt-peterburg/cars/all/?catalog_filter=mark%3D'
              + car_brand.upper()
              + '%2Cmodel%3D'
              + car_model.upper()
              + '&sort=cr_date-desc')
    print('Искомый URL: ' + url)
    return url


# Функция парсинга с сайта auto.ru
def parse_autoru(search_params=None):
    if search_params is None:
        url = url_generator_autoru()
    else:
        url = str('https://auto.ru/sankt-peterburg/cars/all/?catalog_filter=mark%3D'
                        + search_params['brand'].upper()
                        + '%2Cmodel%3D'
                        + search_params['model'].upper()
                        + '&sort=cr_date-desc')
    html = get_html(url, HEADERS_AUTORU)

    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count_autoru(html.text)
        for page in range(1, pages_count + 1):
            print('\n')
            print(f'Парсинг страницы {page} из {pages_count} ...')
            html = get_html(url, HEADERS_AUTORU, params={'page': page})
            cars.extend(get_content_autoru(html.text))
        save_file(cars, PATH_AUTORU)
        print('\n\n' + f'Получено {len(cars)} автомобилей')
        return cars
    else:
        print('ERROR')

