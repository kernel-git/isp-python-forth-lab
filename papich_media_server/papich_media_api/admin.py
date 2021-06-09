from django.contrib import admin
from .models import MediaContent


@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'displayed_name', 'filepath', 'likes')
