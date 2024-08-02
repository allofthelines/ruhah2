from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from box.models import Ticket
from core.models import Outfit
from accounts.models import CustomUser
from accounts.models import UserItemLikes
from .models import StudioOutfitTemp, Item, SizeCategory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .management.commands.image_processing import create_composite_image
from studio.models import CustomUser
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


import time
from django.core.files import File






def studio_tickets(request):
    ticket_list = Ticket.objects.filter(status='open')
    paginator = Paginator(ticket_list, 20)  # Show 20 tickets per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    print('\n1 DEBUG 1 \n', list(ticket_list.order_by('-id')), '\nDEBUG\n')

    if request.user.is_authenticated:
        user_styles = set(request.user.studio_styles.values_list('id', flat=True))
        following_user_ids = list(request.user.following_list.values_list('id', flat=True)) # gia to palio kitrinisma eksw
        user_following_ids = list(request.user.following.values_list('user_to_id', flat=True))

        # Filter tickets based on...
        filtered_tickets = [ticket for ticket in page_obj if
                        #ticket.creator_id.id != request.user.id and # ...if its the same guy
                            ticket.has_submitted_outfits(request.user) and # ...logged-in user exei hdh kanei submit x (des models.py) outfits se afto
                            ticket.style1.id in user_styles] # ...user's studio_styles AFTO ISWS EINAI PROBLEM OTAN ALLAZOUN STYLES

        print('\n2 DEBUG 2\n', filtered_tickets, '\nDEBUG\n')

        # Additional filtering based on studio_visibility
        if request.user.studio_visibility == 'following':
            filtered_tickets = [ticket for ticket in filtered_tickets if
                                ticket.creator_id.id in user_following_ids]

    else:
        following_user_ids = []
        filtered_tickets = page_obj  # Show all tickets for guests

    # Create a new paginator for the filtered tickets
    paginator = Paginator(filtered_tickets, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'following_user_ids': following_user_ids,
    }
    return render(request, 'studio/studio_tickets.html', context)




"""@login_required
def studio_items(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    user = request.user

    # Clear any lingering error messages for authenticated users
    storage = messages.get_messages(request)
    storage.used = False  # Ensure the storage is marked as not used
    for message in list(storage):
        # Only keep messages that are not the guest-only message
        if str(message) == 'Only registered users can submit outfits.':
            message.message = ''  # Clear the message content
            storage.used = True  # Ensure the storage is marked as used to clear the message

    outfit_temp, created = StudioOutfitTemp.objects.get_or_create(ticket=ticket, user=user)

    # Prepare image URLs in a list or dictionary
    image_urls = [outfit_temp.get_image_url(i) for i in range(1, 5)]

    if 'reset' in request.GET:
        item_to_reset = request.GET['reset']
        setattr(outfit_temp, f'{item_to_reset}img', 'studiooutfittemps/default_img.jpg')
        setattr(outfit_temp, f'{item_to_reset}id', '')
        outfit_temp.save()
        return redirect('studio:studio_items', ticket_id=ticket_id)

    context = {
        'ticket': ticket,
        'outfit_temp': outfit_temp,
        'image_urls': image_urls
    }
    return render(request, 'studio/studio_items.html', context)
"""


@login_required
def studio_items(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    user = request.user
    outfit_temp, created = StudioOutfitTemp.objects.get_or_create(ticket=ticket, user=user)

    # Prepare image URLs in a list or dictionary
    image_urls = [outfit_temp.get_image_url(i) for i in range(1, 5)]

    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', 'all')
    items = Item.objects.none()  # Start with an empty QuerySet

    if 'search' in request.GET:
        items = Item.objects.all()

        if search_query:
            words = search_query.split()
            query = Q()
            for word in words:
                query &= Q(tags__icontains=word)
            items = items.filter(query)

        # edw filtrarei gia kathe kathgoria opote borw na kanw skip to epomeno
        if category and category != 'all':
            items = items.filter(cat=category)

        if ticket.asktype != 'outfit':
            # Filter items based on the ticket's sizes
            items = items.filter(
                Q(cat='top', sizes_xyz__name=ticket.size_top_xyz) |
                Q(cat='bottom', sizes_xyz__name=ticket.size_bottom_xyz) |
                Q(cat='footwear') & (
                    Q(sizes_shoe_eu__size=ticket.size_shoe_eu) | Q(sizes_shoe_uk__size=ticket.size_shoe_uk)
                ) |
                Q(cat='accessory') |
                Q(cat='dress')
            ).distinct()  # Adding distinct to avoid duplicates

        # Additional filter if ticket.catalogue is 'liked_only'
        if ticket.catalogue == 'liked_only':
            liked_item_ids = UserItemLikes.objects.filter(
                liker=ticket.creator_id
            ).values_list('item', flat=True)
            items = items.filter(id__in=liked_item_ids)

    return render(request, 'studio/studio_items.html', {
        'ticket': ticket,
        'outfit_temp': outfit_temp,
        'items': items,
        'image_urls': image_urls
    })




"""def studio_items_guest(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    search_query = request.GET.get('search_query', '')

    if search_query:
        query = Q()
        for term in search_query.split():
            query &= Q(tags__icontains=term)
        items = Item.objects.filter(query).distinct()[:20]  # Limit to first 20 search results
    else:
        items = Item.objects.all()[:20]  # Limit to first 20 items

    image_urls = []  # No pre-loaded images for guests

    if not request.user.is_authenticated:
        user = CustomUser(username='guest')
        messages.error(request, 'Only registered users can submit outfits.')
    else:
        user = request.user

    context = {
        'ticket': ticket,
        'items': items,
        'image_urls': image_urls,
        'user': user,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'studio/studio_items_guest.html', context)"""

def studio_items_guest(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', 'all')
    items = Item.objects.none()  # Start with an empty QuerySet

    if 'search' in request.GET:
        items = Item.objects.all()

    if search_query:
        query = Q()
        for term in search_query.split():
            query &= Q(tags__icontains=term)
        items = Item.objects.filter(query).distinct()

    # Apply category filter only if a specific category is selected
    if category and category != 'all':
        items = items.filter(cat=category)

    # Filter items based on the ticket's sizes
    items = items.filter(
        Q(cat='top') |
        Q(cat='bottom') |
        Q(cat='footwear') |
        Q(cat='accessory') |
        Q(cat='dress')
    ).distinct()  # Adding distinct to avoid duplicates

    # Limit to first 20 items
    items = items[:20]

    image_urls = []  # No pre-loaded images for guests

    if not request.user.is_authenticated:
        user = CustomUser(username='guest')
        messages.error(request, 'Only registered users can submit outfits.')
    else:
        user = request.user

    context = {
        'ticket': ticket,
        'items': items,
        'image_urls': image_urls,
        'user': user,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'studio/studio_items_guest.html', context)






def studio_items_reset(request, ticket_id, item_id):
    # Fetch the StudioOutfitTemp instance
    # edw to item_id = 1 2 3 4
    user = request.user
    ticket = Ticket.objects.get(pk=ticket_id)
    outfit_temp = StudioOutfitTemp.objects.get(ticket=ticket, user=user)

    # Reset the specific item image and id based on item_id
    setattr(outfit_temp, f'item{item_id}img', f'studiooutfittemps/default_img{item_id}.jpg')
    setattr(outfit_temp, f'item{item_id}id', '')
    outfit_temp.save()

    # Redirect back to the studio_items view
    return redirect('studio:studio_items', ticket_id=ticket_id)






from django.shortcuts import render
from .models import Item

"""@login_required
def item_search(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    user = request.user
    outfit_temp, created = StudioOutfitTemp.objects.get_or_create(ticket=ticket, user=user)

    # Prepare image URLs in a list or dictionary
    image_urls = [outfit_temp.get_image_url(i) for i in range(1, 5)]

    search_query = request.GET.get('search_query', '')
    items = Item.objects.all()
    if search_query:
        words = search_query.split()
        query = Q()
        for word in words:
            query &= Q(tags__icontains=word)
        items = items.filter(query)

    # Filter items based on the ticket's sizes
    items = items.filter(
        Q(cat='top', sizes_xyz__name=ticket.size_top_xyz) |
        Q(cat='bottom', sizes_xyz__name=ticket.size_bottom_xyz) |
        Q(cat='footwear') & (
                Q(sizes_shoe_eu__size=ticket.size_shoe_eu) | Q(sizes_shoe_uk__size=ticket.size_shoe_uk)
        ) |
        Q(cat='accessory')
    ).distinct()  # Adding distinct to avoid duplicates

    return render(request, 'studio/studio_items.html', {
        'ticket': ticket,
        'outfit_temp': outfit_temp,
        'items': items,
        'image_urls': image_urls
    })
"""

@login_required
def item_search(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    user = request.user
    outfit_temp, created = StudioOutfitTemp.objects.get_or_create(ticket=ticket, user=user)

    # Prepare image URLs in a list or dictionary
    image_urls = [outfit_temp.get_image_url(i) for i in range(1, 5)]

    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', 'all')
    items = Item.objects.none()  # Start with an empty QuerySet

    if 'search' in request.GET:
        items = Item.objects.all()

        if search_query:
            words = search_query.split()
            query = Q()
            for word in words:
                query &= Q(tags__icontains=word)
            items = items.filter(query)

        if category and category != 'all':
            items = items.filter(cat=category)

        # Filter items based on the ticket's sizes
        items = items.filter(
            Q(cat='top', sizes_xyz__name=ticket.size_top_xyz) |
            Q(cat='bottom', sizes_xyz__name=ticket.size_bottom_xyz) |
            Q(cat='footwear') & (
                Q(sizes_shoe_eu__size=ticket.size_shoe_eu) | Q(sizes_shoe_uk__size=ticket.size_shoe_uk)
            ) |
            Q(cat='accessory')
        ).distinct()  # Adding distinct to avoid duplicates

        # Additional filter if ticket.catalogue is 'liked_only'
        if ticket.catalogue == 'liked_only':
            liked_item_ids = UserItemLikes.objects.filter(
                liker=ticket.creator_id
            ).values_list('item', flat=True)
            items = items.filter(id__in=liked_item_ids)

    return render(request, 'studio/studio_items.html', {
        'ticket': ticket,
        'outfit_temp': outfit_temp,
        'items': items,
        'image_urls': image_urls
    })







@login_required
def add_item_to_temp(request):
    item_itemid = request.POST.get('item_itemid')
    item_cat = request.POST.get('item_cat')
    ticket_id = request.POST.get('ticket_id')
    user = request.user
    temp = StudioOutfitTemp.objects.get(ticket_id=ticket_id, user=user)
    error_msg = ''

    item = Item.objects.get(itemid=item_itemid)

    default_img1_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/studiooutfittemps/default_img1.jpg'
    default_img2_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/studiooutfittemps/default_img2.jpg'
    default_img3_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/studiooutfittemps/default_img3.jpg'
    default_img4_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/studiooutfittemps/default_img4.jpg'

    item1 = Item.objects.get(itemid=temp.item1id) if temp.item1id else None
    item2 = Item.objects.get(itemid=temp.item2id) if temp.item2id else None
    item3 = Item.objects.get(itemid=temp.item3id) if temp.item3id else None
    item4 = Item.objects.get(itemid=temp.item4id) if temp.item4id else None

    if item_cat == 'top':
        tops_count = sum(1 for it in [item1, item3, item4] if it and it.cat == 'top')
        dresses_count = 1 if item2 and item2.cat == 'dress' else 0

        if tops_count >= 2:
            error_msg = 'Cannot have more than 2 tops.'
        elif tops_count == 1 and dresses_count == 1:
            error_msg = 'Cannot have 1 dress and 2 tops.'
        elif temp.item1img.url == default_img1_url:
            temp.item1img = item.image
            temp.item1id = item.itemid
        elif temp.item3img.url == default_img3_url:
            temp.item3img = item.image
            temp.item3id = item.itemid
        elif temp.item4img.url == default_img4_url:
            temp.item4img = item.image
            temp.item4id = item.itemid
        else:
            error_msg = 'Please remove an item and try again. Remember you cannot have more than 2 tops.'

    elif item_cat == 'dress':
        tops_count = sum(1 for it in [item1, item3, item4] if it and it.cat == 'top')

        if tops_count >= 2:
            error_msg = 'Cannot have 2 tops and a dress.'
        elif item2 and item2.cat in ['bottom', 'dress']:
            error_msg = 'Cannot have a bottom and a dress.' if item2.cat == 'bottom' else 'Cannot have more than 1 dress.'
        elif temp.item2img.url == default_img2_url:
            temp.item2img = item.image
            temp.item2id = item.itemid

    elif item_cat == 'bottom':
        if item2 and item2.cat in ['bottom', 'dress']:
            error_msg = 'Cannot have more than 1 bottom.' if item2.cat == 'bottom' else 'Cannot have a bottom and a dress.'
        elif temp.item2img.url == default_img2_url:
            temp.item2img = item.image
            temp.item2id = item.itemid

    elif item_cat == 'footwear':
        footwear_count = sum(1 for it in [item3, item4] if it and it.cat == 'footwear')

        if footwear_count >= 1:
            error_msg = 'Cannot have more than 1 footwear.'
        elif temp.item3img.url == default_img3_url:
            temp.item3img = item.image
            temp.item3id = item.itemid
        elif temp.item4img.url == default_img4_url:
            temp.item4img = item.image
            temp.item4id = item.itemid
        else:
            error_msg = 'Please clear one of the last 2 spaces and try again.'


    elif item_cat == 'accessory':
        if 'bag' in item.tags.lower() and ((item3 and 'bag' in item3.tags.lower()) or (item4 and 'bag' in item4.tags.lower())):
                error_msg = 'Cannot have more than 1 bag.'
        elif 'glasses' in item.tags.lower() and ((item3 and 'glasses' in item3.tags.lower()) or (item4 and 'glasses' in item4.tags.lower())):
                error_msg = 'Cannot have more than 1 pair of glasses.'
        elif temp.item3img.url == default_img3_url:
            temp.item3img = item.image
            temp.item3id = item.itemid
        elif temp.item4img.url == default_img4_url:
            temp.item4img = item.image
            temp.item4id = item.itemid
        else:
            error_msg = 'Please clear one of the last 2 spaces and try again.'


    if error_msg:
        messages.error(request, error_msg)

    temp.save()
    return redirect('studio:studio_items', ticket_id=ticket_id)  # Redirect back to the item selection page










def submit_outfit(request, ticket_id):
    user = request.user
    ticket = get_object_or_404(Ticket, id=ticket_id)
    temp = get_object_or_404(StudioOutfitTemp, user=user, ticket=ticket)

    # musthave
    if not(
            (temp.item1id and temp.item2id and temp.item3id) or
            (temp.item1id and temp.item2id and temp.item4id) or
            (temp.item1id and temp.item3id and temp.item4id) or
            (temp.item2id and temp.item3id and temp.item4id)
    ):
        messages.error(request, 'Submission failed.\nPlease include at least 3 items.')
        return redirect('studio:studio_items', ticket_id=ticket_id)

    # musthave
    if not temp.item2id:
        messages.error(request, 'Submission failed.\nPlease include a bottom or a dress.')
        return redirect('studio:studio_items', ticket_id=ticket_id)

    # musthave Fetch the items to check their categories
    item1 = Item.objects.get(itemid=temp.item1id) if temp.item1id else None
    item2 = Item.objects.get(itemid=temp.item2id) if temp.item2id else None
    item3 = Item.objects.get(itemid=temp.item3id) if temp.item3id else None
    item4 = Item.objects.get(itemid=temp.item4id) if temp.item4id else None
    # Check if item2 is a bottom and if there is no top in item1, item3, or item4
    if item2 and item2.cat == 'bottom':
        if not ((item1 and item1.cat == 'top') or (item3 and item3.cat == 'top') or (item4 and item4.cat == 'top')):
            messages.error(request, 'Submission failed.\nPlease include a top.')
            return redirect('studio:studio_items', ticket_id=ticket_id)
    # an einai dress - kane oti thes


    # Create new outfit
    new_outfit = Outfit.objects.create(
        maker_id=user,  # Updated field
        ticket_id=ticket,  # Assigning the ticket instance instead of the ID
        timestamp=timezone.now(),
        image='outfits/default_img.jpg'  # Use default image
    )

    # Fetch Item instances using itemid
    item_ids = [temp.item1id, temp.item2id, temp.item3id, temp.item4id]
    items = Item.objects.filter(itemid__in=[item_id for item_id in item_ids if item_id])

    # Ensure all items exist
    if len(items) != len([item_id for item_id in item_ids if item_id]):
        messages.error(request, 'Some items do not exist.')
        return redirect('studio:studio_items', ticket_id=ticket_id)

    # Set items for the new outfit
    new_outfit.items.set(items)

    # Update ticket
    ticket.current_outfits += 1
    ticket.outfits_all.add(new_outfit)
    if ticket.current_outfits >= ticket.maximum_outfits:
        ticket.status = 'closed'
    ticket.save()

    # Add a delay to give time for the outfit to be fully created
    time.sleep(1)

    # Process the outfit's items to create a composite image
    image_path = create_composite_image(new_outfit)

    if image_path:
        with default_storage.open(image_path, 'rb') as img_file:
            new_outfit.image.save(f'outfit_{new_outfit.id}.jpeg', img_file, save=True)
        messages.success(request, 'Outfit submitted successfully.')
    else:
        messages.error(request, 'Image processing failed.')

    return redirect('studio:studio_success')


def studio_success(request):
    return render(request, 'studio/studio_success.html')