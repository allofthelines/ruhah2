# den doulevei idk giati

from celery import shared_task


@shared_task(name='accounts.tasks.test_task')
def test_task():
    print("Test task executed")

@shared_task
def clear_user_item_cart():
    from .models import UserItemCart
    UserItemCart.objects.all().delete()

print("Loading tasks from accounts...")
