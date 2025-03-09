from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    id = models.AutoField(primary_key=True)  # Not necessary, Django does this by default
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    published_date = models.DateField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_borrowed = models.BooleanField(default=False)
    borrowed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="borrowed_books")
    borrowed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}" 

    # def __str__(self):
    #     return self.title