from django import forms
from .models import Community


class CommunityCreateForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'is_private', 'rules', 'banner', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'community_name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rules': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'icon': forms.FileInput(attrs={'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
