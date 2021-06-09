from django.shortcuts import redirect
from rest_framework import viewsets
from django.http import JsonResponse
from django.db.models import Count
from rest_framework.decorators import action

from .serializers import MediaContentSerializer, UserSerializer
from .models import MediaContent, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('name')
    serializer_class = UserSerializer


class MediaContentViewSet(viewsets.ModelViewSet):
    queryset = MediaContent.objects.annotate(likes_count=Count('likers')).order_by('-likes_count')
    serializer_class = MediaContentSerializer

    @action(methods=['delete'], detail=True)
    def remove_likers(self, request, pk):
        media_content = self.get_object()
        likers_to_remove = request.data['likers']
        for liker_data in likers_to_remove:
            liker = User.objects.get(external_id=int(liker_data['external_id']))
            media_content.likers.remove(liker)
        return redirect('mediacontent-detail', pk)
