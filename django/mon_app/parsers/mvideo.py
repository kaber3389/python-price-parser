import random
import requests
from decimal import Decimal

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mon_app.models import CompetitorProduct


def get_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "mvid-product-cards-list-container"))
    )
    html = driver.page_source
    driver.quit()
    return html


def refined(s):
    s = s.replace('\t', '').replace('\n', '').replace('\r', '')
    return s


def get_page_data(html):
    data_list = []
    soup = BeautifulSoup(html, 'lxml')
    articles = soup.find_all('div', class_="product-cards-layout__item")

    for article in articles:
        url = article.find('a', class_='product-title__text').get('href')
        id_product = url.split('/')[-1].split('-')[-1]
        name = article.find('a', class_='product-title__text').text.strip()
        price_string = article.find('span', class_='price__main-value').text.strip()
        price = ''.join(filter(str.isdigit, price_string))
        categoryId = get_category_id(article.attrs)
        categoryName = name.split()[0]

        supplier_link = article.find('div', class_='product-card--list__price-checkout').find('mvid-supplier-and-multioffer-link')
        if supplier_link:
            supplier_name = supplier_link.find('p', class_='product-supplier__name')
            if supplier_name:
                vendorName = supplier_name.text.strip()
            else:
                vendorName = "-"

        shop = 'М.видео'

        data = {
            'id_product': id_product,
            'name': name,
            'price': price,
            'categoryId': categoryId,
            'categoryName': categoryName,
            'vendorName': vendorName,
            'url': url,
            'shop': shop,
        }
        data_list.append(data)
    return data_list

def get_category_id(attrs):
    for attr_name in attrs:
        if attr_name.startswith('_ngcontent-serverapp-c'):
            return attr_name.split('c')[-1]
    return None

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
    product_count_on_page = 0
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