from django import forms
from .models import ImageModel

class ImageForm(forms.ModelForm):
    class Meta:
        model = ImageModel  
        fields = ['image']  

from .models import mold

class MoldForm(forms.ModelForm):
    class Meta:
        model = mold
        fields = ["name", "description", "image", "completed"]
