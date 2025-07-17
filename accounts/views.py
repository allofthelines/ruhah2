from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser, Customer, UserItemLikes, InviteCode
from studio.models import Style, Item
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserProfileForm, CustomerForm, PortraitUploadForm, ProfileSettingsForm, EmailChangeForm, GridPicUploadForm
import json
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils import timezone
from django.db.models import Q  # gia to search sto profile_gridpic_try_on



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # Use the custom SignUpForm
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            # Fetch all styles and assign to the user
            all_styles = Style.objects.all()
            user.trending_styles.set(all_styles)
            user.studio_styles.set(all_styles)

            # Save the user again to ensure ManyToMany fields are saved
            user.save()



            # Handle the invite code
            # TO EKANA ADD STO TELOS
            if settings.INVITE_CODE_REQUIRED:
                invite_code = form.cleaned_data.get('invite_code')
                if invite_code:
                    invite_code_obj = InviteCode.objects.get(invite_code=invite_code)
                    invite_code_obj.is_used = True
                    invite_code_obj.invitee = user
                    invite_code_obj.save()



            send_signup_confirmation_email(user)  # Send confirmation email
            return redirect('accounts:account_activation_sent')
    else:
        form = SignUpForm()  # Use the custom SignUpForm

    # Print CSRF token for debugging
    print("CSRF Token in session: ", request.session.get('csrf_token'))
    print("CSRF Token in request: ", get_token(request))

    return render(request, 'accounts/signup.html', {'form': form})

def send_signup_confirmation_email(user):
    subject = 'Welcome'
    from_email = 'RUHAH <contact@ruhah.com>'
    message = render_to_string('accounts/activation_email.txt', {
        'user': user,
        'domain': settings.EMAIL_DOMAIN,
        'protocol': settings.EMAIL_PROTOCOL,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    send_mail(subject, message, from_email, [user.email], fail_silently=False)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # Optionally log the user in
        return redirect('accounts:activation_success')
    else:
        return render(request, 'accounts/activation_invalid.html')




def activation_success(request):
    return render(request, 'accounts/activation_success.html')

def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')



from .models import PortraitUpload, GridPicUpload
from box.models import Ticket


@login_required
def profile(request):
    user = request.user
    customer = getattr(user, 'customer', None)

    user_form = UserProfileForm(instance=user, user=user)
    customer_form = CustomerForm(instance=customer, customer=customer) if customer else None
    portrait_upload_form = PortraitUploadForm(user=user)  # Pass user to the form
    gridpic_upload_form = GridPicUploadForm(user=user)
    profile_settings_form = ProfileSettingsForm(instance=user, user=user)

    available_styles = Style.objects.all()
    user_trending_styles = user.trending_styles.all()
    user_studio_styles = user.studio_styles.all()
    user_gridpics = GridPicUpload.objects.filter(uploader_id=user, deleted_by_uploader='no').order_by('-timedate_uploaded')

    editing = request.GET.get('edit') == 'true'
    editing_settings = request.GET.get('edit_settings') == 'true'

    invite_codes = InviteCode.objects.filter(inviter=user, is_used=False)

    # Query the UserItemLikes model for the logged-in user
    user_likes = UserItemLikes.objects.filter(liker=user)

    user_tickets = Ticket.objects.filter(
        creator_id=request.user.id,
        asktype='outfit',
        creator_profile_visibility='show'
    )

    if request.method == 'POST':
        if 'user_form' in request.POST:
            user_form = UserProfileForm(request.POST, request.FILES, instance=user, user=user)
            if user_form.is_valid():
                print("DEBUG: Form is valid")
                print("DEBUG: Current username in form before save:", user_form.cleaned_data['username'])
                saved_user = user_form.save(commit=True)
                print("DEBUG: Username after form save:", saved_user.username)  # Confirm the username after save
                print("DEBUG: Username directly from DB after form save:",
                      CustomUser.objects.get(id=user.id).username)  # Check directly from DB
                return redirect(f'{request.path}?edit=user')
            else:
                print("DEBUG: Form is not valid")
                print("Form errors:", user_form.errors)  # Print form errors if form is not valid
            # Handle other forms...
        elif 'customer_form' in request.POST and customer:
            customer_form = CustomerForm(request.POST, instance=customer, customer=customer)
            if customer_form.is_valid():
                customer_form.save(customer=customer)
                return redirect(f'{request.path}?edit=customer')
        elif 'portrait_upload_form' in request.POST:
            portrait_upload_form = PortraitUploadForm(request.POST, request.FILES, user=user)  # Pass user to the form
            if portrait_upload_form.is_valid():
                portrait_upload = portrait_upload_form.save(commit=False)
                portrait_upload.wearer_id = user  # Automatically assign the current user
                portrait_upload.status = 'pending'  # Automatically assign status to 'pending'
                portrait_upload.save()
                return redirect('accounts:upload_success')  # Redirect to the success page
        elif 'gridpic_upload_form' in request.POST:
            gridpic_upload_form = GridPicUploadForm(request.POST, request.FILES, user=user)
            if gridpic_upload_form.is_valid():
                gridpic_upload = gridpic_upload_form.save(commit=False)
                gridpic_upload.uploader_id = user
                gridpic_upload.save()
                return redirect('accounts:upload_gridpic_success')
        elif 'profile_settings_form' in request.POST:
            profile_settings_form = ProfileSettingsForm(request.POST, instance=user, user=user)
            if profile_settings_form.is_valid():
                profile_settings_form.save(user=user)
                selected_trending_styles = request.POST.getlist('trending_styles')
                selected_studio_styles = request.POST.getlist('studio_styles')
                user.trending_styles.set(selected_trending_styles)
                user.studio_styles.set(selected_studio_styles)
                user.accept_private_asks = request.POST.get('accept_private_asks', 'yes')
                user.private_ask_price = request.POST.get('private_ask_price', 0)
                return redirect(f'{request.path}?edit_settings=false')

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'portrait_upload_form': portrait_upload_form,
        'profile_s'
        'ettings_form': profile_settings_form,
        'gridpic_upload_form': gridpic_upload_form,  # Add this line
        'user': user,
        'available_styles': available_styles,
        'user_trending_styles': user_trending_styles,
        'user_studio_styles': user_studio_styles,
        'user_gridpics': user_gridpics,
        'editing': editing,
        'editing_settings': editing_settings,
        'user_likes': user_likes,
        'user_tickets': user_tickets,
        'invite_codes': invite_codes,
    }

    return render(request, 'accounts/profile.html', context)

def upload_gridpic_success(request):
    return render(request, 'accounts/upload_gridpic_success.html')

@login_required
def upload_success(request):
    return render(request, 'accounts/upload_success.html')























from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "accounts/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': settings.EMAIL_DOMAIN,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': settings.EMAIL_PROTOCOL,
                    }
                    email = render_to_string(email_template_name, c)
                    from_email = 'RUHAH <contact@ruhah.com>'  # Set the sender name here
                    send_mail(subject, email, from_email, [user.email], fail_silently=False)
            return redirect("accounts:password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="accounts/password_reset.html", context={"password_reset_form": password_reset_form})




from django.contrib.auth.views import PasswordResetConfirmView

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')











from django.shortcuts import render, get_object_or_404, redirect
from .models import CustomUser, UserFollows, GridPicUpload
from django.contrib.auth.models import AnonymousUser
import random
from itertools import chain
from operator import attrgetter
import math

""" BEFORE INTRODUCTION OF GRID PICS // ONLY WITH OUTFITS - DIFFERENT LOGIC

def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    is_own_profile = (request.user == profile_user)
    is_following = False

    if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
        is_following = UserFollows.objects.filter(user_from=request.user, user_to=profile_user).exists()

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
    }
    return render(request, 'accounts/public_profile.html', context)"""


def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    is_own_profile = (request.user == profile_user)
    is_following = False

    if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
        is_following = UserFollows.objects.filter(user_from=request.user, user_to=profile_user).exists()

    # Fetch outfits and order by timestamp (recent first)
    outfits = list(Outfit.objects.filter(maker_id=profile_user, maker_grid_visibility='show').order_by('-timestamp'))

    # Fetch non-deleted GridPicUpload objects and order by timedate_uploaded (recent first)
    grid_pics = list(GridPicUpload.objects.filter(uploader_id=profile_user, deleted_by_uploader='no').order_by('-timedate_uploaded'))

    # Combine and shuffle
    # grid_items = list(outfits) + list(grid_pics)
    # random.shuffle(grid_items)

    # Calculate the interval for inserting GridPicUploads
    if len(grid_pics) > 0:
        interval = max(1, math.floor(len(outfits) / len(grid_pics)))
    else:
        interval = len(outfits)  # If no grid_pics, interval is the length of outfits

    # Interleave outfits and grid_pics
    grid_items = []
    grid_pic_index = 0
    for i, outfit in enumerate(outfits):
        grid_items.append({'type': 'outfit', 'item': outfit})
        if i % interval == interval - 1 and grid_pic_index < len(grid_pics):
            grid_items.append({'type': 'gridpic', 'item': grid_pics[grid_pic_index]})
            grid_pic_index += 1

    # Add any remaining grid_pics at the end
    grid_items.extend({'type': 'gridpic', 'item': pic} for pic in grid_pics[grid_pic_index:])

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'grid_items': grid_items,
    }
    return render(request, 'accounts/public_profile.html', context)


@login_required
def follow(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    if request.method == 'POST' and request.user != profile_user:
        UserFollows.objects.get_or_create(user_from=request.user, user_to=profile_user)
    return redirect('accounts:public_profile', username=username)

@login_required
def unfollow(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    if request.method == 'POST' and request.user != profile_user:
        UserFollows.objects.filter(user_from=request.user, user_to=profile_user).delete()
    return redirect('accounts:public_profile', username=username)

"""def followers_list(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    followers = UserFollows.objects.filter(user_to=profile_user).select_related('user_from')
    followers_list = [relation.user_from for relation in followers]
    context = {
        'profile_user': profile_user,
        'followers': followers_list,
    }
    return render(request, 'accounts/followers_list.html', context)"""


def followers_list(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    followers = UserFollows.objects.filter(user_to=profile_user).select_related('user_from')
    followers_list = [relation.user_from for relation in followers]

    # Add logic to check if the logged-in user is following each user in the followers list
    if request.user.is_authenticated:
        followed_users = UserFollows.objects.filter(user_from=request.user).values_list('user_to_id', flat=True)
    else:
        followed_users = []

    context = {
        'profile_user': profile_user,
        'followers': followers_list,
        'followed_users': followed_users,
    }
    return render(request, 'accounts/followers_list.html', context)


"""def following_list(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    following = UserFollows.objects.filter(user_from=profile_user).select_related('user_to')
    following_list = [relation.user_to for relation in following]
    context = {
        'profile_user': profile_user,
        'following': following_list,
    }
    return render(request, 'accounts/following_list.html', context)"""

def following_list(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    following = UserFollows.objects.filter(user_from=profile_user).select_related('user_to')
    following_list = [relation.user_to for relation in following]

    # Add logic to check if the logged-in user is following each user in the following list
    if request.user.is_authenticated:
        followed_users = UserFollows.objects.filter(user_from=request.user).values_list('user_to_id', flat=True)
    else:
        followed_users = []

    context = {
        'profile_user': profile_user,
        'following': following_list,
        'followed_users': followed_users,
    }
    return render(request, 'accounts/following_list.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import UserItemLikes
from core.models import Outfit
import json

@login_required
@require_POST
def like_outfit(request):
    try:
        data = json.loads(request.body)
        outfit_id = data.get('outfit_id')
        print('BBBBBBBBBBBBBBB\n', outfit_id, '\nBBBBBBBBBBBBBB')

        if not outfit_id:
            return JsonResponse({'status': 'error', 'message': 'No outfit ID provided'}, status=400)

        outfit = Outfit.objects.get(id=outfit_id)
        liker = request.user
        styler = outfit.maker_id

        for item in outfit.items.all():
            # Check if a UserItemLikes instance already exists
            if not UserItemLikes.objects.filter(liker=liker, item=item).exists():
                UserItemLikes.objects.create(
                    item=item,  # Use 'item' instead of 'outfit'
                    liker=liker,
                    styler=styler
                )

        print('DEBUG: Successfully added likes')
        return JsonResponse({'status': 'success'})
    except Outfit.DoesNotExist:
        print('DEBUG: Outfit not found')
        return JsonResponse({'status': 'error', 'message': 'Outfit not found'}, status=404)
    except json.JSONDecodeError:
        print('DEBUG: JSON decode error')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print('DEBUG: Unexpected error', str(e))
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)


def remove_like(request, like_id):
    if request.method == "POST":
        try:
            like = UserItemLikes.objects.get(id=like_id, liker=request.user)
            like.delete()
        except UserItemLikes.DoesNotExist:
            pass  # Handle the case where the like doesn't exist if necessary

    next_url = request.GET.get('next', reverse('accounts:profile') + '#likes')  # Default to 'accounts:profile#likes' if 'next' not provided
    return redirect(next_url)

@login_required
def remove_all_likes(request):
    if request.method == "POST":
        UserItemLikes.objects.filter(liker=request.user).delete()
    next_url = request.GET.get('next', reverse('accounts:profile') + '#likes')  # Default to 'accounts:profile#likes' if 'next' not provided
    return redirect(next_url)


@login_required
def profile_likes_randomize(request):
    if request.method == 'POST':
        user_likes = UserItemLikes.objects.filter(liker=request.user)

        # Separate items by category
        tops = [like.item for like in user_likes if like.item.cat == 'top' and like.item.sizes_xyz.exists()]
        bottoms = [like.item for like in user_likes if like.item.cat == 'bottom' and like.item.sizes_xyz.exists()]
        accessories = [like.item for like in user_likes if
                       like.item.cat == 'accessory' and like.item.sizes_xyz.exists()]

        # Function to get a random item of a specific category
        def get_random_item(category):
            items = category[:]  # Create a copy to avoid modifying the original list
            if items:
                item = random.choice(items)
                category.remove(item)  # Remove the item to avoid repetition
                return item
            return None

        # Create two sets of 3 items each
        randomized_items = []
        for _ in range(2):  # Do this twice for 3+3 items
            for category in [tops, bottoms, accessories]:
                item = get_random_item(category)
                if item:
                    randomized_items.append(item)

        if not randomized_items:
            message = "None of these items is available. Please like more outfits and try again."
            return render(request, 'accounts/profile_likes_randomize.html', {'message': message})

        # Remove all likes
        user_likes.delete()

        context = {
            'randomized_items': randomized_items,
        }
        return render(request, 'accounts/profile_likes_randomize.html', context)
    else:
        # Handle GET request, maybe redirect to profile page
        return redirect('accounts:profile')


def remove_ask(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.creator_id.id == request.user.id:
        ticket.creator_profile_visibility = 'hide'
        ticket.save()
    return redirect('accounts:profile')


def remove_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfit, id=outfit_id)
    if request.method == 'POST' and request.user == outfit.maker_id:
        outfit.maker_grid_visibility = 'hide'
        outfit.save()
        next_url = request.GET.get('next', 'accounts:profile')
        return redirect(next_url)
    return redirect('accounts:profile')

@login_required
def remove_gridpic(request, gridpic_id):
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id)
    if request.method == 'POST' and request.user == gridpic.uploader_id:
        gridpic.deleted_by_uploader = 'yes'
        gridpic.timedate_deleted_by_uploader = timezone.now()
        gridpic.save()
        next_url = request.GET.get('next', 'accounts:profile')
        return redirect(next_url)
    return redirect('accounts:profile')

from studio.models import SizeCategory

def profile_ask_outfit_details(request, outfit_id):
    outfit = get_object_or_404(Outfit, id=outfit_id)
    items = outfit.items.all().prefetch_related('sizes_xyz')

    context = {
        'outfit': outfit,
        'items': items,
    }
    return render(request, 'accounts/profile_ask_outfit_details.html', context)


def profile_grid_outfit_details(request, outfit_id):
    outfit = get_object_or_404(Outfit, id=outfit_id)

    # Retrieve all the items associated with the outfit, including size details
    items = outfit.items.all().prefetch_related('sizes_xyz')

    context = {
        'outfit': outfit,
        'items': items,
        'profile_user': outfit.maker_id,  # Assuming outfit has a maker field that refers to the profile user
        'outfit_id': outfit.id, # passes outfit_id to template gia to ai chat gia to back button
    }

    # Render the template with the context
    return render(request, 'accounts/profile_grid_outfit_details.html', context)















def email_change_request(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.new_email = form.cleaned_data['new_email']
            user.email_change_requested_at = timezone.now()
            user.save()
            send_email_change_confirmation_email(user)
            return redirect('accounts:email_change_requested')
    else:
        form = EmailChangeForm(instance=request.user)
    return render(request, 'accounts/email_change_request.html', {'form': form})

def send_email_change_confirmation_email(user):
    subject = "Confirm Your Email Address"
    from_email = 'RUHAH <contact@ruhah.com>'
    email_template_name = "accounts/email_change_confirmation.html"
    c = {
        "email": user.new_email,
        'domain': settings.EMAIL_DOMAIN,
        'protocol': settings.EMAIL_PROTOCOL,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
    }
    email = render_to_string(email_template_name, c)
    send_mail(subject, email, from_email, [user.new_email], fail_silently=False)


def email_change_requested(request):
    return render(request, 'accounts/email_change_requested.html')

def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email = user.new_email
        user.new_email = None
        user.email_change_requested_at = None
        user.save()
        return render(request, 'accounts/email_confirmed.html')
    else:
        return render(request, 'accounts/email_confirmation_failed.html')



























"""
ENERGO ALLA TOXW VGALEI TRY-ON PART
VALE/VGALE KRYVONTAS TO KOUMPI TRY-ON STO PROFILE.HTML
"""


def tryon_item_search(request, gridpic_id):
    # Fetch the GridPicUpload object using gridpic_id from the URL
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    print(f"Selected GridPic: {gridpic}")

    # Determine which image to show
    if gridpic.tryon_state == 'temp' and gridpic.gridpic_temp_img:
        # Show the temporary image if it exists
        selected_gridpic_url = gridpic.gridpic_temp_img.url
    elif gridpic.tryon_state == 'virtual' and gridpic.gridpic_tryon_img:
        # Show the try-on image if it exists
        selected_gridpic_url = gridpic.gridpic_tryon_img.url
    else:
        # Show the original processed image
        selected_gridpic_url = gridpic.gridpic_processed_img.url

    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', 'all')
    search_results = Item.objects.none()

    # Perform the search only if the search parameter is present
    if 'search' in request.GET:
        search_results = Item.objects.all()

        if search_query:
            words = search_query.split()
            query = Q()
            for word in words:
                query &= Q(tags__icontains=word)
            search_results = search_results.filter(query)

        if category and category != 'all':
            search_results = search_results.filter(cat=category)

    context = {
        'selected_gridpic': gridpic,  # Ensure the gridpic is available in the template
        'selected_gridpic_url': selected_gridpic_url,  # Add the URL for the selected gridpic
        'search_results': search_results,  # Pass search results to the template
    }

    # Render the template and display search results
    return render(request, 'accounts/profile_gridpic_try_on.html', context)






import requests
from django.conf import settings

def call_kolors_api(image1_path, image2_path):
    """
    Function to call the Kolors model API with two images and receive a processed image.
    """
    try:
        # Prepare the payload for the API request
        with open(image1_path, 'rb') as image1, open(image2_path, 'rb') as image2:
            files = {
                'image1': image1,
                'image2': image2
            }
            headers = {
                'Authorization': f"Bearer {settings.KOLORS_API_KEY}",
                'Content-Type': 'multipart/form-data'
            }
            response = requests.post(settings.KOLORS_API_URL, files=files, headers=headers)

        # Check if the response is successful
        if response.status_code == 200:
            return response.content  # Assume the API returns the processed image content
        else:
            print("Error:", response.json())
            return None

    except Exception as e:
        print(f"Error calling Kolors API: {str(e)}")
        return None










"""
------------------------------
PERFORM = TELEFTAIO VHMA
------------------------------
"""
import requests
from django.conf import settings
from django.core.files.base import ContentFile

@login_required
def perform_try_on(request, gridpic_id, item_id):
    """
    Handle the "Try-On" process by integrating with the Kolors model API.
    """
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)
    item = get_object_or_404(Item, id=item_id)

    # Ensure user has enough credits
    if request.user.credits < 10:
        messages.error(request, "You need at least 10 credits to perform a Try-On.")
        return redirect('accounts:profile')

    # Ensure the gridpic is in the original state
    if gridpic.tryon_state != 'original':
        messages.error(request, "This gridpic already has a try-on applied.")
        return redirect('accounts:profile_gridpic_try_on', gridpic_id=gridpic.id)

    # Call the Kolors API with the selected images
    response = call_kolors_api(gridpic.gridpic_processed_img.path, item.image.path)

    if response:
        # Save the processed image temporarily
        temp_image_name = f"{gridpic.gridpic_processed_img.name.split('/')[-1].split('.')[0]}_temp.png"
        gridpic.gridpic_temp_img.save(temp_image_name, ContentFile(response), save=True)

        # Set the tryon_state to 'temp'
        gridpic.tryon_state = 'temp'
        gridpic.gridpic_tryon_item_id.set([item])  # Associate the selected item
        gridpic.save()

        # Deduct credits from the user
        request.user.credits -= 10
        request.user.save()

        return redirect('accounts:profile_try_on_submitted')
    else:
        messages.error(request, "Failed to process Try-On. Please try again later.")
        return redirect('accounts:profile')

def perform_try_off(request, gridpic_id):
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    # Ensure it's in the virtual state before trying off
    if gridpic.tryon_state != 'virtual':
        messages.error(request, "No virtual try-on to remove.")
        return redirect('accounts:profile')

    # Set state to 'original' and delete try-on image
    gridpic.tryon_state = 'original'
    gridpic.gridpic_tryon_img.delete(save=False)  # Deleting the try-on image
    gridpic.gridpic_tryon_item_id.clear()
    gridpic.save()

    messages.success(request, "Try-on removed and reverted to original.")
    return redirect(f"{reverse('accounts:profile')}#gridpics")


from django.shortcuts import get_object_or_404, redirect
from .models import GridPicUpload
from django.contrib import messages

"""
------------------------------
PROFILE_GRIDPIC = PHGAINEI STHN EPOMENH SELIDA
------------------------------
"""
def profile_gridpic_try_on(request, gridpic_id):
    # Retrieve the selected gridpic object
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    # Determine which image to show based on the tryon_state
    if gridpic.tryon_state == 'temp' and gridpic.gridpic_temp_img:
        selected_gridpic_url = gridpic.gridpic_temp_img.url
    elif gridpic.tryon_state == 'virtual' and gridpic.gridpic_tryon_img:
        selected_gridpic_url = gridpic.gridpic_tryon_img.url
    else:
        selected_gridpic_url = gridpic.gridpic_processed_img.url

    context = {
        'selected_gridpic_url': selected_gridpic_url,
        'selected_gridpic': gridpic,
    }

    return render(request, 'accounts/profile_gridpic_try_on.html', context)

def profile_gridpic_try_off(request, gridpic_id):
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    # Ensure the gridpic is in the 'virtual' state before allowing 'try-off'
    if gridpic.tryon_state != 'virtual':
        messages.error(request, "Cannot perform try-off as the gridpic is not in the 'virtual' state.")
        return redirect('accounts:profile')

    # Perform the 'try-off' by reverting the gridpic to its original state
    gridpic.tryon_state = 'original'
    if gridpic.gridpic_tryon_img:
        gridpic.gridpic_tryon_img.delete(save=False)  # Delete the virtual try-on image
    gridpic.gridpic_tryon_item_id.clear()  # Clear any associated items
    gridpic.save()

    messages.success(request, "Try-off successful. Reverted to the original gridpic.")
    return redirect(f"{reverse('accounts:profile')}#gridpics")

"""
------------------------------
ACCEPT = DEN PHGAINEI POUTHENA APLA KLIKAREIS STO PROFILE.HTML KAI EPIKYRWNEI H OXI
------------------------------
"""
@login_required
def accept_try_on(request, gridpic_id):
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    # Ensure it's in the temp state before accepting
    if gridpic.tryon_state != 'temp':
        messages.error(request, "No temporary try-on to accept.")
        return redirect('accounts:profile')

    # Rename and move the temp image to try-on image
    if gridpic.gridpic_temp_img:
        tryon_image_name = f"{gridpic.gridpic_processed_img.name.split('/')[-1].split('.')[0]}_tryon.png"
        gridpic.gridpic_tryon_img.save(tryon_image_name, gridpic.gridpic_temp_img.file, save=True)
        gridpic.gridpic_temp_img.delete(save=False)  # Remove temp image after moving

    # Change the state to 'virtual'
    gridpic.tryon_state = 'virtual'
    gridpic.save()

    messages.success(request, "Try-on accepted and saved.")
    # return redirect('accounts:profile')
    return redirect(f"{reverse('accounts:profile')}#gridpics")

@login_required
def reject_try_on(request, gridpic_id):
    gridpic = get_object_or_404(GridPicUpload, id=gridpic_id, uploader_id=request.user)

    # Ensure it's in the temp state before rejecting
    if gridpic.tryon_state != 'temp':
        messages.error(request, "No temporary try-on to reject.")
        return redirect('accounts:profile')

    # Revert state back to 'original' and delete the temporary try-on image
    gridpic.tryon_state = 'original'
    if gridpic.gridpic_temp_img:
        gridpic.gridpic_temp_img.delete(save=False)  # Delete the temp image
    gridpic.gridpic_tryon_item_id.clear()  # Clear associated item
    gridpic.save()

    messages.success(request, "Try-on rejected and reverted to original.")
    # return redirect('accounts:profile')
    return HttpResponseRedirect(f"{reverse('accounts:profile')}#gridpics")




from django.shortcuts import render

def profile_try_on_submitted(request):
    return render(request, 'accounts/profile_try_on_submitted.html')