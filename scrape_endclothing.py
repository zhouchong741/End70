import requests
from bs4 import BeautifulSoup
import re
import json
import time
import math
import os

BASE_URL = "https://www.endclothing.com/cn/sale"
OUTPUT_FILE = "endclothing_70off.json"
DATA_JS_FILE = "data.js"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def load_existing_data():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert list to dict keyed by url for easy lookup
                return {item['url']: item for item in data}
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return {}

def save_data(products_dict):
    # Save as JSON
    products_list = list(products_dict.values())
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)
    
    # Save as JS for HTML view
    json_str = json.dumps(products_list, ensure_ascii=False)
    with open(DATA_JS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"window.products = {json_str};")

def get_page_soup(page_num):
    url = f"{BASE_URL}?page={page_num}"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def get_total_pages(soup):
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
            
            # Extract Image
            img_tag = link.find('img')
            img_url = ""
            if img_tag:
                if img_tag.get('src'):
                    img_url = img_tag.get('src')
                elif img_tag.get('srcset'):
                    # srcset format: "url1 1w, url2 2w", take first one
                    img_url = img_tag.get('srcset').split(' ')[0]
            
            match = re.search(r'(.*)(CN¥[\d,]+)(CN¥[\d,]+)(70% off)$', content)
            if match:
                name = match.group(1).strip()
                original_price_str = match.group(2)
                sale_price_str = match.group(3)
                
                original_price = int(re.sub(r'[^\d]', '', original_price_str))
                discounted_price = int(re.sub(r'[^\d]', '', sale_price_str))
                
                products.append({
                    "name": name,
                    "original_price": original_price,
                    "discounted_price": discounted_price,
                    "discount": "70% off",
                    "url": full_url,
                    "image_url": img_url
                })
            else:
                # Fallback for cases where the regex doesn't match
                name_match = re.search(r'(.*)(CN¥)', content)
                name = name_match.group(1).strip() if name_match else content
                products.append({
                    "name": name,
                    "raw_content": content,
                    "url": full_url,
                    "discount": "70% off",
                    "image_url": img_url
                })
    return products

def main():
    print("Loading existing data...")
    all_products_dict = load_existing_data()
    print(f"Loaded {len(all_products_dict)} existing products.")
    
    current_run_urls = set()
    
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
    print(f"Found {len(products)} items on page 1.")
    
    for p in products:
        url = p['url']
        current_run_urls.add(url)
        all_products_dict[url] = p

    try:
        for page in range(2, total_pages + 1):
            soup = get_page_soup(page)
            if not soup:
                continue
            
            products = extract_products(soup)
            print(f"Found {len(products)} items on page {page}. Total unique items so far: {len(all_products_dict)}")
            
            for p in products:
                url = p['url']
                current_run_urls.add(url)
                all_products_dict[url] = p
            
            if len(products) > 0 or page % 5 == 0:
                save_data(all_products_dict)
                print(f"Progress saved.")

            time.sleep(1)

        # If loop completes, prune old data
        print("Scraping complete. Cleaning up old data...")
        keys_to_remove = [url for url in all_products_dict if url not in current_run_urls]
        for url in keys_to_remove:
            del all_products_dict[url]
        
        print(f"Removed {len(keys_to_remove)} old items. Final count: {len(all_products_dict)}")
        save_data(all_products_dict)
        print(f"Final save to {OUTPUT_FILE} and {DATA_JS_FILE}")

    except KeyboardInterrupt:
        print("Scraping interrupted by user. Saving current progress...")
        save_data(all_products_dict)
    except Exception as e:
        print(f"An error occurred: {e}. Saving current progress...")
        save_data(all_products_dict)

if __name__ == "__main__":
    main()
