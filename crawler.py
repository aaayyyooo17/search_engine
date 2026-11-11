import json
import re
import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.math.kit.edu"
MAX_DEPTH = 3      
TIMEOUT = 5            
DELAY = 0.2            


NON_HTML_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".rar", ".mp4", ".mp3", ".avi",
}


def is_internal(url: str, base_netloc: str):
    return urlparse(url).netloc.lower() in ("", base_netloc.lower())

def is_non_html(url: str):
    path = urlparse(url).path.lower()
    return any(path.endswith(extension) for extension in NON_HTML_EXTENSIONS)

# def normalize(url: str):
#     url = url.split("#")[0]
#     parsed = urlparse(url)
#     url = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower()).geturl()
#     if url.endswith("/"):
#         url = url[:-1]
#     return url 

def normalize(url: str):
    url = url.split("#")[0]
    parsed = urlparse(url)
    path = re.sub(r"/index\.(html?|php)$", "", parsed.path, flags=re.IGNORECASE)
    key = parsed.netloc.lower() + path.rstrip("/")
    if parsed.query:
        key += "?" + parsed.query
    return key

def fetch(url: str):
    try:
        resp = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return None, None
    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code != 200 or "text/html" not in content_type:
        return None, None
    return resp.url, resp.text

def extract_title(soup):
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""
    


def extract_links(soup, page_url):
    links = set()
    for a in soup.find_all("a", href = True):
        href = a["href"].strip()
        if href.lower().startswith(("mailto:", "javascript:", "tel:")):
            continue
        absolute = urljoin(page_url, href)
        if normalize(absolute) == normalize(page_url):
            continue
        if is_non_html(absolute):
            continue
        links.add(absolute)
    return links

def extract_text(soup):
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()

def renumber(pages, titles, links, texts):
    old_ids = sorted(pages)
    new_id = {old: new for new, old in enumerate(old_ids, start=1)}   # old id -> new id

    pages  = {new_id[i]: pages[i]  for i in old_ids}
    titles = {new_id[i]: titles[i] for i in old_ids}
    texts  = {new_id[i]: texts[i]  for i in old_ids}
    links  = {new_id[i]: sorted(new_id[t] for t in links[i]) for i in old_ids}
    return pages, titles, links, texts

def crawl(start_url: str, max_depth: int):
    queue = deque([(start_url, 0)])
    queued_urls = {normalize(start_url)}
    base_loc = None
    pages = {}
    texts = {}
    titles = {}
    url_id = {}
    next_id = 1
    raw_links = {}
    while queue:
        url, depth = queue.popleft()
        real_url, html = fetch(url)
        time.sleep(DELAY)
        if html is None:
            continue
        if base_loc is None:
            base_loc = urlparse(real_url).netloc
        if not is_internal(real_url, base_loc):
            continue

        key = normalize(real_url)
        if key in url_id:
            url_id[normalize(url)] = url_id[key]
            continue

        page_id = next_id
        next_id += 1
        url_id[key] = page_id
        url_id[normalize(url)] = page_id

        soup = BeautifulSoup(html, "html.parser")
        pages[page_id] = real_url
        titles[page_id] = extract_title(soup)
        found_links = extract_links(soup, real_url)
        texts[page_id] = extract_text(soup)
        
        internal_links = {link for link in found_links if is_internal(link, base_loc)}
        raw_links[page_id] = internal_links

        if depth < max_depth:
            for link in sorted(internal_links):
                link_key = normalize(link)
                if link_key not in queued_urls:
                    queued_urls.add(link_key)
                    queue.append((link, depth+1))

        print(f"[{page_id}] depth={depth} {real_url}")


    links_final = {}
    for page_id, urls in raw_links.items():
        ids = set()
        for link in urls:
            key = normalize(link)
            if key in url_id and url_id[key] != page_id:
                ids.add(url_id[key])
        links_final[page_id] = sorted(ids)

    pages, titles, links, texts = clean_graph(pages, titles, links_final, texts)
    return renumber(pages, titles, links, texts)


def clean_graph(pages, titles, links, texts):
    changed = True
    while changed:
        changed = False
        valid_ids = set(pages.keys())

        for pid in links:
            filtered = [t for t in links[pid] if t in valid_ids]
            if filtered != links[pid]:
                links[pid] = filtered

        empty_ids = [pid for pid, ids in links.items() if len(ids) == 0]
        for pid in empty_ids:
            del pages[pid]
            del links[pid]
            del texts[pid]
            del titles[pid]
            changed = True

    return pages, titles, links, texts


def save(pages: dict, titles: dict, links_out: dict, texts: dict):
    with open("pages.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in pages.items()}, f, ensure_ascii=False, indent=2)
    with open("links.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in links_out.items()}, f, indent=2)
    with open("texts.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in texts.items()}, f, ensure_ascii=False, indent=2)
    with open("titles.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in titles.items()}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    pages, titles, links_out, texts = crawl(BASE_URL, max_depth=MAX_DEPTH)
    save(pages, titles, links_out, texts)
    print(f"\nDone. Crawled {len(pages)} pages")
                



















