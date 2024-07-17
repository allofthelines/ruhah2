"""

NEW IMAGE UPLOAD PIPELINE se S3 KAI POSTGRES (BULK)

1. raw fwtografies se /media/items-temp

2. REMOVE BACKGROUND
3. python manage.py crop_png
4. python manage.py square_png

5. manually rename 1.png 2.png
6. manually update /studio/static/studio/new_items.json

7. python manage.py rename_items_before_upload
8. python manage.py upload_items_s3
9. heroku run python manage.py upload_items_json


"""