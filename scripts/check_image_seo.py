import os
from bs4 import BeautifulSoup


def check_image_seo(directory):
    print(f"🔍 Checking SEO for images in: {directory}\n")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    imgs = soup.find_all('img')
                    for img in imgs:
                        src = img.get('src', 'Unknown')
                        alt = img.get('alt')

                        # بررسی وجود Alt
                        if not alt:
                            print(f"❌ Missing Alt: {file} -> {src}")

                        # بررسی نام فایل (اگر نام فایل فقط عدد یا خیلی کوتاه باشد)
                        filename = src.split('/')[-1]
                        if len(filename) < 5 or filename.split('.')[0].isdigit():
                            print(f"⚠️ Bad Filename: {file} -> {src}")


if __name__ == "__main__":
    check_image_seo('templates')