from rest_framework import serializers

from .models import MediaContent, User


class MediaContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaContent
        fields = ('id', 'displayed_name', 'filepath', 'likes', 'likers')
        extra_kwargs = {'likers': {'required': False}}


class UserSerializer(serializers.ModelSerializer):
    liked_media_content = MediaContentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('external_id', 'name', 'is_moderator', 'liked_media_content')
        extra_kwargs = {'liked_media_content': {'required': False}}
