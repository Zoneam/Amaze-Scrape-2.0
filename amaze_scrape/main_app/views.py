import os
import uuid
# from datetime import date
from django.shortcuts import render, redirect
# import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
# from django.http import HttpResponseRedirect
# from django.dispatch import receiver
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.views.generic import ListView, DetailView
# from .models import 
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.models import User
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
# Create your views here.
from django.http import HttpResponse
HEADERS = ({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"})

URL = "https://www.amazon.com/Sony-PlayStation-Pro-1TB-Console-4/dp/B07K14XKZH/"


def search(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('myaccount/')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

def search(request):
    return render(request, 'search.html')

def search_query(request):
    queryset = request.GET.get("search")
    productResults = {}
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)


    driver.get(f'https://www.amazon.com/s?k={queryset}&ref=nb_sb_noss')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_results = soup.find_all( class_ = "s-asin")
    for result in raw_results:
        print(result.find('span', class_ = "a-text-normal").text)
        print(result.find('img', class_ = "s-image").text)
        print(result.find('span', class_ = "a-price-whole"), result.find('span', class_ = "a-price-fraction"))
        print(result.find('a', class_ = "a-link-normal").get('href'))
        print(result.find('span', class_ = "a-text-normal").text)
        print(result.find('span', class_ = "a-text-normal").text)
        # print(result.find('span', class_ = "a-text-normal").text)
        print('------------------------------')
    # print(span)
    # time.sleep(5)
    # print (len(span))
    driver.close()
    return render(request, 'search.html')

