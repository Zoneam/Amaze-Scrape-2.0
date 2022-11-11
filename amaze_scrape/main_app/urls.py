from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    # path('accounts/login/', views.login, name='login'),
    path('search/', views.search, name='search'),
    path('search_items/', views.search_query, name='search_query'),
]
