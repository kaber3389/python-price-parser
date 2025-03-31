from django.shortcuts import render
import re

from .parsers.mvideo import mvideo
from .parsers.citilink import citilink
from .parsers.wildberries import wildberries


def index(request):
    return render(request, 'mon_app/index.html')


def support(request):
    return render(request, 'mon_app/support/support.html')


def parsing(request):
    if request.method == 'GET':
        return render(request, 'mon_app/index.html')
    elif request.method == 'POST':
        url_target = request.POST.get('url_target')
        page_count = request.POST.get('page_count')

        # Check if there is a url_target and page_count
        if url_target and page_count:
            # Checking validity of page_count
            if (re.match(r'\d\b', page_count) or re.match(r'\d\d\b', page_count)) and not re.match('0', page_count):
                # If target_url is from mvideo
                if re.match('https://www.mvideo.ru/', url_target):
                    mvideo(url_target, page_count)
                # If target_url is from citilink
                elif re.match('https://www.citilink.ru/', url_target):
                    citilink(url_target, page_count)
                # If target_url is from wildberries
                elif re.match('https://www.wildberries.ru/', url_target):
                    wildberries(url_target, page_count)
                # If target_url is invalid
                else:
                    return render(request, 'mon_app/exceptions/invalid_url.html')
            # If page_count is invalid
            else:
                return render(request, 'mon_app/exceptions/invalid_page_count.html')
        # If page_count doesn’t exist
        elif url_target and not page_count:
            return render(request, 'mon_app/exceptions/not_page_count.html')
        # If url_target doesn’t exist
        elif page_count and not url_target:
            return render(request, 'mon_app/exceptions/not_url_target.html')
        # If neither exists
        else:
            return render(request, 'mon_app/exceptions/not_arguments.html')

        return render(request, 'mon_app/success.html', context={
            'url_target': url_target,
            'page_count': page_count,
        })