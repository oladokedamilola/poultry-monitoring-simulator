# flock/models.py
from django.db import models
from django.contrib.auth.models import User

BREEDS = [
    ("broiler", "Broiler"),
    ("layer", "Layer"),
    ("kuroiler", "Kuroiler"),
    ("local", "Local Breed"),
]

AGE_GROUPS = [
    ("chick", "Chick"),
    ("grower", "Grower"),
    ("adult", "Adult"),
]

class FlockBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flock_blocks")
    name = models.CharField(max_length=100)
    number_of_birds = models.PositiveIntegerField(default=10)
    breed = models.CharField(max_length=20, choices=BREEDS)
    age_group = models.CharField(max_length=20, choices=AGE_GROUPS)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def get_display_info(self):
        """Debug method to get all display information"""
        return {
            'id': self.id,
            'name': self.name,
            'number_of_birds': self.number_of_birds,
            'breed': self.breed,
            'breed_display': self.get_breed_display(),
            'age_group': self.age_group,
            'age_group_display': self.get_age_group_display(),
            'description': self.description,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'user': self.user.username if self.user else None,
        }
