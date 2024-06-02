import os

os.system('python manage.py migrate --database=default')
os.system('python manage.py migrate --database=q')
