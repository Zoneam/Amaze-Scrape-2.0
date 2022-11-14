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
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.db.models import Sum
from selenium.webdriver.common.action_chains import ActionChains
import threading
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import HttpResponse
HEADERS = ({ 
      'user-agent': 'Mozilla/5.0 (Windows NT 16.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.132 Safari/537.36',
      'upgrade-insecure-requests': '1',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'en-US,en;q=0.9,en;q=0.8'
    })

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
            return redirect('/search/')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def search(request):
    return render(request, 'search.html')

def interceptor(request):
    del request.headers['Referer']  # Delete the header first
    request.headers['Referer'] = HEADERS


def search_query(request):
    queryset = request.GET.get("search")
    if not queryset:
        return redirect('search')
    productResults = []
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.amazon.com/s?k={queryset}&ref=nb_sb_noss')
    # -------------------- Walmart Block start --------------------
    # driver.get(f'https://www.walmart.com/search?q={queryset}')
    # action = ActionChains(driver)
    # holdBtn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "px-captcha")))
    # action.click_and_hold(on_element = holdBtn)
  
    # # perform the operation
    # action.perform()
    # time.sleep(15)
    # action.release(holdBtn)
    # action.perform()
    # time.sleep(3)
    # action.release(holdBtn)
    # -------------------- Walmart Block end --------------------
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # foundAsBot =  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "buy-now-button")))
    if soup.find('title').text == 'Sorry! Something went wrong!':
        print('\033[48;5;225m\033[38;5;245m Sorry! Something went wrong! \033[0;0m')
    else:
        raw_results = soup.find_all( class_ = "s-asin")
        if raw_results:
            for idx,result in enumerate(raw_results):
                print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
                title = result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal").text if result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal") is not None else ''
                if not title:
                    title = result.find('span', class_ = "a-size-medium a-color-base a-text-normal").text if result.find('span', class_ = "a-size-medium a-color-base a-text-normal") is not None else ''
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
    return render(request, 'amazon.html', {'productResults': productResults})

def raleys_query(request):
    print('Raleys')
    productResults = []
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://shop.raleys.com/shop/categories/52?tags=on_sale')
    WebDriverWait(driver,65).until(EC.visibility_of_element_located((By.ID, "content")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)
    if soup.find('title').text == 'Sorry! Something went wrong!':
        print('\033[48;5;225m\033[38;5;24 driver Sorry! Something went wrong! \033[0;0m')
    else:
        raw_results = soup.find_all( class_ = "cell-wrapper")
        # print(raw_results)
        if raw_results:
            for idx,result in enumerate(raw_results):
                print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
                title = result.find('div', class_ = "cell-title-text").text if result.find('div', class_ = "cell-title-text") is not None else ''
                was = result.find('span', class_ = 'css-hhuz2w').text if result.find('span', class_ = 'css-hhuz2w') is not None else ''
                current = result.find('span', class_ = 'css-os8wsm').text if result.find('span', class_ = 'css-os8wsm') is not None else ''
                imgLink = result.find('span', class_ = "cell-image")['data-src'] if result.find('span', class_ = "cell-image") is not None else ''
                print('------>>>>>')
                # link = result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")['href'] if result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal") is not None else ''
                productResult = {
                    'was': f"{was}",
                    'current': current,
                    'title': title,
                    'imgLink': imgLink,
                    'discount': round((1 - (float(current[1:]) / float(was[1:]))) * 100, 2),
                    # 'link': link,
                }
                productResults.append(productResult)
        else:
            print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    productResults = sorted(productResults, key=lambda k: k['discount'], reverse=True)
    return render(request, 'raleys.html', {'productResults': productResults})