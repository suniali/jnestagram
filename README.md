# Jnestagram
A web app for posting images, like instagram.


#### Packages

cryptography                       46.0.5<br>
dj-database-url                    3.1.0<br>
Django                             6.0.2<br>
django-admin-honeypot-updated-2021 1.2.0<br>
django-cleanup                     9.0.0<br>
django-environ                     0.12.0<br>
django-htmx                        1.27.0<br>
django-resized                     1.0.3<br>
django-storages                    1.14.6<br>
boto3                              1.42.46<br>
gunicorn                           25.0.3<br>
pillow                             12.1.1<br>
psycopg2-binary                    2.9.11<br>
requests                           2.32.5<br>
whitenoise                         6.11.0<br>

<br><br>

## < Installation >

### Set Up
1. Create folder and open up with your preferred IDE (eg. VS Code)
2. Download Github Desktop and sign in with your Github account
3. Clone repository using Github Desktop (choose the correct path to your folder)
4. Duplicate staticfiles folder and rename it "static"
5. Get the .env file and save it into the a_core folder

### Terminal / Command Line
1. Install Python (python.org, check if installed: python --version)
2. Activate Virtual Environment (eg. venv)
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver
  
  
---

    
## < How to add a feature >

1. Create feature branch: feature_nameofthefeature_yourname (change "nameoffeature" and "yourname")
2. Add new feature to the Features table in the admin interface
3. In the .env file change DEVELOPER=Yourname (change "Yourname") 
4. Add feature toggle: 
#### # views.py
```python
from a_features.views import feature_enabled

try: 
    feature_herobutton = feature_enabled(1, 'Yourname')
except:
    feature_herobutton = False
```
5. Change "1" with the id of the feature and "Yourname"
  
---
  
## < Unocss Installation with Node >

This installation is only required if you make css changes on the site.

### Unocss Set Up 

1. Download node (nodejs.org, check if installed: node --version)
2. mkdir node && cd node
3. npm init -y && npm add -D unocss @unocss/cli
#### # Create a uno.config.ts (or .js) file in your root directory to define how UnoCSS extracts classes from your Django templates:
```
import { 
  defineConfig,
  presetUno,
  presetAttributify,
  presetIcons } from 'unocss'

export default defineConfig({
  content: {
    filesystem: [
      'templates/*.html',
      'templates/**/*.html',
      'templates/**/**/*.html', // Scans all HTML files
      '**/*.py',   // Scans Python files for class names
    ],
  },
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      extraProperties: {
        'display': 'inline-block',
        'vertical-align': 'middle',
      },
    }),
  ],
})
```
#### # package.json : scripts to run unocss for developer or production
```
"scripts": {
    "dev": "unocss \"templates/**/*.html\" -o static/css/uno.css --watch",
    "build": "unocss \"templates/**/*.html\" -o static/css/uno.css --minify"
  },
```

### Unocss Commands 

#### Development
1. npm run dev
2. ctrl+c

#### Deployment
1. npm run build
2. python manage.py collectstatic