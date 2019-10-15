from django import forms


class fileForm(forms.Form):
    selectedY = forms.CharField()
    selectedX = forms.CharField()