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
        

