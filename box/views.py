from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from ruhah import settings
from .forms import TicketForm  # Ensure you create this form in the forms.py file
from .models import Ticket  # Make sure you have this model defined in your models.py
import stripe
from django.utils import timezone
from django.urls import reverse
from django.urls import reverse
# afta einai gia to json gia to studio_tickets.html
from django.http import JsonResponse
from .models import Ticket
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, Customer

from django.views.decorators.csrf import csrf_exempt

stripe.api_key = "sk_test_51HjtkWHCAjs916uo0avrWzOy7rb2tImrjRVgFKdWeXye6zFbn6sZrQafC2QTkpcsaGWPMgiTfIqigXA5lCFfDOFV00gJ5e6ekt"
endpoint_secret = 'whsec_2vr6jDZBVHSF0WJ3uC180K1iFKFllyb7' # sto webhook # TO KSANAVAZW KATW KANE SEARCH ENDPOINT

def ticket_view(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid() or not form.is_valid():
            size_top_xyz = None
            size_bottom_xyz = None
            size_waist_inches = None
            shoe_size_eu = None
            shoe_size_uk = None
            print('FORM VALID')

            if request.user.is_authenticated:
                customer = get_object_or_404(Customer, user=request.user)  # Fetch the Customer instance
                size_top_xyz = customer.top_size_xyz
                size_bottom_xyz = customer.bottom_size_xyz
                size_waist_inches = customer.size_waist_inches
                shoe_size_eu = customer.shoe_size_eu
                shoe_size_uk = customer.shoe_size_uk
                username = request.user.username  # Fetch the username from CustomUser
                print('shoe_size_eu', shoe_size_eu)

                if customer.top_size_xyz is None:
                    size_top_xyz = form.cleaned_data.get('size_top_xyz')
                if customer.bottom_size_xyz is None:
                    size_bottom_xyz = form.cleaned_data.get('size_bottom_xyz')
                if customer.size_waist_inches is None:
                    size_waist_inches = form.cleaned_data.get('size_waist_inches')
                if customer.shoe_size_eu is None:
                    shoe_size_eu = form.cleaned_data.get('size_shoe_eu')
                if customer.shoe_size_uk is None:
                    shoe_size_uk = form.cleaned_data.get('size_shoe_uk')

                if not customer.top_size_xyz:
                    customer.top_size_xyz = size_top_xyz
                if not customer.bottom_size_xyz:
                    customer.bottom_size_xyz = size_bottom_xyz
                if not customer.size_waist_inches:
                    customer.size_waist_inches = size_waist_inches
                if not customer.shoe_size_eu:
                    customer.shoe_size_eu = shoe_size_eu
                if not customer.shoe_size_uk:
                    customer.shoe_size_uk = shoe_size_uk
                customer.save()

            else:
                size_top_xyz = form.cleaned_data['size_top_xyz']
                size_bottom_xyz = form.cleaned_data['size_bottom_xyz']
                size_waist_inches = form.cleaned_data['size_waist_inches']
                shoe_size_eu = form.cleaned_data['size_shoe_eu']
                shoe_size_uk = form.cleaned_data['size_shoe_uk']

            if not (size_top_xyz and size_bottom_xyz and size_waist_inches and shoe_size_eu and shoe_size_uk):
                return render(request, 'box/ticket_form.html', {'form': form, 'size_fields_required': True})

            ticket = Ticket(
                style1=form.cleaned_data['style1'],
                occasion=form.cleaned_data['occasion'],
                condition=form.cleaned_data['condition'],
                price=form.cleaned_data['price'],
                notes=form.cleaned_data['notes'],
                size_top_xyz=size_top_xyz,
                size_bottom_xyz=size_bottom_xyz,
                size_waist_inches=size_waist_inches,
                size_shoe_eu=shoe_size_eu,
                size_shoe_uk=shoe_size_uk,
                creator_id=request.user if request.user.is_authenticated else None,  # Set creator_id if authenticated
            )
            ticket.save()
            request.session['ticket_id'] = ticket.id
            return redirect('box:success_url')  # Ensure this line matches the URL name in urls.py
        else:
            print('FORM NOT VALID')
            return render(request, 'box/ticket_form.html', {'form': form})
    else:
        initial_data = {}
        if request.user.is_authenticated:
            customer = get_object_or_404(Customer, user=request.user)  # Fetch the Customer instance
            if customer.top_size_xyz:
                initial_data['size_top_xyz'] = customer.top_size_xyz
            if customer.bottom_size_xyz:
                initial_data['size_bottom_xyz'] = customer.bottom_size_xyz
            if customer.size_waist_inches:
                initial_data['size_waist_inches'] = customer.size_waist_inches
            if customer.shoe_size_eu:
                initial_data['size_shoe_eu'] = customer.shoe_size_eu
            if customer.shoe_size_uk:
                initial_data['size_shoe_uk'] = customer.shoe_size_uk

        form = TicketForm(initial=initial_data)
        print(initial_data)
        return render(request, 'box/ticket_form.html', {'form': form})

def success_view(request):
    ticket_id = request.session.get('ticket_id', 'Unknown Ticket ID')
    return render(request, 'box/success.html', {'ticket_id': ticket_id})


# afta einai gia to json gia to studio_tickets.html
@login_required
def api_tickets(request):
    page_number = request.GET.get('page', 1)
    tickets = Ticket.objects.filter(status='open').exclude(stylists_all__username=request.user.username).distinct()
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_obj = paginator.get_page(page_number)

    tickets_data = [
        {
            "id": ticket.id,
            "style1": ticket.style1,
            "style2": ticket.style2.style_name if ticket.style2 else 'None', # SVHSE AN ERROR prepei na return as string gia to  studio_tickets.ja
            "occasion": ticket.occasion,
            "notes": ticket.notes
        }
        for ticket in page_obj
    ]

    return JsonResponse({"tickets": tickets_data})


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .forms import TicketForm
from .models import Ticket, Order
from accounts.models import CustomUser
import stripe
import json
from django.utils import timezone


# edw ksekinaei stripe
def create_checkout_session(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    domain_name = settings.DOMAIN_NAME

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Styling Fee',
                },
                'unit_amount': 1500,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{domain_name}{reverse('box:payment_successful')}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{domain_name}{reverse('box:payment_rejected')}",
        metadata={
            'ticket_id': ticket.id
        }
    )

    return redirect(session.url, code=303)


# ERXOMAI EDW APO URLS.PY
# GIA NA PAS STO URLS.PY H ENTOLH ERXETAI APO STRIPE
# APO TO LINK POU VAZEIS STO WEBHOOK
# PREPEI NANAI TO URLS.PY POU SE STELNEI EDW
# WEBSITE.COM/BOX/ *TO URL PATTERN STO URLS.PY* PROSOXH DONT FORGET TO /BOX/
# to @csrf_exempt shmantiko also, xwris afto error
# einai gia cross party used otan kanw interraction me alla site
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # ISWS PROBLHMA EDW GIATI ORDER.TICKET_ID PLEON EINAI FK KAI OXI CHARFIELD
        # DES PIO KATW
        ticket_id = session['metadata']['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.status = 'open' # doulevei
        ticket.save()

        # Extract payment details from the session
        amount_paid = session['amount_total'] / 100  # Stripe amounts are in cents
        customer_id = session.get('customer')
        customer_details = session.get('customer_details', {})

        # Extract customer email and address
        customer_email = customer_details.get('email')
        customer_address = str(customer_details.get('address', 'N/A'))

        timestamp = timezone.now()

        # Create the order
        order = Order(
            type='box',
            # ISWS PROBLHMA EDW GIATI ORDER.TICKET_ID PLEON EINAI FK KAI OXI CHARFIELD
            # MALLON PREPEI NA GINEI ticket_id=ticket ok to ekana
            # PALIA HTAN ticket_id=ticket_id
            ticket_id=ticket,  # Assigning the Ticket instance
            money=amount_paid,
            creator_id=CustomUser.objects.get(id=customer_id) if customer_id else None,
            status='preparing',
            address_customer=customer_address,
            timestamp=timestamp
        )
        order.save()

    return HttpResponse(status=200)


def payment_successful(request):
    return render(request, 'box/payment_successful.html')

def payment_rejected(request):
    return render(request, 'box/payment_rejected.html')