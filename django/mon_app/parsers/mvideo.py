import random
import requests
from decimal import Decimal

from bs4 import BeautifulSoup
from mon_app.models import CompetitorProduct


def get_html(url):
    user_agent = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'
    )
    r = requests.get(url, headers={'User-Agent': user_agent})

    if r.ok:
        return r.text
    print(r.status_code)


def refined(s):
    s = s.replace('\t', '').replace('\n', '').replace('\r', '')
    return s


def get_page_data(html):
    data_list = []
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('a', class_="sel-product-tile-title")

    for div in divs:
        url = 'https://www.mvideo.ru' + div.get('href')
        products = div.get('data-product-info').split('{')[1::2]

        for product in products:
            refined_product = refined(product)
            p = '{' + refined_product
            d = eval(p)

            id_product = d.get('productId')
            name = d.get('productName')
            price = d.get('productPriceLocal')
            categoryId = d.get('productCategoryId')
            categoryName = d.get('productCategoryName')
            vendorName = d.get('productVendorName')
            groupId = d.get('productGroupId')
            shop = 'М.видео'

            data = {
                'id_product': id_product,
                'name': name,
                # Генерация цены с рандомайзером для создания образца базы данных МОИХ товаров
                # 'price': float(price) + round(random.uniform(-1, 1) * 400) * 5,
                'price': price,
                'categoryId': categoryId,
                'categoryName': categoryName,
                'vendorName': vendorName.lower().title(),
                'groupId': groupId,
                'url': url,
                'shop': shop,
            }

            print(data)
            data_list.append(data)
    return data_list


def write_db(competitor_products):
    meta = {'updated_count': 0, 'created_count': 0}
    urls = [product.get('url') for product in competitor_products if product.get('url')]
    CompetitorProduct.objects.filter(url__in=urls).update(status=False)

    for competitor_product in competitor_products:
        url = competitor_product.get('url')
        if url:
            price = Decimal(competitor_product.get('price'))
            id_product = int(competitor_product.get('id_product'))
            categoryId = competitor_product.get('categoryId')
            categoryName = competitor_product.get('categoryName')
            vendorName = competitor_product.get('vendorName')
            groupId = competitor_product.get('groupId')
            shop = competitor_product.get('shop')
            name = competitor_product.get('name')

            _, created = CompetitorProduct.objects.update_or_create(
                url=url,
                defaults={
                    'id_product': id_product,
                    'name': name,
                    'price': price,
                    'categoryId': categoryId,
                    'categoryName': categoryName,
                    'vendorName': vendorName,
                    'groupId': groupId,
                    'status': True,
                    'shop': shop,
                }
            )
            if created:
                meta['created_count'] += 1
            else:
                meta['updated_count'] += 1
    return meta


def mvideo(url_target, page_count):
    pattern = url_target + '/f/page={}'
    for i in range(1, int(page_count) + 1):
        url = pattern.format(str(i))
        html = get_html(url)
        product_list = get_page_data(html)
        write_db(product_list)
        product_count_on_page = len(product_list)

        print("-" * 42)
        print(f"На странице номер {i} получено {product_count_on_page} продуктов")
        print("-" * 42)

        meta = write_db(product_list)
        print(f'--> {i}: {meta}')

    all_product_count = int(product_count_on_page) * int(page_count)
    print("-" * 42)
    print(f"Всего на странице {url_target} получено {all_product_count} продуктов")
    print("-" * 42)