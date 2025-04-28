from django import forms

class Query(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'searchBar'}))