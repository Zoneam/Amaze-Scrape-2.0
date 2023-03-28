import re
import math
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.decorators import login_required
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.core.utils import ChromeType

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

    wmProductResults = []
    amazonProductResults = []
    compareResults = []
    queryset = request.GET.get("search")
    if not queryset:
        return redirect('search')
    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),options=options)
    # driver = webdriver.Chrome()
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
                    'amazonPrice': float(whole + fraction) if isfloat(whole + fraction) else (whole + fraction),
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
                'walMartprice': float(re.search(r'\$(\d+\.\d+)', price).group(1)) if re.search(r'\$(\d+\.\d+)', price) is not None else price,
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