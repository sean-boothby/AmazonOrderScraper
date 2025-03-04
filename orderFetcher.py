# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 19:01:32 2025

@author: Sean
"""

cookie = 'ubid-main=132-8193239-7735707; at-main=Atza|IwEBIJKrSrhkr0mEg0F9xl3k6CLUyze8mz0JaKmhQn8DRn5N4UyzyHmycAASCs0WOu2QwDtXjPP9J1Cccr4ppc4Ag5l65vrTWvX4MdmTqQ1KPwE5dhBTvh2G8ZHGmmm5gJkg933n_HwqAd45-FPJpwGrUSjcmKatuJocPiC3MXlFihF2QqCfdVB_vdMbs5uzmDvhPMF27RRmcqJt7p2-dAj5XE9uffrxq3HGVIqmIHRp0pbMcg; x-main="e4e28e9CSrPaTOXzWuU1WychwyEiRHproGQxeiugVNti?LjoYhYnF8MzZHYctJ0B"'
cookietwo = 'ubid-main=132-8193239-7735707; at-main=Atza|IwEBIJKrSrhkr0mEg0F9xl3k6CLUyze8mz0JaKmhQn8DRn5N4UyzyHmycAASCs0WOu2QwDtXjPP9J1Cccr4ppc4Ag5l65vrTWvX4MdmTqQ1KPwE5dhBTvh2G8ZHGmmm5gJkg933n_HwqAd45-FPJpwGrUSjcmKatuJocPiC3MXlFihF2QqCfdVB_vdMbs5uzmDvhPMF27RRmcqJt7p2-dAj5XE9uffrxq3HGVIqmIHRp0pbMcg; x-main="e4e28e9CSrPaTOXzWuU1WychwyEiRHproGQxeiugVNti?LjoYhYnF8MzZHYctJ0B"; sess-at-main="Zr8Xm0+lru4q3wkDjkiZmj1z+Ry18mIUpYm+tg2pJV8="'



import requests
import json
from bs4 import BeautifulSoup
import time
import re
import sys

order_history = []

ubid_main = sys.argv[1]
at_main = sys.argv[2] #at-main
x_main = sys.argv[3] # x-main
sess_at_main = sys.argv[4] # sess-at-main

# Construct cookies using command-line arguments
cookie_orders = f"ubid-main={ubid_main}; at-main={at_main}; x-main={x_main}"
cookie_price = f"ubid-main={ubid_main}; at-main={at_main}; x-main={x_main}; sess-at-main={sess_at_main}"



def makerequest(orderindex):
    url = "https://www.amazon.com/your-orders/orders?startIndex={}&orderFilter=RETAIL&timeFilter=months-3&enablePosy=false".format(orderindex)
    headers = {
        "Host": "www.amazon.com",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cookie": cookie_orders,
        "device-memory": "8",
        "downlink": "10",
        "dpr": "2",
        "ect": "4g",
        "priority": "u=1, i",
        "referer": "https://www.amazon.com/your-orders/orders",
        "rtt": "50",
        "sec-ch-device-memory": "8",
        "sec-ch-dpr": "2",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-viewport-width": "400",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
        "viewport-width": "400",
        "x-requested-with": "XMLHttpRequest"
    }
    response = requests.get(url, headers=headers)
    return response
        
        
def test_moreorders(r):
    # Split the response by '&&&' to separate different sections
    sections = r.text.split('&&&')
    
    order_count = 0
    # Look for sections that contain the item-card div, which represents an order
    for section in sections:
        if 'item-card' in section:
            order_count += 1
    print(str(order_count))
    if order_count > 0:        
        return True
    else:
        return False
    
def parsedata(r):
    sections = r.text.split('&&&')
    for section in sections:
        if 'item-card' in section:
            html_content = section.replace('["append","div.your-orders-mobile-orders-container","', '').replace('"]', '').replace('\\n', '').replace('\\', '')
            soup = BeautifulSoup(html_content, 'html.parser')

            link = soup.find('a', class_='item-card__link')
            order_id = next((param.split('=')[1] for param in link['href'].split('&') if param.startswith('orderId=')), None)
            description = link['aria-label'] if link and 'aria-label' in link.attrs else None
            price = get_price(order_id)
            print(f"Order ID: {order_id}" if order_id else "No order ID found.")
            print(f"Description: {description}" if description else "No description found.")
            print(price)
            order_history.append({'order_id': order_id, 'description': description, 'price': price})
            time.sleep(1)    
    
def parseprice(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # price_elements = soup.find_all(text=True)
    price_pattern = re.compile(r"\$\d*\.\d{2}")

# Find all text elements in the HTML
    for text in soup.stripped_strings:
        match = price_pattern.search(text)
        if match:
            # print(match.group())  # Print the first valid price found
            return match.group()
    
def get_price(oid):
    # Construct the request URL with the provided order ID
    base_url = "https://www.amazon.com/gp/aw/ya"
    url = "https://www.amazon.com/gp/aw/ya?ac=od&ref=ppx_pop_mob_b_order_details&oid={}".format(oid)
    # params = {
    #     "ac": "od",
    #     "ref": "ppx_pop_mob_b_order_details",
    #     "oid": oid
    # }
    cookie = 'ubid-main=132-8193239-7735707; at-main=Atza|IwEBIJKrSrhkr0mEg0F9xl3k6CLUyze8mz0JaKmhQn8DRn5N4UyzyHmycAASCs0WOu2QwDtXjPP9J1Cccr4ppc4Ag5l65vrTWvX4MdmTqQ1KPwE5dhBTvh2G8ZHGmmm5gJkg933n_HwqAd45-FPJpwGrUSjcmKatuJocPiC3MXlFihF2QqCfdVB_vdMbs5uzmDvhPMF27RRmcqJt7p2-dAj5XE9uffrxq3HGVIqmIHRp0pbMcg; x-main="e4e28e9CSrPaTOXzWuU1WychwyEiRHproGQxeiugVNti?LjoYhYnF8MzZHYctJ0B"; sess-at-main="Zr8Xm0+lru4q3wkDjkiZmj1z+Ry18mIUpYm+tg2pJV8="'

    # cookie = 'ubid-main=132-8193239-7735707; at-main=Atza|IwEBIJKrSrhkr0mEg0F9xl3k6CLUyze8mz0JaKmhQn8DRn5N4UyzyHmycAASCs0WOu2QwDtXjPP9J1Cccr4ppc4Ag5l65vrTWvX4MdmTqQ1KPwE5dhBTvh2G8ZHGmmm5gJkg933n_HwqAd45-FPJpwGrUSjcmKatuJocPiC3MXlFihF2QqCfdVB_vdMbs5uzmDvhPMF27RRmcqJt7p2-dAj5XE9uffrxq3HGVIqmIHRp0pbMcg; sess-at-main="Zr8Xm0+lru4q3wkDjkiZmj1z+Ry18mIUpYm+tg2pJV8="; sst-main=Sst1|PQGSH2YnGD-xyE3TReRuXXz7CdF_SKT8EXRrjT2CJW8a9Ajp6HIQ_Xre2fKwBJtGD_CL6w7cCSSykG66BPCvNGrWLtltjmsxx4izDlp-mDP7oN-l54b0bEf3VNfkKws4Dbnkkxcnx6LSZX4BVIqMyEvS2TDBU2SJNgElsPoDdVZjNz_uSKAhv1hCij1LxQz8Wg1f6tXKYVa9nVTkKOu43LbVa3LFQnDZuc3nNVxLB0_zgx4a7mLv-3ODeB7fxq0vfSGbvSDCrEhIZvftmwlE1Hn37W1KGT_VWJq3Diti8DSMVrI; session-id-time=2082787201l; session-token=4rJlFeSFlB/gky2h/PfTxB8PKjJh2HEM/nEzspItvRxcOz/7ihizba8AqxvTNKAQMt0+M5gm0ZNn4jAdwsGGZVQy0YBFNazvmeSuqcbOlvsGxEMYanvwR9jjV4OcgFMFzLmbc3Ra3N0lciG0xbGUczGSemgbNgTccNIBumG51Kahl1aZVcHE1svss5CxvqlOwNGt9XdaA5eSEZLLprWcfF2uKpJJCtZPqzFUihlvYHQJc0s6VWzRyX663ow+ZnLvaVZugWzwQarAFmrAi3BptZWRVxZd7OGmxeNObqu9x6WfPU+ZL1/IWv11jIe2kfVgX+TOr3wrWYeEyJBWbiYQwppVICnT4+R6ZNWAjtxcSn/uZpVHnW9+nAMCIh9uV+uY; x-main="e4e28e9CSrPaTOXzWuU1WychwyEiRHproGQxeiugVNti?LjoYhYnF8MzZHYctJ0B"; csm-hit=FJ2SB9EVWGQ96M182PA1+s-14FZVZ9BSASXWV5AZW7F|1741024496555'
    # Define headers based on the provided request information
    headers = {
        "authority": "www.amazon.com",
        "method": "GET",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cookie": cookie_price,
        #"cookie": "i18n-prefs=USD; x-amz-captcha-1=1730582410553894; x-amz-captcha-2=TYuB1uSmiBmpLooxNYGyAg==; ubid-main=132-8193239-7735707; lc-main=en_US; s_nr=1736718953661-New; s_vnum=2168718953662&vn=1; s_dslv=1736718953662; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiMzlkMTE2Iiwia2V5IjoiQ1d4bFdBRW5QNE9qY3N6Rk5ucytUVDdnMktlM3RpaUFlSVFsVmRmU21vUi91bmhwWjdtQTVnc3NBOGExSGtoQUtybkdkL1F6NEhSTHIyUnYxamZNQWJZcDJYaUVCV0pGcEFhZEs5U2RtOEUxeVR0djcvUFJISjFHTnBuRHpxNFRKRFRZMjdmdkRmWUs4cjByWlRvRktzd1JEM0FDWHNIZzR1TWZZeno3MmM0dU41QjZRc3NlMTFrOGdUMk9kSkw3NUdyVTI4VC80MmxTU05CeUxwVzE5TVBrT2h3eE5ZWGRPNXJhWnhraC82VkpUcTgvZkdlVGJjZmRaeDZNcWI2U2JnV1hmWWVnQTVVK1FIdlE1Z1k3OGhsdmlvTzk2VWRKZnJ5dS9iMEkrK2ZzVzdTTnA1ZGxYdnBtSE1MSkJyN2RRajdpOHJ1Q1Y3dWZ2eEJIMHVSYk1BPT0ifQ==; skin=noskin; session-id=137-1415228-6188013; JSESSIONID=B5CA31A65363397BF7EE20A06B6C3BD5; at-main=Atza|IwEBIJKrSrhkr0mEg0F9xl3k6CLUyze8mz0JaKmhQn8DRn5N4UyzyHmycAASCs0WOu2QwDtXjPP9J1Cccr4ppc4Ag5l65vrTWvX4MdmTqQ1KPwE5dhBTvh2G8ZHGmmm5gJkg933n_HwqAd45-FPJpwGrUSjcmKatuJocPiC3MXlFihF2QqCfdVB_vdMbs5uzmDvhPMF27RRmcqJt7p2-dAj5XE9uffrxq3HGVIqmIHRp0pbMcg; sess-at-main=\"Zr8Xm0+lru4q3wkDjkiZmj1z+Ry18mIUpYm+tg2pJV8=\"; sst-main=Sst1|PQGSH2YnGD-xyE3TReRuXXz7CdF_SKT8EXRrjT2CJW8a9Ajp6HIQ_Xre2fKwBJtGD_CL6w7cCSSykG66BPCvNGrWLtltjmsxx4izDlp-mDP7oN-l54b0bEf3VNfkKws4Dbnkkxcnx6LSZX4BVIqMyEvS2TDBU2SJNgElsPoDdVZjNz_uSKAhv1hCij1LxQz8Wg1f6tXKYVa9nVTkKOu43LbVa3LFQnDZuc3nNVxLB0_zgx4a7mLv-3ODeB7fxq0vfSGbvSDCrEhIZvftmwlE1Hn37W1KGT_VWJq3Diti8DSMVrI; session-id-time=2082787201l; session-token=oOeRidIzcFDDIZN5AAVN/BB9opZ9TSvSzCMj2A9Qsy/ER4bE5g2nbKwrf0z67UfpGYJP/gTL+FVoz+4gZkCbaSphDmaBpMY2zO+1/LjzLxxrstgM5jjyQjkLyQPyZEm+iEne3F0sSAnZWNxKbu0eynURCHqFkLAiNKga6nAXaucJOI5FsIjf60cheC70JQjOaS8wNH6jr9wjJFHEE2HQDdMvSxjqlfeRbISqcCX5QJeKOMPZhDQJg4iDcgyC/larh0UX3XfR4oFT998M5rCXgKBG4ealcJ1ZEQBvN/Y+y4lWn2qc9VBuq2onh78zvYSxd4rQBadpJ4JEtlABEHar+iyn7aAFW5P6UX3q0BnwEc/1xZY9eDaBlt1kguwf91oS; x-main=\"q6sLk6ZrUIftC2KrHLWlCr7LwrNEhCVtS3OxpI@0i8t7I2FeJrl8QMEs?Z5UJT6B\"; csm-hit=FJ2SB9EVWGQ96M182PA1+s-AHRPCG69XMEEQGC62N5X|1740929325511",
        "device-memory": "8",
        "downlink": "1.8",
        "dpr": "1",
        "ect": "4g",
        "priority": "u=0, i",
        "referer": f"https://www.amazon.com/your-orders/pop?ref=ppx_yo2ov_mob_b_pop&orderId={oid}&lineItemId=jilkqvqskitrtops&shipmentId=BxVC54Mhs&packageId=1&asin=B0CZ8YWLM4",
        "rtt": "50",
        "sec-ch-device-memory": "8",
        "sec-ch-dpr": "1",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-viewport-width": "769",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
        "viewport-width": "769"
    }
    
    response = requests.get(url, headers=headers)
    price = parseprice(response.text)
    return price


ordertest = True
orderindex = 0
while ordertest:
    r = makerequest(orderindex)
    ordertest = test_moreorders(r)
    orderindex += 10
    parsedata(r)
