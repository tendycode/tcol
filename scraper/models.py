
from django.db import models
import uuid
from django.utils import timezone

class Book(models.Model):
    GENRE_CHOICES = [
        ('Fiction', 'Fiction'),
        ('NonFiction', 'NonFiction'),
        ('Science', 'Science'),
        ('History', 'History'),
        ('Biograpy', 'Biograpy'),
    ]


    bookID = models.UUIDField(null=True, blank=True)
    isbn = models.CharField(max_length=50, null=True, blank=True)  # Not unique yet, nullable for now
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500, default='Unknown')
    summary = models.TextField(blank=True, null=True)
    totalCopies = models.IntegerField(default=0)
    availabeCopies = models.IntegerField(default=0)
    publicationdate = models.DateField(blank=True, null=True)
    CoveimageUrl = models.URLField(max_length=255, blank=True, null=True)
    Genre = models.CharField(max_length=500, choices=GENRE_CHOICES, default='Default')
    # Genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='Fiction')

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
    






