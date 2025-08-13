import os
import socket
import ipaddress
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

AFFILIATE_APP_KEY = os.getenv("AFFILIATE_APP_KEY")
ENDPOINT = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.listHotProducts"
HEADERS = {"User-Agent": "Mozilla/5.0 (AdFactoryBot)"}
TIMEOUT = 20


def _resolve_ips(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None)
        ips = []
        for info in infos:
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
        return ips
    except Exception:
        return []


def is_public_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname or ""
        if not host:
            return False
        ips = _resolve_ips(host)
        if not ips:
            return False
        for ip in ips:
            addr = ipaddress.ip_address(ip)
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast:
                return False
        return True
    except Exception:
        return False


def _safe_http_get(url: str, headers: dict, timeout: int, max_redirects: int = 3) -> requests.Response:
    current_url = url
    for _ in range(max_redirects + 1):
        if not is_public_url(current_url):
            raise ValueError("Blocked non-public URL")
        r = requests.get(current_url, headers=headers, timeout=timeout, allow_redirects=False)
        if r.is_redirect or r.status_code in (301, 302, 303, 307, 308):
            loc = r.headers.get("Location")
            if not loc:
                break
            current_url = urljoin(current_url, loc)
            continue
        return r
    return r


def scrape_product(url: str) -> dict:
    r = _safe_http_get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.select_one("h1.product-title-text") or soup.select_one("title")
    title = title_tag.text.strip() if title_tag else url

    def extract_img_src(img):
        # Try src, data-src, srcset
        src = img.get("src") or img.get("data-src")
        if not src:
            srcset = img.get("srcset")
            if srcset:
                # take first candidate
                src = srcset.split(",")[0].split()[0]
        if not src:
            return None
        # Make absolute
        return urljoin(url, src)

    raw_images = [extract_img_src(img) for img in soup.select("img")]
    images = [u for u in raw_images if u and u.startswith("http") and is_public_url(u)]
    # De-duplicate preserving order and keep only first 10
    images = list(dict.fromkeys(images))[:10]

    return {"url": url, "title": title, "images": images}


def get_top_trends() -> list[dict]:
    if AFFILIATE_APP_KEY:
        params = {
            "appKey": AFFILIATE_APP_KEY,
            "fields": "productId,productTitle,imageUrl,productUrl,orderCount,averageStar",
        }
        resp = requests.get(ENDPOINT, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("result", {}).get("products", [])
        trends = []
        for p in products:
            orders = p.get("orderCount", 0)
            rating = p.get("averageStar", 0.0)
            if orders > 1000 and rating >= 4.7:
                trends.append(
                    {
                        "name": p.get("productTitle"),
                        "orders": orders,
                        "rating": rating,
                        "url": p.get("productUrl"),
                        "image": p.get("imageUrl"),
                    }
                )
        return trends[:10]
    return []