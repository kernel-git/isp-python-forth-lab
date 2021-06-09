from blog.models import Post, Category
from asgiref.sync import sync_to_async


@sync_to_async
def get_posts_by_category(category):
    return Post.objects.filter(categories__title=category)


@sync_to_async()
def get_all_categories():
    return Category.objects.all()


@sync_to_async()
def get_ordered_posts(criteria):
    return Post.objects.order_by(criteria)
