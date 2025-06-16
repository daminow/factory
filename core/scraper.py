import os
import requests
from bs4 import BeautifulSoup

AFFILIATE_APP_KEY = os.getenv("AFFILIATE_APP_KEY")
ENDPOINT = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.listHotProducts"


def scrape_product(url: str) -> dict:
    """
    Scrape product page for title and image URLs.
    """
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tag = soup.select_one('h1.product-title-text') or soup.select_one('title')
    title = title_tag.text.strip() if title_tag else url
    images = [img['src'] for img in soup.select('img') if img.get('src') and img['src'].startswith('http')]
    return {'url': url, 'title': title, 'images': images}


def get_top_trends() -> list[dict]:
    """
    Fetch top trending products via AliExpress Affiliate API or fallback scraping.
    Returns list of dicts with keys: name, orders, rating, url, image.
    """
    # Try Affiliate API first
    if AFFILIATE_APP_KEY:
        params = {
            "appKey": AFFILIATE_APP_KEY,
            "fields": "productId,productTitle,imageUrl,productUrl,orderCount,averageStar"
        }
        resp = requests.get(ENDPOINT, params=params)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("result", {}).get("products", [])
        trends = []
        for p in products:
            orders = p.get("orderCount", 0)
            rating = p.get("averageStar", 0.0)
            if orders > 1000 and rating >= 4.7:
                trends.append({
                    "name": p.get("productTitle"),
                    "orders": orders,
                    "rating": rating,
                    "url": p.get("productUrl"),
                    "image": p.get("imageUrl"),
                })
        return trends[:10]
    # Fallback: simple scraping of AliExpress hot products page
    fallback_url = "https://www.aliexpress.com/glosearch/hot-products"
    resp = requests.get(fallback_url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = soup.select('div.hot-product-card')[:10]
    trends = []
    for it in items:
        name_el = it.select_one('a.item-title')
        name = name_el.text.strip() if name_el else ''
        orders_el = it.select_one('span.order-count')
        orders = int(''.join(filter(str.isdigit, orders_el.text))) if orders_el else 0
        rating_el = it.select_one('span.star-rating')
        rating = float(rating_el.text.strip()) if rating_el else 0.0
        link = name_el['href'] if name_el and name_el.get('href') else ''
        img_el = it.select_one('img')
        image = img_el['src'] if img_el and img_el.get('src') else ''
        trends.append({"name": name, "orders": orders, "rating": rating, "url": link, "image": image})
    return trends
```python
import requests
from bs4 import BeautifulSoup

def scrape_product(url: str) -> dict:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.select_one('title').text
    images = [img['src'] for img in soup.select('img') if img.get('src')]
    return {'url': url, 'title': title, 'images': images}

def get_top_trends() -> list[dict]:
    # placeholder: fetch from AliExpress API
    return [
        {'name': f'Product {i+1}', 'orders': 1000+i*100, 'rating': 4.8}
        for i in range(10)
    ]