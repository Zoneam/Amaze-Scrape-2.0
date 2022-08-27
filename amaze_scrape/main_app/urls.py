from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/signup/', views.signup, name='signup'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('search/', views.search, name='search'),
    path('search_items/', views.search_query, name='search_query'),
]
