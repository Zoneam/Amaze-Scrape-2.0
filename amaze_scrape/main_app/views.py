import re
import os
import uuid
import time
import schedule
import threading
import string
import math
import pandas as pd
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import requests
from .models import Product, Store
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import login
from django.db.models import Q
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
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = ({ 
      'user-agent': 'Mozilla/5.0 (Windows NT 16.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.132 Safari/537.36',
      'upgrade-insecure-requests': '1',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'en-US,en;q=0.9,en;q=0.8'
    })
HEADERSWM = ({ 
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'upgrade-insecure-requests': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'method': 'GET',
    'authority': 'www.walmart.com',
    'sheme': 'https',
    'cache-control': 'max-age=0',
    'referer': 'https://www.walmart.com/',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    })


def jaccard_similarity(s1, s2):
    s1_words = set(s1.lower().split())
    s2_words = set(s2.lower().split())

    stop_words = {'the', 'and', 'a', 'an', 'of', 'in', 'to', 'that', 'is', 'for', 'it', 'with', 'as', 'was', 'on', 'at', 'by', 'be', 'this', 'which', 'or', 'but', 'not', 'are', 'from', 'they', 'we', 'an', 'said', 'was', 'were', 'he', 'she', 'has', 'have', 'had', 'will', 'its', 'can', 'could', 'would', '&'}
    s1_words = s1_words - stop_words
    s2_words = s2_words - stop_words
    
    return len(s1_words.intersection(s2_words)) / len(s1_words.union(s2_words))


def matching_words_percentage(s1, s2):
    return jaccard_similarity(s1, s2) * 100

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

    wmProductResults = []
    amazonProductResults = []
    compareResults = []
    queryset = request.GET.get("search")
    if not queryset:
        return redirect('search')
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.amazon.com/s?k={queryset}&ref=nb_sb_noss')
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # foundAsBot =  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "buy-now-button")))
    if soup.find('title').text == 'Sorry! Something went wrong!':
        print('\033[48;5;225m\033[38;5;245m Sorry! Something went wrong! \033[0;0m')
    else:
        raw_results = soup.find_all( class_ = "s-asin")
        if raw_results:
            for idx, result in enumerate(raw_results[:8]):
                # print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m", result)
                title = result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal").text if result.find('span', class_ = "a-size-base-plus a-color-base a-text-normal") is not None else ''
                if not title:
                    title = result.find('span', class_ = "a-size-medium a-color-base a-text-normal").text if result.find('span', class_ = "a-size-medium a-color-base a-text-normal") is not None else ''
                whole = result.find('span', class_ = 'a-price-whole').text if result.find('span', class_ = 'a-price-whole') is not None else ''
                fraction = result.find('span', class_ = 'a-price-fraction').text if result.find('span', class_ = 'a-price-fraction') is not None else ''
                imgLink = result.find('img', class_ = "s-image")['src'] if result.find('img', class_ = "s-image") is not None else ''
                link = result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")['href'] if result.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal") is not None else ''
                productResult = {
                    'amazonPrice': float(whole + fraction),
                    'amazontitle': title,
                    'amazonimgLink': imgLink,
                    'amazonlink': link,
                }
                amazonProductResults.append(productResult)
        else:
            print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()

# -------------------- Walmart Block start --------------------------------

    for idx, amazonProductResult in enumerate(amazonProductResults[:8]):
        print(idx, amazonProductResult['amazontitle'])
        target_url=f"https://www.walmart.com/search?q={amazonProductResult['amazontitle']}"
        resp = requests.get(target_url, headers=HEADERSWM)
        # time.sleep(2)
        soup = BeautifulSoup(resp.text, 'html.parser')
        products = soup.findAll("div", class_ = "pa0-xl")

        for idx, product in enumerate(products):
            title = product.find('span', attrs={"data-automation-id": "product-title"}).text if product.find('span', attrs={"data-automation-id": "product-title"}) is not None else ''
            price = product.find('div', attrs={"data-automation-id": "product-price"}).findChildren()[0].text if product.find('div', attrs={"data-automation-id": "product-price"}) is not None else ''
            link = (product.find('a')["href"] if product.find('a')["href"] is not None else '')
            imgLink = (product.find('img')["src"] if product.find('img')["src"] is not None else '')
            productResult = {
                'walMartstore': 'Walmart',
                'walMarttitle': title,
                'walMartprice': float(re.search(r'\$(\d+\.\d+)', price).group(1)),
                'walMartlink': link,
                'walMartimgLink': imgLink,
                'grade': 0,
            }
            wmProductResults.append(productResult)
            
        for idx, wmProductResult in enumerate(wmProductResults):
            wmProductResult['grade'] = math.floor(matching_words_percentage(amazonProductResult['amazontitle'], wmProductResult['walMarttitle']))
        
        sorted_WalMart_list = sorted(wmProductResults, key=lambda x: x['grade'], reverse=True)
        
        if sorted_WalMart_list[0]['grade'] > 30:
            print('>>>>>>>>> Match %',  sorted_WalMart_list[0]['grade'])
            compareResults.append({**amazonProductResult, **sorted_WalMart_list[0]})
    # -------------------- Walmart Block end --------------------
    sortedCompareResults = sorted(compareResults, key=lambda x: x['grade'], reverse=True)

    return render(request, 'amazon.html', {'compareResults': sortedCompareResults})

@login_required
def raleys_query(request):
    if Store.objects.filter(name='Raleys').exists():
        store = Store.objects.get(name='Raleys') # get the store
        print('>>>>>>>>> store exists')
        print(store.id)
        print(store.age())
        if store.age() < 1:
            productResults = Product.objects.filter(store = store.id).order_by('-discount')
            return render(request, 'raleys.html', {'productResults': productResults})
        else:
            print('>>>>>>>>> store expired')
            store.delete()
            Store.objects.create(name='Raleys')
            store = Store.objects.get(name='Raleys')
            print('>>>>>>>> new store created')
    else:
        Store.objects.create(name='Raleys')
        store = Store.objects.get(name='Raleys')
        print(">>>>>>>>> store doesn't exist")
    productResults = []
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--crash-dumps-dir=/tmp")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://shop.raleys.com/shop/categories/52?tags=on_sale')
    WebDriverWait(driver,65).until(EC.presence_of_element_located((By.CLASS_NAME, "add-to-cart-button")))
    html = driver.page_source
    print('html',html)
    driver.implicitly_wait(65)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    if soup.find('title').text == 'Sorry! Something went wrong!':
        print('\033[48;5;225m\033[38;5;24 driver Sorry! Something went wrong! \033[0;0m')
    else:
        raw_results = soup.find_all("li", class_="cell-wrapper")
        if raw_results:
            for idx,result in enumerate(raw_results):
                print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
                title = result.find('div', class_ = "cell-title-text").text if result.find('div', class_ = "cell-title-text") is not None else ''
                was = result.find('span', class_ = 'css-hhuz2w').text if result.find('span', class_ = 'css-hhuz2w') is not None else ''
                current = result.find('span', class_ = 'css-os8wsm').text if result.find('span', class_ = 'css-os8wsm') is not None else ''
                imgLink = result.find('span', class_ = "cell-image")['data-src'] if result.find('span', class_ = "cell-image") is not None else ''
                if "for" in current:
                    current = current.split("for")[-1].strip()[1:]
                else:
                    current = current[1:]
                if "for" in was:
                    was = was.split("for")[-1].strip()[1:]
                else:
                    was = was[1:]

                productResult = {
                    'store': store,
                    'was': f"{was}",
                    'current': current,
                    'title': title,
                    'imgLink': imgLink,
                    'discount': round((1 - (float(current) / float(was))) * 100, 2),
                    'link': 'https://shop.raleys.com/shop/categories/52?tags=on_sale',
                }
                productResults.append(productResult)
        else:
            print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    productResults = sorted(productResults, key=lambda k: k['discount'], reverse=True)
    for product in productResults:
        Product.objects.create(title = product['title'], discount = product['discount'], store = product['store'], was = product['was'], current = product['current'], imgLink = product['imgLink'], link = product['link'])
    return render(request, 'raleys.html', {'productResults': productResults})

@login_required
def safeway_query(request):
    if Store.objects.filter(name='Safeway').exists():
        store = Store.objects.get(name='Safeway')
        print('>>>>>>>>> store exists')
        print(store)
        print(store.age())
        if store.age() < 1:
            productResults = Product.objects.filter(store = store.id).order_by('-discount')
            return render(request, 'safeway.html', {'productResults': productResults})
        else:
            print('>>>>>>>>> store expired')
            store.delete()
            Store.objects.create( name='Safeway')
            store = Store.objects.get(name='Safeway')
            print('>>>>>>>> new store created')
    else:
        Store.objects.create( name='Safeway')
        store = Store.objects.get(name='Safeway')
        print(">>>>>>>>> store doesn't exist")
    
    productResults = []
    options = Options()
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--crash-dumps-dir=/tmp")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.safeway.com/shop/deals/member-specials.html')
    print(driver)
    WebDriverWait(driver,28).until(EC.visibility_of_element_located((By.CLASS_NAME , "product-level-4")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_results = soup.find_all(class_ = "product-card-container")
    if raw_results:
        for idx,result in enumerate(raw_results):
            print(f"\033[48;5;225m\033[38;5;245m -------------{idx+1}---------- \033[0;0m")
            title = result.find('a', class_ = "product-title__name").text if result.find('a', class_ = "product-title__name") is not None else ''
            was = '.'.join(re.findall(r'\d+', result.find('del', class_ = 'product-price__baseprice').text)) if result.find('del', class_ = 'product-price__baseprice') is not None else ''
            current = '.'.join(re.findall(r'\d+', result.find('span', class_ = 'product-price__discounted-price').text))  if result.find('span', class_ = 'product-price__discounted-price') is not None else ''
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
    HEADERSWM = ({ 
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'upgrade-insecure-requests': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'method': 'GET',
    'authority': 'www.walmart.com',
    'sheme': 'https',
    'cache-control': 'max-age=0',
    'referer': 'https://www.walmart.com/',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    })
    productResults = []
    # queryset = request.GET.get("search")
    #----------------------------------------------
    target_url=f"https://www.walmart.com/shop/deals"
    resp = requests.get(target_url, headers=HEADERSWM)
    time.sleep(2)
    soup = BeautifulSoup(resp.text, 'html.parser')
    products = soup.findAll("div", class_ = "pa0-xl")

    for idx, product in enumerate(products):
        title = product.find('span', attrs={"data-automation-id": "product-title"}).text if product.find('span', attrs={"data-automation-id": "product-title"}) is not None else ''
        price = product.find('div', attrs={"data-automation-id": "product-price"}).findChildren()[0].text if product.find('div', attrs={"data-automation-id": "product-price"}) is not None else ''
        was = product.find('div', class_ = 'gray mr1 strike f7 f6-l').text if product.find('div', class_ = 'gray mr1 strike f7 f6-l') is not None else ''
        link = (product.find('a')["href"] if product.find('a')["href"] is not None else '')
        imgLink = (product.find('img')["src"] if product.find('img')["src"] is not None else '')
        productResult = {
            'store': 'Walmart',
            'title': title,
            'price': price,
            'was': was,
            'link': link,
            'imgLink': imgLink,
        }
        productResults.append(productResult)
    
    if("Robot or human" in resp.text):
        print(True)
    else:
        print(False)
    return render(request, 'walmart.html', {'productResults': productResults})


def target_query(request):
    return HttpResponse('<h1>Under Construction</h1>')

def traderjoes_query(request):
    return HttpResponse('<h1>Under Construction</h1>')

def wholefoods_query(request):
    return HttpResponse('<h1>Under Construction</h1>')