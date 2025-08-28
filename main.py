from bs4 import BeautifulSoup
import requests

# Target Zepto search URL for vegetables
url = "https://www.bigbasket.com/pc/fruits-vegetables/fresh-vegetables/?nc=ct-fa"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

try:
    # Send request
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    exit()

# Parse the HTML
soup = BeautifulSoup(response.text, 'lxml')
# Try to locate product containers (adjust if needed)

product_divs = soup.find_all('div')

# Save only meaningful data to file
with open('data.txt', 'w', encoding='utf-8') as f:
    if not product_divs:
        f.write("⚠️ No products found. Consider using Selenium for JS-rendered content.\n")
    else:
        for product in product_divs:
            name = product.find("div",class_= "tw-text-300 tw-font-semibold tw-line-clamp-2")
            price = product.find("div", class_="tw-text-200 tw-font-semibold")
            quantity = product.find("div", class_="tw-text-200 tw-font-medium tw-line-clamp-1")
            image = product.find("img")
            image_url = image['src'] if image else "N/A"
            f.write(f"Name: {name.text.strip() if name else 'N/A'}\n")
            f.write(f"Price: {price.text.strip() if price else 'N/A'}\n")
            f.write(f"Quantity: {quantity.text.strip() if quantity else 'N/A'}\n")
            f.write(f"Image URL: {image_url}\n")
            f.write("-" * 50 + "\n")

    print("✅ Done. Product data saved in zepto_cleaned_data.txt")
