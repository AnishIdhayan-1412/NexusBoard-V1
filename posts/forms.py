from django import forms
from .models import Post, Comment
from communities.models import Community, Membership
from core.validators import validate_image

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'post_type', 'community', 'body', 'url', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'An interesting title...'}),
            'post_type': forms.Select(attrs={'class': 'form-select'}),
            'community': forms.Select(attrs={'class': 'form-select'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            validate_image(image)
        return image

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            joined_ids = Membership.objects.filter(user=user, is_active=True).values_list('community_id', flat=True)
            self.fields['community'].queryset = Community.objects.filter(id__in=joined_ids)
        else:
            self.fields['community'].queryset = Community.objects.all()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts...'
            })
        }
        labels = {'body': ''}
