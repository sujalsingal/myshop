import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from pathlib import Path

# Prepare output folder
img_folder = Path("media/products")
img_folder.mkdir(parents=True, exist_ok=True)

# Zepto URL and headers
url = "https://www.zeptonow.com/cn/dairy-bread-eggs/dairy-bread-eggs/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/f594b28a-4775-48ac-8840-b9030229ff87"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    exit()

soup = BeautifulSoup(response.text, 'lxml')
product_divs = soup.find_all('a', class_="relative z-0 my-3 rounded-t-xl rounded-b-md group")

with open('products_local.txt', 'w', encoding='utf-8') as f:
    if not product_divs:
        f.write("⚠️ No products found. Page might be JS-rendered.\n")
    else:
        for product in product_divs:
            name_tag = product.find("h5", class_="text-xl font-[500] leading-6 tracking-normal text-[#2E3642] line-clamp-2")
            price_tag = product.find("p", class_="text-[20px] font-[700] leading-7 tracking-[-0.2px] text-[#262A33]")
            qty_tag = product.find("p", class_="text-base font-[450] leading-5 tracking-normal text-[#5A6477]")
            img_tag = product.find("img")

            name = name_tag.text.strip() if name_tag else "N/A"
            price = price_tag.text.strip() if price_tag else "N/A"
            quantity = qty_tag.text.strip() if qty_tag else "N/A"

            # Handle image
            img_url = img_tag['src'] if img_tag else None
            local_img_path = "N/A"
            if img_url:
                try:
                    img_data = requests.get(img_url, stream=True, timeout=10)
                    img_data.raise_for_status()
                    # Create a clean filename
                    ext = os.path.splitext(urlparse(img_url).path)[-1]
                    filename = f"{name.replace(' ', '_').replace('/', '_')}{ext}"
                    full_path = img_folder / filename

                    with open(full_path, 'wb') as img_file:
                        img_file.write(img_data.content)
                    local_img_path = f"products/{filename}"
                except Exception as e:
                    print(f"⚠️ Failed to download {img_url}: {e}")

            # Save product info to file
            f.write(f"Name: {name}\n")
            f.write(f"Price: {price}\n")
            f.write(f"Quantity: {quantity}\n")
            f.write(f"Image Path: {local_img_path}\n")
            f.write("-" * 50 + "\n")

print("✅ Product data with local images saved.")
