import os
import re


def fix_translations(directory):
    # الگوی جستجو برای پیدا کردن _("text") یا _('text')
    pattern = re.compile(r'_\(["\'](.*?)["\']\)')

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # جایگزینی الگو با {% trans "text" %}
                new_content = pattern.sub(r'{% trans "\1" %}', content)

                if content != new_content:
                    # اضافه کردن {% load i18n %} به ابتدای فایل اگر وجود نداشته باشد
                    if '{% load i18n %}' not in new_content:
                        new_content = '{% load i18n %}\n' + new_content

                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Fixed: {path}")


if __name__ == "__main__":
    # نام پوشه تمپلیت‌های خود را اینجا چک کن
    fix_translations('templates')