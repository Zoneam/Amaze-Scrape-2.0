from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import views
from .views.target import target_query
from .views.walmart import walmart_query
from .views.search_compare import search_compare
from .views.raleys import raleys_query
from .views.safeway import safeway_query

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.search, name='search'),
    path('accounts/signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('search/', views.search, name='search'),
    path('search_compare/', search_compare, name='search_compare'),
    path('raleys_query/', raleys_query, name='raleys_query'),
    path('walmart_query/', walmart_query, name='walmart_query'),
    path('safeway_query/', safeway_query, name='safeway_query'),
    path('target_query/', target_query, name='target_query'),
    path('tradejoes_query/', views.traderjoes_query, name='traderjoes_query'),
    path('wholefoods_query/', views.wholefoods_query, name='wholefoods_query'),
]