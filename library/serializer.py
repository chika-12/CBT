from rest_framework import serializers
from . import models
from django import forms

class BookSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Books
        fields = "__all__"

class BookForm(forms.ModelForm):
    """Form for creating and updating Books."""
    
    class Meta:
        model = models.Books
        fields = '__all__' 
        


from django import forms
from .models import BookSuggestion

class BookSuggestionForm(forms.ModelForm):
    class Meta:
        model = BookSuggestion
        fields = ['title', 'author', 'isbn', 'publication_year', 
                  'genre', 'reason', 'source', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Author's full name"
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us why this book would be valuable...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional information...'
            }),
        }