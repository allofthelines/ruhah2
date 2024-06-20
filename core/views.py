import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.db.models import Count
from django.db.models import Q
from django.views.generic import TemplateView

from .forms import OutfitRatingForm
from .models import Outfit
from accounts.models import Customer, CustomUser, UserFollows
from box.models import Ticket  # Assuming the Ticket model is in the box app

def home(request):
    if request.method == "POST":
        form = OutfitRatingForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("core:home")

    # Fetch ticket IDs that have at least two outfits associated with them
    ticket_ids_with_at_least_two_outfits = Outfit.objects.values('ticket_id').annotate(outfit_count=Count('id')).filter(
        outfit_count__gte=2)

    if ticket_ids_with_at_least_two_outfits:
        # Randomly select one ticket ID from those available
        chosen_ticket_id = random.choice(ticket_ids_with_at_least_two_outfits)['ticket_id']
        # Get all outfits with the chosen ticket ID
        outfits_with_ticket_id = list(Outfit.objects.filter(ticket_id=chosen_ticket_id))
        # Randomly select two outfits
        outfits = random.sample(outfits_with_ticket_id, k=2)
    else:
        # Handle the situation where there aren't enough outfits with the same ticket ID
        outfits = []
        message = "Not enough outfits with the same ticket ID in the database"
        return render(request, "core/home.html", {"message": message})

    return render(request, "core/home.html", {"outfits": outfits})


class TrendingView(ListView):
    template_name = "core/trending.html"
    model = Outfit
    ordering = "-rating"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.is_authenticated:
            if user.trending_mode == 'following':
                following_ids = UserFollows.objects.filter(user_from=user).values_list('user_to_id', flat=True)
                queryset = queryset.filter(maker_id__in=following_ids)

            # Filter outfits based on the user's trending_styles
            user_styles = set(user.trending_styles.values_list('id', flat=True))
            queryset = queryset.filter(ticket_id__style1__id__in=user_styles)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['trending_mode'] = user.trending_mode
        else:
            context['trending_mode'] = 'discover'

        return context


class UploadView(CreateView):
    model = Outfit
    fields = ("image",)
    template_name = "core/upload.html"
    success_url = reverse_lazy("core:upload")

class TermsView(TemplateView):
    template_name = 'core/terms.html'

class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'

class HelpView(TemplateView):
    template_name = 'core/help.html'

class SocialView(TemplateView):
    template_name = 'core/social.html'




def search(request):
    query = request.GET.get('q')
    if query:
        if query.lower() == 'all':
            users = CustomUser.objects.all().order_by('username')
        else:
            users = CustomUser.objects.filter(username__icontains=query).order_by('username')
    else:
        users = CustomUser.objects.none()

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'core/search.html', context)
