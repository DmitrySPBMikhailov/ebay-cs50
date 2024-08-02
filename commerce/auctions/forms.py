from django.forms import ModelForm
from .models import Listing


class ListingCreateForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "price", "description", "image", "category"]


class ListingUpdateForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "price", "description", "image", "category"]
