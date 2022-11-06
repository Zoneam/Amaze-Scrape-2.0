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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.db.models import Sum
# Create your views here.
from django.http import HttpResponse
HEADERS = ({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100102 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"})

def search(request):
    return HttpResponse("Hello, world. You're at the index.")

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

def interceptor(request):
    del request.headers['Referer']  # Delete the header first
    request.headers['Referer'] = HEADERS


def search_query(request):

    queryset = request.GET.get("search")
    productResults = []
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.amazon.com/s?k={queryset}&ref=nb_sb_noss')
    # driver.get(f'https://www.walmart.com/search?q={queryset}')

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # foundAsBot =  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "buy-now-button")))
    if soup.find('title').text == 'Sorry! Something went wrong!':
        print('\033[48;5;225m\033[38;5;245m Sorry! Something went wrong! \033[0;0m')
    else:
        raw_results = soup.find_all( class_ = "s-asin")
        if raw_results:
            for idx,result in enumerate(raw_results):
                # print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
                title = result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal").text if result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal") is not None else ''
                whole = result.find('span', class_ = 'a-price-whole').text if result.find('span', class_ = 'a-price-whole') is not None else ''
                fraction = result.find('span', class_ = 'a-price-fraction').text if result.find('span', class_ = 'a-price-fraction') is not None else ''
                imgLink = result.find('img', class_ = "s-image")['src'] if result.find('img', class_ = "s-image") is not None else ''
                link = result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")['href'] if result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal") is not None else ''
                productResult = {
                    'price': f"${whole}{fraction}",
                    'title': title,
                    'imgLink': imgLink,
                    'link': link,
                }
                productResults.append(productResult)
        else:
            print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    return render(request, 'search.html', {'productResults': productResults})

