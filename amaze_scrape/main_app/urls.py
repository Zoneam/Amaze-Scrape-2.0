from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('search/', views.search, name='search'),
    path('amazon_query/', views.amazon_query, name='amazon_query'),
    path('raleys_query/', views.raleys_query, name='raleys_query'),
    path('walmart_query/', views.walmart_query, name='walmart_query'),
    path('safeway_query/', views.safeway_query, name='safeway_query'),
    path('target_query/', views.target_query, name='target_query'),
    path('tradejoes_query/', views.traderjoes_query, name='traderjoes_query'),
    path('wholefoods_query/', views.wholefoods_query, name='wholefoods_query'),
]