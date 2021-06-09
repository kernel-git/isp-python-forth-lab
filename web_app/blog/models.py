from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category, related_name='topics')
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    body = models.TextField()
    publication_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


