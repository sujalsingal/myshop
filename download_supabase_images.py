py
   import csv
   import os
   import requests
   from urllib.parse import urlparse
   from pathlib import Path

   CSV_FILE = "supabase_products.csv"
   IMAGE_DIR = "downloaded_images"
   Path(IMAGE_DIR).mkdir(exist_ok=True)

   def download_image(image_url, product_id, product_name):
       if not image_url or not image_url.startswith('http'):
           return None
       try:
           response = requests.get(image_url, timeout=10)
           if response.status_code == 200:
               ext = os.path.splitext(urlparse(image_url).path)[1].lower()
               if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                   ext = '.jpg'
               safe_name = "".join(c if c.isalnum() else "_" for c in product_name[:30])
               filename = f"{product_id}_{safe_name}{ext}"
               filepath = os.path.join(IMAGE_DIR, filename)
               with open(filepath, 'wb') as f:
                   f.write(response.content)
               print(f"✅ {filename}")
               return filename
       except Exception as e:
           print(f"❌ {image_url}: {e}")
       return None

   with open(CSV_FILE, 'r', encoding='utf-8') as f:
       reader = csv.DictReader(f)
       for row in reader:
           download_image(row['product_photo'], row['id'], row['product_name'])
   ```