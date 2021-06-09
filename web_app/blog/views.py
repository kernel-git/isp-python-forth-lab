import asyncio
import logging
from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .async_requests import *
from .models import Post

logger = logging.getLogger('django')


class BlogListView(ListView):
    paginate_by = 2
    model = Post
    template_name = 'home.html'

    queryset = asyncio.run(get_ordered_posts('-publication_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = asyncio.run(get_all_categories())
        return context
    #queryset = Book.objects.filter(publisher__name='Acme Publishing')


class CategoryPostList(ListView):
    paginate_by = 2
    template_name = 'posts_by_category.html'

    def get_queryset(self):
        coroutine = get_posts_by_category(self.kwargs['category'])
        return asyncio.run(coroutine)


class BlogDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'


class BlogCreateView(CreateView):
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'body', 'categories']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super(BlogCreateView, self).form_valid(form)


class BlogUpdateView(UpdateView):
    model = Post
    template_name = 'post_edit.html'
    fields = ['title', 'body', 'categories']

    def get_object(self, queryset=None):
        obj = super(BlogUpdateView, self).get_object(queryset)
        if obj.author != self.request.user:
            messages.error(self.request, "You can't edit this post")
            logger.error("Attempt to get an access to update function")
            raise Http404("You don't own this object")
        return obj


class BlogDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        obj = super(BlogDeleteView, self).get_object(queryset)
        if obj.author != self.request.user:
            messages.error(self.request, "You can't edit this post")
            logger.error("Attempt to get an access to delete function")
            raise Http404("You don't own this object")
        return obj


