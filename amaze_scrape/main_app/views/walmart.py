import time
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests


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