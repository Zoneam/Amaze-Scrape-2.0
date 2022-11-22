import re
import os
import uuid
import time
import schedule
import threading
# import chromedriver from './chromedriver';
import pandas as pd
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from .models import Product, Store
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.db.models import Sum
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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

@login_required
def amazon_query(request):
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

@login_required
def raleys_query(request):
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

@login_required
def safeway_query(request):
    if (Store.objects.filter(user=request.user).exists()):
        store = Store.objects.get(user=request.user)
        print('>>>>>>>>> store exists')
        print(store.age())
        if store.age() < 1:
            productResults = Product.objects.filter(store = store.id)
            return render(request, 'safeway.html', {'productResults': productResults})
        else:
            print('>>>>>>>>> store expired')
            store.delete()
            Store.objects.create(user=request.user, name='Safeway')
            store = Store.objects.get(user=request.user)
            print('>>>>>>>> new store created')
    else:
        Store.objects.create(user=request.user, name='Safeway')
        store = Store.objects.get(user=request.user)
        print(">>>>>>>>> store doesn't exist")

    productResults = []
    options = Options()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--crash-dumps-dir=/tmp")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(executable_path = os.environ.get('CHROMEDRIVER_PATH'),options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.safeway.com/shop/deals/member-specials.html')
    WebDriverWait(driver,28).until(EC.visibility_of_element_located((By.CLASS_NAME , "aproduct-grid-v2")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup)
    raw_results = soup.find_all( class_ = "product-item-inner")
    if raw_results:
        for idx,result in enumerate(raw_results):
            print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
            title = result.find('a', class_ = "product-title").text if result.find('a', class_ = "product-title") is not None else ''
            was = '.'.join(re.findall(r'\d+', result.find('span', class_ = 'product-strike-base-price').text)) if result.find('span', class_ = 'product-strike-base-price') is not None else ''
            current = '.'.join(re.findall(r'\d+', result.find('span', class_ = 'product-price product-strike-price').text))  if result.find('span', class_ = 'product-price product-strike-price') is not None else ''
            aTag = result.find('a') if result.find('a') is not None else ''
            productResult = {
                'store': store,
                'was': was,
                'current': current,
                'title': title,
                'imgLink': f'https://images.albertsons-media.com/is/image/ABS/{aTag["data-bpn"]}?$ecom-product-card-tablet-jpg$&defaultImage=Not_Available',
                'discount': round((1 - (float(current) / float(was))) * 100, 2),
                'link': f'https://www.safeway.com{aTag["href"]}',
            }
            productResults.append(productResult)
    else:
        print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    productResults = sorted(productResults, key=lambda k: k['discount'], reverse=True)

    for product in productResults:
        Product.objects.create(title = product['title'], discount = product['discount'], store = product['store'], was = product['was'], current = product['current'], imgLink = product['imgLink'], link = product['link'])
    
    return render(request, 'safeway.html', {'productResults': productResults})


def walmart_query(request):
    return HttpResponse('<h1>Under Construction</h1>')

def target_query(request):
    return HttpResponse('<h1>Under Construction</h1>')

def traderjoes_query(request):
    return HttpResponse('<h1>Under Construction</h1>')

def wholefoods_query(request):
    return HttpResponse('<h1>Under Construction</h1>')