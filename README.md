## Scripts

###STUDIO APP

###**`1_create_item.py`**

excel.ITEMS.ITEMID == 666666<br>
django.ITEM.ITEMID oxi 666666

>RUN SCRIPT

django.ITEM.ITEMID = 666666<br>
django.ITEM.NAME = EXCEL.ITEMS.NAME<br>
django.ITEM.FIELD = EXCEL.ITEMS.FIELD<br>

###**`2_item_image.py`**

Write images to Item instances from media/items-temp folder and move them to media/items folder.

###**`3_item_tags.py`**

django.ITEM.ITEMID == 666666<br>
excel.ITEMSTAGS 666666 | shirt blue stripes

>RUN SCRIPT

django.ITEM.TAGS ++ shirt blue stripes

###**`delete_double_tags.py`**

django.ITEM.TAGS == top top blue

>RUN SCRIPT

django.ITEM.TAGS == top blue

###**`update_shopify_sizes.py`**

UPDATE ITEM SIZES BASED ON SHOPIFY AVAILABILITY

<br><br><br>
## Prerequisites
- Python version >= 3.8.2
- Install the dependencies with `pip install -r requirements/main.txt`

## Running the app
First apply the database migrations.
```
python manage.py migrate
```

Then start the development server.
```
python manage.py runserver
```

```
python manage.py 
```
New items from excel to models ```
python manage.py new_item
```
