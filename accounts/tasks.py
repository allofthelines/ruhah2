from celery import shared_task

@shared_task
def clear_user_item_cart():
    from .models import UserItemCart
    UserItemCart.objects.all().delete()

@shared_task
def test_task():
    print("Test task executed")