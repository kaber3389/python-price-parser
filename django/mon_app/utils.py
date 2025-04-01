from django.contrib import messages
from django.db.models import Q
from unicodedata import decimal

from .models import CompetitorProduct, Match, MyProduct


def status_true_util(modeladmin, request, queryset):
    rows_updated = queryset.update(status=True)
    if rows_updated == 1:
        message_bit = "1 Competitor`s product was"
    else:
        message_bit = f"{rows_updated} Competitor`s products were"
    modeladmin.message_user(request, f"{message_bit} successfully marked as True.")


def status_false_util(modeladmin, request, queryset):
    rows_updated = queryset.update(status=False)
    if rows_updated == 1:
        message_bit = "1 Competitor`s product was"
    else:
        message_bit = f"{rows_updated} Competitor`s products were"
    modeladmin.message_user(request, f"{message_bit} successfully marked as False.")


#Сравнение товаров конкурента со своими товарами
def start_matching_competitor_util(modeladmin, request, queryset):
    products_competitor = queryset.values('id_product', 'name', 'price', 'shop', 'url')

    for product_competitor in products_competitor:
        shop_competitor = product_competitor.get('shop')
        id_product_competitor = product_competitor.get('id_product')
        name_competitor = product_competitor.get('name')
        price_competitor = product_competitor.get('price')
        url_competitor = product_competitor.get('url')

        search_query = name_competitor
        keywords = [word.strip('",.') for word in search_query.split() if len(word) > 2]
        from django.db.models import Q
        query = Q()
        for keyword in keywords:
            query |= Q(name__icontains=keyword)

        product_my = MyProduct.objects.filter(query).values(
            'id_product', 'name', 'price'
        ).first()

        if not product_my:
            continue

        id_product_my = product_my.get('id_product')
        name_my = product_my.get('name')
        price_my = product_my.get('price')
        diff = price_my - price_competitor

        if diff <= 0:
            status = True
        else:
            status = False

        Match.objects.update_or_create(
            id_product_competitor=id_product_competitor,
            defaults={
                'id_product': id_product_my,
                'name_my': name_my,
                'price_my': price_my,
                'shop_competitor': shop_competitor,
                'name_competitor': name_competitor,
                'url': url_competitor,
                'price_competitor': price_competitor,
                'diff': diff,
                'status': status,
            }
        )
    modeladmin.message_user(request, "Объекты сравнены")


def start_matching_my_util(modeladmin, request, queryset):
    products_my = queryset.values('id_product', 'name', 'price')

    for product_my in products_my:
        id_product_my = product_my.get('id_product')
        name_my = product_my.get('name')
        price_my = product_my.get('price')

        search_query = name_my
        keywords = [word.strip('",.') for word in search_query.split() if len(word) > 2]
        from django.db.models import Q
        query = Q()
        for keyword in keywords:
            query |= Q(name__icontains=keyword)
        product_competitor = CompetitorProduct.objects.filter(query).first()  # Объект модели

        if not product_competitor:
            continue
        shop_competitor = product_competitor.shop
        id_product_competitor = product_competitor.id_product
        name_competitor = product_competitor.name
        price_competitor = product_competitor.price

        diff = price_my - price_competitor
        status = True if diff < 0 else False if diff > 0 else None

        Match.objects.update_or_create(
            id_product=id_product_my,
            id_product_competitor=id_product_competitor,
            defaults={
                'name_my': name_my,
                'price_my': price_my,
                'shop_competitor': shop_competitor,
                'name_competitor': name_competitor,
                'price_competitor': price_competitor,
                'diff': diff,
                'status': status,
            }
        )
    modeladmin.message_user(request, "Объекты сравнены")

def analyze_util(modeladmin, request, queryset):
    count = queryset.count()
    prices_competitor = queryset.values('price_competitor')
    prices_my = queryset.values('price_my')

    sum_price_competitor = 0
    for price_competitor in prices_competitor:
        sum_price_competitor += price_competitor.get('price_competitor')

    sum_price_my = 0
    for price_my in prices_my:
        sum_price_my += price_my.get('price_my')

    avg_competitor = sum_price_competitor / count
    avg_my = sum_price_my / count

    if avg_my < avg_competitor:
        percent_diff = round(100 - (avg_my / avg_competitor * 100), 2)
        messages.info(
            request,
            f"Средняя цена у конкурента: {avg_competitor}, средняя цена у меня: {avg_my}. "
            f"Мои товары на {percent_diff} процентов дешевле."
        )
    else:
        percent_diff = round(100 - (avg_competitor / avg_my * 100), 2)
        messages.error(
            request,
            f"Средняя цена у конкурента: {avg_competitor}, средняя цена у меня: {avg_my}. "
            f"Мои товары на {percent_diff} процентов дороже."
        )