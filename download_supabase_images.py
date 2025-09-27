# download_supabase_images.py
import csv
import os
import requests
from urllib.parse import urlparse
from pathlib import Path

# ✅ CONFIG — customize these
CSV_FILE = "Supabase Snippet E-commerce Database Schema.csv"      # Your exported CSV filename
IMAGE_DIR = "downloaded_images"         # Folder to save images
PLACEHOLDER = "placeholder.jpg"         # Fallback image (create one)

# Create image directory
Path(IMAGE_DIR).mkdir(exist_ok=True)

def download_image(product_photo, product_id, product_name):
    if not product_photo or not product_photo.startswith('http'):
        return None

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyShopBot/1.0)'}
        response = requests.get(product_photo, timeout=10, headers=headers)

        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
            # Get extension
            parsed = urlparse(product_photo)
            ext = os.path.splitext(parsed.path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                ext = '.jpg'

            # Clean filename
            safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in product_name[:30])
            filename = f"{product_id}_{safe_name}{ext}"
            filepath = os.path.join(IMAGE_DIR, filename)

            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
            return filename

        else:
            print(f"⚠️  Invalid image: {product_photo} (HTTP {response.status_code})")
            return None

    except Exception as e:
        print(f"❌ Error downloading {product_photo}: {str(e)}")
        return None

# Read CSV and download
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product_id = row['id']
        product_name = row['product_name']
        product_photo = row['product_photo']  # ← Make sure your CSV has this column name!

        local_filename = download_image(product_photo, product_id, product_name)

        # Print mapping for later use
        if local_filename:
            print(f"MAPPING: {product_id} → {local_filename}")
        else:
            print(f"MAPPING: {product_id} → {PLACEHOLDER}")