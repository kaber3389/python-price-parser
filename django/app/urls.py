"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from mon_app.api.competitor_products_api import api_productcompetitor_id, api_productcompetitor
from mon_app.api.my_products_api import api_productmy_id, api_productmy
from mon_app.api.match_api import api_match_id, api_match
from mon_app.views import index, parsing, support

urlpatterns = [
    path('', index, name='index_url'),
    path('parsing/', parsing, name='parsing_url'),
    path('support/', support, name='support_url'),
    path('api/productcompetitor/<id>', api_productcompetitor_id, name='api_productcompetitor_id_url'),
    path('api/productcompetitor/', api_productcompetitor, name='api_productcompetitor_url'),
    path('api/productmy/<id>', api_productmy_id, name='api_productmy_id_url'),
    path('api/productmy/', api_productmy, name='api_productmy_url'),
    path('api/match/<id>', api_match_id, name='api_match_id_url'),
    path('api/match/', api_match, name='api_match_url'),
]