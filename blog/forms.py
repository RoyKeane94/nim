from django import forms
from .models import Post, Author, Book, NewsletterSubscriber, Tag, Guest


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'publish_date', 'author', 'book', 'series_order',
            'guests', 'tags',
            'points', 'commentary', 'is_draft',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post title'
            }),
            'publish_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control'
            }),
            'book': forms.Select(attrs={
                'class': 'form-control'
            }),
            'series_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Ch. or episode #'
            }),
            'guests': forms.CheckboxSelectMultiple(attrs={
                'class': 'checkbox-multi'
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'checkbox-multi'
            }),
            'commentary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Your personal commentary (markdown supported)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make points a JSON field handled separately in the view
        if 'points' in self.fields:
            del self.fields['points']
        # Optional: order guests and tags by name
        if 'guests' in self.fields:
            self.fields['guests'].queryset = Guest.objects.all().order_by('name')
            self.fields['guests'].required = False
        if 'tags' in self.fields:
            self.fields['tags'].queryset = Tag.objects.all().order_by('name')
            self.fields['tags'].required = False


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'newsletter-input',
                'placeholder': 'Enter your email',
                'type': 'email'
            })
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author name'
            })
        }


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Guest name'
            })
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag name'
            })
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'source_type', 'is_series', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book title'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Book description'
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_series': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

