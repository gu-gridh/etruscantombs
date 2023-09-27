from django import forms
from .models import Place, Image

from diana.abstract.models import get_fields, DEFAULT_FIELDS

class PlaceForm(forms.ModelForm):
    
    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS + ['id'])
        
    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['default_image'].queryset = Image.objects.filter(tomb=self.instance.id)
        
