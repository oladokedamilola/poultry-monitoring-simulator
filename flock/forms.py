from django import forms
from .models import FlockBlock

class BlockForm(forms.ModelForm):
    class Meta:
        model = FlockBlock
        fields = ["name", "number_of_birds", "breed", "age_group", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "number_of_birds": forms.NumberInput(attrs={"class": "form-control"}),
            "breed": forms.Select(attrs={"class": "form-control"}),
            "age_group": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        
    def clean_number_of_birds(self):
        number_of_birds = self.cleaned_data.get("number_of_birds")
        if number_of_birds <= 0:
            raise forms.ValidationError("Number of birds must be a positive integer.")
        return number_of_birds
    
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Name cannot be empty.")
        return name
    