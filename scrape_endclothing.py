import requests
from bs4 import BeautifulSoup
import re
import json
import time
import math

BASE_URL = "https://www.endclothing.com/cn/sale"
OUTPUT_FILE = "endclothing_70off.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_page_soup(page_num):
    url = f"{BASE_URL}?page={page_num}"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def get_total_pages(soup):
    """
    获取总页数
    """
    try:
        plp_body = soup.find(id='plpBody')
        if plp_body:
            first_div = plp_body.find('div')
            if first_div:
                divs = first_div.find_all('div', recursive=False)
                if len(divs) >= 2:
                    second_div = divs[1]
                    span = second_div.find('span')
                    if span:
                        count_text = span.get_text(strip=True)
                        count_match = re.search(r'(\d+)', count_text)
                        if count_match:
                            total_count = int(count_match.group(1))
                            print(f"产品总数: {total_count}")
                            
                            product_links = soup.find_all('a', href=re.compile(r'/cn/.*\.html'))
                            unique_links = set(l['href'] for l in product_links if l.get('href'))
                            items_on_page = len(unique_links)
                            
                            if items_on_page == 0:
                                items_on_page = 120
                            
                            print(f"每页商品数: {items_on_page}")
                            
                            total_pages = math.ceil(total_count / items_on_page)
                            print(f"总页数: {total_pages}")
                            return total_pages
    except Exception as e:
        print(f"获取总页数时出错: {e}")
    
    return None

def extract_products(soup):
    """提取所有 70% off 的产品信息"""
    products = []
    discount_spans = soup.find_all(string=re.compile(r'70% off'))
    
    if not discount_spans:
        return []

    for text_node in discount_spans:
        parent = text_node.parent
        while parent and parent.name != 'a':
            parent = parent.parent
        
        if parent and parent.name == 'a':
            link = parent
            href = link.get('href')
            
            full_url = f"https://www.endclothing.com{href}" if href.startswith('/') else href
            content = link.get_text(strip=True)
            
            match = re.search(r'(.*)(CN¥[\\d,]+)(CN¥[\\d,]+)(70% off)$', content)
            if match:
                products.append({
                    "name": match.group(1).strip(),
                    "original_price": match.group(2),
                    "sale_price": match.group(3),
                    "discount": match.group(4),
                    "url": full_url
                })
            else:
                products.append({
                    "raw_content": content,
                    "url": full_url,
                    "discount": "70% off"
                })
    return products

def main():
    print(f"清空输出文件: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    all_70_off_products = []
    
    soup = get_page_soup(1)
    if not soup:
        print("Failed to load first page. Exiting.")
        return

    total_pages = get_total_pages(soup)
    if not total_pages:
        print("Could not determine total pages automatically. Defaulting to 100.")
        total_pages = 100

    print("Processing page 1...")
    products = extract_products(soup)
    all_70_off_products.extend(products)
    print(f"Found {len(products)} items on page 1.")

    try:
        for page in range(2, total_pages + 1):
            soup = get_page_soup(page)
            if not soup:
                continue
            
            products = extract_products(soup)
            all_70_off_products.extend(products)
            print(f"Found {len(products)} items on page {page}. Total: {len(all_70_off_products)}")
            
            if len(products) > 0 or page % 5 == 0:
                unique_products = {p['url']: p for p in all_70_off_products}.values()
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(list(unique_products), f, ensure_ascii=False, indent=2)
                print(f"Progress saved to {OUTPUT_FILE}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Scraping interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        unique_products = {p['url']: p for p in all_70_off_products}.values()
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(unique_products), f, ensure_ascii=False, indent=2)
        print(f"Final save to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
