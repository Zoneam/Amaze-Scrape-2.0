import re
import math
from ..models.favorites import Wm_Product, Amazon_Product, Favorite
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.decorators import login_required
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.core.utils import ChromeType
from django.http import JsonResponse
from ..forms import ProductForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

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

def interceptor(request):
    del request.headers['Referer']  # Delete the header first
    request.headers['Referer'] = HEADERS

def jaccard_similarity(s1, s2):
    s1_words = set(s1.lower().split())
    s2_words = set(s2.lower().split())
    stop_words = {'the', 'and', 'a', 'an', 'of', 'in', 'to', 'that', 'is', 'for', 'it', 'with', 'as', 'was', 'on', 'at', 'by', 'be', 'this', 'which', 'or', 'but', 'not', 'are', 'from', 'they', 'we', 'an', 'said', 'was', 'were', 'he', 'she', 'has', 'have', 'had', 'will', 'its', 'can', 'could', 'would', '&'}
    s1_words = s1_words - stop_words
    s2_words = s2_words - stop_words
    
    return len(s1_words.intersection(s2_words)) / len(s1_words.union(s2_words))

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def matching_words_percentage(s1, s2):
    return jaccard_similarity(s1, s2) * 100

@login_required
def search_compare(request):
    page = request.GET.get('page')
    # Checking if there is a page number to pull data from user session
    if not page:
        amazon_product_results = amazon_product_search(request)
        sorted_compare_results = walmart_compare_results(amazon_product_results)
        # Store the sorted_compare_results in the session for pagination purposes
        request.session['sorted_compare_results'] = sorted_compare_results
    else:
        # Use the stored results for pagination
        sorted_compare_results = request.session.get('sorted_compare_results', [])

    paginator = Paginator(sorted_compare_results, 5)  # Show # items per page
    compare_results_page = paginator.get_page(page)
    return render(request, 'amazon.html', {'compare_results': compare_results_page})


# ------------------- Amazon Scraper --------------------------------
def amazon_product_search(request,):
    amazon_product_results = []
    queryset = request.GET.get("search")
    # if not queryset:
    #     return redirect('search')
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),options=options)
    # Setting interceptor on the driver to inject headers
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
                product_result = {
                    'amazonPrice': float(whole + fraction) if isfloat(whole + fraction) else (whole + fraction),
                    'amazontitle': title,
                    'amazonimgLink': imgLink,
                    'amazonlink': link,
                }
                amazon_product_results.append(product_result)
        else:
            print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    return amazon_product_results


# -------------------- Walmart Scraper --------------------------------
def walmart_compare_results(amazon_product_results):
    wm_product_results = []
    compare_results = []

    for idx, amazon_product_result in enumerate(amazon_product_results[:8]):
        target_url=f"https://www.walmart.com/search?q={amazon_product_result['amazontitle']}"
        resp = requests.get(target_url, headers=HEADERSWM)
        # time.sleep(2)
        soup = BeautifulSoup(resp.text, 'html.parser')
        products = soup.findAll("div", class_ = "pa0-xl")

        for idx, product in enumerate(products):
            title = product.find('span', attrs={"data-automation-id": "product-title"}).text if product.find('span', attrs={"data-automation-id": "product-title"}) is not None else ''
            price = product.find('div', attrs={"data-automation-id": "product-price"}).findChildren()[0].text if product.find('div', attrs={"data-automation-id": "product-price"}) is not None else ''
            link = (product.find('a')["href"] if product.find('a')["href"] is not None else '')
            imgLink = (product.find('img')["src"] if product.find('img')["src"] is not None else '')
            product_result = {
                'walMartstore': 'Walmart',
                'walMarttitle': title,
                'walMartprice': float(re.search(r'\$(\d+\.\d+)', price).group(1)) if re.search(r'\$(\d+\.\d+)', price) is not None else price,
                'walMartlink': link,
                'walMartimgLink': imgLink,
                'grade': 0,
            }
            wm_product_results.append(product_result)
            
        for idx, wmproduct_result in enumerate(wm_product_results):
            wmproduct_result['grade'] = math.floor(matching_words_percentage(amazon_product_result['amazontitle'], wmproduct_result['walMarttitle']))
        
        sorted_WalMart_list = sorted(wm_product_results, key=lambda x: x['grade'], reverse=True)
        print('>>>>>>>>> sorted_WalMart_list', sorted_WalMart_list)
        if sorted_WalMart_list:
            if sorted_WalMart_list[0]['grade'] > 30:
                print('>>>>>>>>> Match %',  sorted_WalMart_list[0]['grade'])
                compare_results.append({**amazon_product_result, **sorted_WalMart_list[0]})
    # -------------------- Walmart Block end --------------------
    sorted_compare_results = sorted(compare_results, key=lambda x: x['grade'], reverse=True)
    return sorted_compare_results


@login_required
def favorite(request):
    if request.method == 'POST':
        wm_title = request.POST.get('wm_title')
        wm_price = request.POST.get('wm_price')
        wm_link = request.POST.get('wm_link')
        wm_imgLink = request.POST.get('wm_imgLink')
        amazon_title = request.POST.get('amazon_title')
        amazon_price = request.POST.get('amazon_price')
        amazon_link = request.POST.get('amazon_link')
        amazon_imgLink = request.POST.get('amazon_imgLink')
        grade = request.POST.get('grade')

        amazon_product = Amazon_Product.objects.create(
            amazon_title=amazon_title,
            amazon_price=amazon_price,
            amazon_link=amazon_link,
            amazon_imgLink=amazon_imgLink,
            
        )

        # Create a new Walmart product
        wm_product = Wm_Product.objects.create(
            wm_title=wm_title,
            wm_price=wm_price,
            wm_link=wm_link,
            wm_imgLink=wm_imgLink,
            grade=grade
        )

        # Add both products to the user's favorites
        Favorite.objects.create(
            user=request.user,
            amazon_product=amazon_product,
            wm_product=wm_product,
        )

    return JsonResponse({'success': True})

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'favorites.html', {'favorites': favorites})

@csrf_exempt
@login_required
def unfavorite(request):
    if request.method == 'DELETE':
        favorite_id = request.GET.get('favorite_id')
        favorite = get_object_or_404(Favorite, id=favorite_id)
        Amazon_Product.objects.filter(id=favorite.amazon_product.id).delete()
        Wm_Product.objects.filter(id=favorite.wm_product.id).delete()
        favorite.delete()
        return JsonResponse({'success': True, 'deleted_favorite_id': favorite_id})
    else:
        return JsonResponse({'success': False})