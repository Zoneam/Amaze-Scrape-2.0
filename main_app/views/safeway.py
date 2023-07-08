import re
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from ..models.deals import Product, Store
# from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.contrib.auth.decorators import login_required
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = ({ 
      'user-agent': 'Mozilla/5.0 (Windows NT 16.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.132 Safari/537.36',
      'upgrade-insecure-requests': '1',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'en-US,en;q=0.9,en;q=0.8'
    })

def interceptor(request):
    del request.headers['Referer']  # Delete the header first
    request.headers['Referer'] = HEADERS

@login_required
def safeway_query(request):
    if Store.objects.filter(name='Safeway').exists():
        store = Store.objects.get(name='Safeway')
        # print('>>>>>>>>> store exists')
        if store.age() < 1:
            productResults = Product.objects.filter(store = store.id).order_by('-discount')
            return render(request, 'safeway.html', {'productResults': productResults})
        else:
            # print('>>>>>>>>> store expired')
            store.delete()
            Store.objects.create( name='Safeway')
            store = Store.objects.get(name='Safeway')
            # print('>>>>>>>> new store created')
    else:
        Store.objects.create( name='Safeway')
        store = Store.objects.get(name='Safeway')
        # print(">>>>>>>>> store doesn't exist")
    
    productResults = []
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--crash-dumps-dir=/tmp")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # Set the interceptor on the driver
    driver.request_interceptor = interceptor
    driver.get(f'https://www.safeway.com/shop/deals/member-specials.html')
    WebDriverWait(driver,28).until(EC.visibility_of_element_located((By.CLASS_NAME , "product-level-4")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_results = soup.find_all(class_ = "product-card-container")
    if raw_results:
        for idx,result in enumerate(raw_results):
            title = result.find('a', class_ = "product-title__name").text if result.find('a', class_ = "product-title__name") is not None else ''
            was = '.'.join(re.findall(r'\d+', result.find('del', class_ = 'product-price__baseprice').text)) if result.find('del', class_ = 'product-price__baseprice') is not None else ''
            
            current = '.'.join(re.findall(r'\d+', result.find('span', class_ = 'product-price__discounted-price').text))  if result.find('span', class_ = 'product-price__discounted-price') is not None else ''
            aTag = result.find('a') if result.find('a') is not None else ''
            current = current.split(".")[0] + '.' + current.split(".")[1]
            print(was)
            productResult = {
                'store': store,
                'was': was,
                'current': current,
                'title': title,
                'imgLink': f'https://images.albertsons-media.com/is/image/ABS/{aTag["data-bpn"]}?$ecom-product-card-tablet-jpg$&defaultImage=Not_Available',
                'discount': round((1 - (float(current) / float(was))) * 100, 2) if current.replace('.', '', 1).isdigit() and was.replace('.', '', 1).isdigit() else '0',
                'link': f'https://www.safeway.com{aTag["href"]}',
            }
            productResults.append(productResult)
            print(productResult)
    else:
        print("\033[48;5;225m\033[38;5;245m -- No results -- \033[0;0m")
    driver.close()
    productResults = sorted(productResults, key=lambda k: k['discount'], reverse=True)

    for product in productResults:
        Product.objects.create(title = product['title'], discount = product['discount'], store = product['store'], was = product['was'], current = product['current'], imgLink = product['imgLink'], link = product['link'])
    
    return render(request, 'safeway.html', {'productResults': productResults})
