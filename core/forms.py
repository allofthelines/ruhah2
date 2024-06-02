from django import forms
from django.core.exceptions import ValidationError
from .models import Outfit
from accounts.models import Customer, Stylist

class OutfitRatingForm(forms.Form):
    outfit1 = forms.IntegerField()
    outfit2 = forms.IntegerField()
    winner = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        outfit1 = cleaned_data.get("outfit1")
        outfit2 = cleaned_data.get("outfit2")
        winner = cleaned_data.get("winner")

        if outfit1 and not Outfit.objects.filter(pk=outfit1).exists():
            self.add_error("outfit1", ValidationError("Outfit doesn't exist.", code="invalid"))
        if outfit2 and not Outfit.objects.filter(pk=outfit2).exists():
            self.add_error("outfit2", ValidationError("Outfit doesn't exist.", code="invalid"))

        if winner and winner not in (outfit1, outfit2):
            self.add_error("winner", ValidationError("Winner must be either outfit1 or outfit2.", code="invalid"))

    def save(self):
        outfit1 = Outfit.objects.get(pk=self.cleaned_data["outfit1"])
        outfit2 = Outfit.objects.get(pk=self.cleaned_data["outfit2"])

        winner, loser = (outfit1, outfit2) if self.cleaned_data["winner"] == outfit1.pk else (outfit2, outfit1)

        winner.rating, loser.rating = calculate_elo(winner.rating, loser.rating)

        winner.save()
        loser.save()

def calculate_elo(winner_rating, loser_rating, k=40):
    """Return the Elo ratings of a winner and loser as a tuple."""
    R_1, R_2 = map(lambda x: 10 ** (x / 400), [winner_rating, loser_rating])
    E_1, E_2 = map(lambda x: x / (R_1 + R_2), [R_1, R_2])
    new_winner_rating = round(winner_rating + k * (1 - E_1))
    new_loser_rating = round(loser_rating - k * E_2)
    return new_winner_rating, new_loser_rating
