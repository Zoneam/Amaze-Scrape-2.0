from django.shortcuts import render
from bs4 import BeautifulSoup
from ..models import Product, Store
# from selenium import webdriver
from seleniumwire import webdriver
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
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
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