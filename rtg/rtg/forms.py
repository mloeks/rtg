
from django import forms


class RtgContactForm(forms.Form):
    author = forms.CharField(min_length=3, max_length=30)
    email = forms.EmailField(max_length=254)
    content = forms.CharField(min_length=3, max_length=4000)